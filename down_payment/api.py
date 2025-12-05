import frappe
from frappe.utils import nowdate, flt

@frappe.whitelist()
def create_sales_invoice_on_sales_order(docname, amount):

    order = frappe.get_doc("Sales Order", docname)
    amount = flt(amount)

    # ===== Prevent creating more than 1 Down Payment =====
    existing_si = getattr(order, "custom_down_payment_invoice_ref", None)

    if existing_si:
        si_doc = frappe.get_doc("Sales Invoice", existing_si)

        # لو الفاتورة السابقة ما زالت Submitted → ممنوع تعمل تاني
        if si_doc.docstatus == 1:
            frappe.throw(f"""
                A Down Payment Invoice already exists for this Sales Order:
                <b>{existing_si}</b><br><br>
                You cannot create another one.
            """)
        elif si_doc.docstatus == 0:
            frappe.throw(f"""
                A Down Payment Invoice <b>{existing_si}</b> is still Draft.
                Please Submit or Cancel it before creating a new one.
            """)

        # لو الفاتورة Cancelled أو Return → يسمح بإنشاء واحدة جديدة
        elif si_doc.docstatus == 2 or getattr(si_doc, "is_return", 0):
            order.db_set("custom_down_payment_invoice_ref", None)

    # ===== Validation =====
    if amount <= 0:
        frappe.throw("Down Payment amount must be greater than zero.")

    if amount > flt(order.grand_total):
        frappe.throw("Down Payment cannot exceed the Sales Order total amount.")

    # ===== Settings =====
    settings = frappe.get_single("Down Payment Setting")

    company = order.company or getattr(settings, "company", None)
    if not company:
        frappe.throw("Company is missing in Sales Order or Down Payment Settings")

    # Cost center logic
    cost_center = (
        getattr(order, "cost_center", None)
        or getattr(settings, "cost_center", None)
        or frappe.db.get_value("Company", company, "cost_center")
    )

    service_item = getattr(settings, "down_payment_item", None)
    if not service_item:
        frappe.throw("Service Item is missing in Down Payment Settings")

    dp_uom = getattr(settings, "uom", None)

    taxes_template = getattr(settings, "tax_template", None)

    income_acc = getattr(settings, "income_account", None)
    if not income_acc:
        frappe.throw("Income Account must be set in Down Payment Settings")

    # ===== Create Sales Invoice =====
    si = frappe.new_doc("Sales Invoice")
    si.customer = order.customer
    si.company = company
    si.posting_date = nowdate()
    si.custom_is_down_payment = 1
    si.custom_down_payment_link_sales_order = order.name

    si.ignore_pricing_rule = 1
    si.apply_discount_on = "Net Total"

    if taxes_template:
        si.taxes_and_charges = taxes_template

    si.set_missing_values()

    # Add Item Line
    si.append("items", {
        "item_code": service_item,
        "qty": 1,
        "uom": dp_uom,
        "rate": amount,
        "description": f"Down Payment for Sales Order {order.name}",
    })

    si.calculate_taxes_and_totals()
    si.insert()
    si.submit()

    # ===== Link Invoice Back to Sales Order =====
    order.db_set("custom_down_payment_invoice_ref", si.name)
    order.db_set("status", "Partially Invoiced")

    return si.name

########################################################################################################

def unlink_down_payment_on_cancel(doc, method):

    if not getattr(doc, "custom_is_down_payment", 0):
        return  # مش فاتورة داون → تجاهل

    so = getattr(doc, "custom_down_payment_link_sales_order", None)
    if not so:
        return  # مفيش ربط أساسًا → تجاهل

    # تحميل السيلز أوردر
    try:
        order = frappe.get_doc("Sales Order", so)
    except frappe.DoesNotExistError:
        return

    # إزالة قيمة الربط فقط
    order.db_set("custom_down_payment_invoice_ref", None)
    order.db_set("status", "Uninvoiced")

    frappe.msgprint(
        f"The Down Payment Invoice <b>{doc.name}</b> was cancelled.<br>"
        f"The link to Sales Order <b>{so}</b> has been removed.",
        indicator="orange"
    )

########################################################################################################

def unlink_on_return(doc, method):
    # نتحقق أنها فاتورة مرتجع
    if not getattr(doc, "is_return", 0):
        return

    # نجيب الفاتورة الأصلية
    original = doc.return_against
    if not original:
        return

    # نشوف هل الفاتورة الأصلية كانت Down Payment
    try:
        si = frappe.get_doc("Sales Invoice", original)
    except:
        return

    if not getattr(si, "custom_is_down_payment", 0):
        return

    # نشوف السيلز أوردر المرتبط
    so = getattr(si, "custom_down_payment_link_sales_order", None)
    if not so:
        return

    # حذف الربط
    try:
        order = frappe.get_doc("Sales Order", so)
        order.db_set("custom_down_payment_invoice_ref", None)
        order.db_set("status", "Uninvoiced")
    except:
        return

    frappe.msgprint(
        f"Return Invoice <b>{doc.name}</b> detected.<br>"
        f"Down Payment Invoice <b>{original}</b> link removed from Sales Order <b>{so}</b>.",
        indicator="orange"
    )

