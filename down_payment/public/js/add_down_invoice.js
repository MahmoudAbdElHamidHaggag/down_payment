frappe.ui.form.on("Sales Invoice", {
    custom_is_down_payment: frm => run_all(frm),
    custom_inclued_down_payment: frm => run_all(frm),
    customer: frm => run_all(frm),
    custom_down_payment_ref: frm => run_all(frm),
    custom_down_payment_link_sales_order: frm => run_all(frm),


    onload(frm) {
        run_all(frm);
        set_down_payment_filter(frm);
        set_sales_payment_filter(frm)
    },

    refresh(frm) {
        let cust = frm.doc.customer;
        let com = frm.doc.company;

        if (!cust) return;

        frm.set_query('custom_down_payment_link_sales_order', function () {
            return {
                filters:[
                    ['customer','=',cust],
                    ['company','=',com],
                    ['docstatus','=',1],
                ]
            };
        });
        frm.set_query('custom_down_payment_ref', function () {
            return {
                filters:[
                    ['customer','=',cust],
                    ["custom_is_down_payment",'=',1],
                    ['company','=',com],
                    ['docstatus','=',1],
                ]
            };
        });

    }
});

function run_all(frm) {
    console.log("RUN_ALL");
    validate_down(frm);
    add_item(frm);
    add_amount(frm);

}

function validate_down(frm) {
    let down = frm.doc.custom_is_down_payment;
    let includ = frm.doc.custom_inclued_down_payment;
    let cust = frm.doc.customer;

    if (!cust) {
        if (down) {
            frm.set_value("custom_is_down_payment", 0);
            frappe.msgprint("Please choose the customer first");
        }
        if (includ) {
            frm.set_value("custom_inclued_down_payment", 0);
            frappe.msgprint("Please choose the customer first");
        }
    }

    frm.set_df_property("custom_inclued_down_payment", "read_only", down && cust ? 1 : 0);
    frm.set_df_property("custom_is_down_payment", "read_only", includ && cust ? 1 : 0);

    if (!down) {
        frm.clear_table("items");
        frm.fields_dict["items"].grid.update_docfield_property("item_code", "read_only", 0);
        frm.fields_dict["items"].grid.update_docfield_property("uom", "read_only", 0);
        frm.fields_dict["items"].grid.update_docfield_property("qty", "read_only", 0);

        frm.fields_dict["items"].grid.cannot_add_rows = false;
        frm.fields_dict["items"].grid.cannot_delete_rows = false;

        frm.refresh_field("items");
    }
}





async function add_item(frm) {
    let down = frm.doc.custom_is_down_payment;
    let cust = frm.doc.customer;
    let includ = frm.doc.custom_inclued_down_payment;

    if (!(down && cust && !includ)) return;

    // لا تعيد البناء لو فيه items بالفعل
    if (frm.doc.items && frm.doc.items.length > 0) return;

    let item_code = await frappe.db.get_single_value("Down Payment Setting", "down_payment_item");
    let tax = await frappe.db.get_single_value("Down Payment Setting", "tax_template");
    let cost = await frappe.db.get_single_value("Down Payment Setting", "cost_center");
    let company = await frappe.db.get_single_value("Down Payment Setting", "company");
    let income = await frappe.db.get_single_value("Down Payment Setting", "income_account");
    let uom = await frappe.db.get_single_value("Down Payment Setting", "uom");
    let name = await frappe.db.get_single_value("Down Payment Setting", "item_name");

    if (!item_code) {
        frappe.msgprint("Down Payment Item not found");
        return;
    }

    frm.set_value("company", company);
    frm.set_value("cost_center", cost);
    frm.set_value("taxes_and_charges", tax);

    frm.clear_table("items");
    let row = frm.add_child("items");
    row.item_code = item_code;
    row.income_account = income;
    row.uom = uom;
    row.item_name = name;
    row.qty = 1;

    frm.fields_dict["items"].grid.update_docfield_property("item_code", "read_only", 1);
    frm.fields_dict["items"].grid.update_docfield_property("uom", "read_only", 1);
    frm.fields_dict["items"].grid.update_docfield_property("qty", "read_only", 1);

    frm.fields_dict["items"].grid.cannot_add_rows = true;
    frm.fields_dict["items"].grid.cannot_delete_rows = true;

    frm.refresh_field("items");
}

function set_sales_payment_filter(frm) {
    let cust = frm.doc.customer;
    let com = frm.doc.company;

    if (!cust) return;

    frm.set_query('custom_down_payment_link_sales_order', function () {
        return {
            filters:[
                ['customer','=',cust],
                ['company','=',com],
                ['docstatus','=',1],
            ]
        };
    });
}




async function add_amount(frm) {

    let cust = frm.doc.customer;
    let includ = frm.doc.custom_inclued_down_payment;
    let name_sa = frm.doc.custom_down_payment_ref;

    if (!cust || !includ || !name_sa) return;

    // لو فيه خصم بالفعل → لا تعمل override
    if (frm.doc.discount_amount > 0) return;

    let tax = await frappe.db.get_value(
        "Sales Taxes and Charges Template",
        { is_default: 1, disabled: 0, company: frm.doc.company },
        "name"
    );

    let sa = await frappe.db.get_doc("Sales Invoice", name_sa);
    let amount = sa.grand_total;

    frm.set_value("taxes_and_charges", tax.message.name);
    frm.set_value("apply_discount_on", "Net Total");
    frm.set_value("discount_amount", amount);

    // رسالة لمرة واحدة فقط
    if (!frm._dp_message_shown) {
        frappe.msgprint(`Down Payment Amount of ${amount} added as Discount!`);
        frm._dp_message_shown = true;
    }
}