#######################################################################################################


import frappe

BILLING_FIELD = "custom_down_payment_invoice_ref"


def _set_if_exists(doctype: str, name: str, field: str, value):
    if frappe.get_meta(doctype).has_field(field):
        frappe.db.set_value(doctype, name, field, value, update_modified=False)


def _update_sales_order_for_invoice(si_name: str, clear_link: bool, batch_status: str | None = None):
    if not si_name:
        return
    batch_names = frappe.get_all("Sales Order", filters={BILLING_FIELD: si_name}, pluck="name")
    for b in batch_names:
        data = {}
        if clear_link and frappe.get_meta("Sales Order").has_field(BILLING_FIELD):
            data[BILLING_FIELD] = None
        if batch_status and frappe.get_meta("Sales Order").has_field("status"):
            data["status"] = batch_status
        if data:
            frappe.db.set_value("Sales Order", b, data, update_modified=False)

def on_si_submit(doc, method=None):
    if getattr(doc, "is_return", 0):
        target = doc.get("return_against")
        _update_sales_order_for_invoice(target, clear_link=True, batch_status="Uninvoiced")
    else:
        _update_sales_order_for_invoice(doc.name, clear_link=False, batch_status="Invoiced")

def on_si_cancel(doc, method=None):
    _update_sales_order_for_invoice(doc.name, clear_link=True, batch_status="Uninvoiced")


########################################################################################################

@frappe.whitelist()
def create_sales_invoice_on_payment(docname, amount):

    order = frappe.get_doc("Sales Order", docname)
    amount = flt(amount)

    # ===== Prevent creating more than 1 Down Payment =====
    existing_si = getattr(order, "custom_down_payment_invoice_ref", None)

    if existing_si:
        si_doc = frappe.get_doc("Sales Invoice", existing_si)

        # لو الفاتورة السابقة ما زالت Submitted → ممنوع تعمل تاني
        if si_doc.docstatus == 1:
            frappe.throw(f"""
                A Down Payment Invoice already exists for this Sales Order:
                <b>{existing_si}</b><br><br>
                You cannot create another one.
            """)
        elif si_doc.docstatus == 0:
            frappe.throw(f"""
                A Down Payment Invoice <b>{existing_si}</b> is still Draft.
                Please Submit or Cancel it before creating a new one.
            """)

        # لو الفاتورة Cancelled أو Return → يسمح بإنشاء واحدة جديدة
        elif si_doc.docstatus == 2 or getattr(si_doc, "is_return", 0):
            order.db_set("custom_down_payment_invoice_ref", None)

    # ===== Validation =====
    if amount <= 0:
        frappe.throw("Down Payment amount must be greater than zero.")

    if amount > flt(order.grand_total):
        frappe.throw("Down Payment cannot exceed the Sales Order total amount.")

    # ===== Settings =====
    settings = frappe.get_single("Down Payment Setting")

    company = order.company or getattr(settings, "company", None)
    if not company:
        frappe.throw("Company is missing in Sales Order or Down Payment Settings")

    # Cost center logic
    cost_center = (
        getattr(order, "cost_center", None)
        or getattr(settings, "cost_center", None)
        or frappe.db.get_value("Company", company, "cost_center")
    )

    service_item = getattr(settings, "down_payment_item", None)
    if not service_item:
        frappe.throw("Service Item is missing in Down Payment Settings")

    dp_uom = getattr(settings, "uom", None)

    taxes_template = getattr(settings, "tax_template", None)

    income_acc = getattr(settings, "income_account", None)
    if not income_acc:
        frappe.throw("Income Account must be set in Down Payment Settings")

    # ===== Create Sales Invoice =====
    si = frappe.new_doc("Sales Invoice")
    si.customer = order.customer
    si.company = company
    si.posting_date = nowdate()
    si.custom_is_down_payment = 1
    si.customdown_payment_link_sales_order = order.name

    si.ignore_pricing_rule = 1
    si.apply_discount_on = "Net Total"

    if taxes_template:
        si.taxes_and_charges = taxes_template

    si.set_missing_values()

    # Add Item Line
    si.append("items", {
        "item_code": service_item,
        "qty": 1,
        "uom": dp_uom,
        "rate": amount,
        "description": f"Down Payment for Sales Order {order.name}",
    })

    si.calculate_taxes_and_totals()
    si.insert()
    si.submit()

    # ===== Link Invoice Back to Sales Order =====
    order.db_set("custom_down_payment_invoice_ref", si.name)
    order.db_set("status", "Partially Invoiced")

    return si.name

