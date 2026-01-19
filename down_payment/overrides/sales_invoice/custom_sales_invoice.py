import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import flt
import json

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  
        self.apply_down_payment_logic()

    def apply_down_payment_logic(self):
        if not getattr(self, "custom_include_down_payment", 0):
            return

        down_payment_total = flt(self.custom_down_payment_amount or 0)
        down_payment_net = flt(self.custom_down_payment_amount_befor_tax or 0)

        if down_payment_total <= 0:
            frappe.throw("The down payment must not equal 0 or minus")


        if down_payment_total > (flt(self.net_total) + flt(self.total_taxes_and_charges)):
            frappe.throw("The down payment must be less than the invoice grand total.")

        if self.custom_include_down_payment and self.apply_discount_on == "Grand Total":
            frappe.throw ("The discount should be applied to the Net Total and not the Grand Total, as long as this invoice includes the down payment.")

        for tax in self.get("taxes"):
            current_taxable = flt(tax.get("taxable_amount") or self.net_total)
            new_taxable = current_taxable - down_payment_net
            tax.taxable_amount = new_taxable
            
            tax_rate = flt(tax.get("rate") or 0)
            
            if tax.charge_type == "On Net Total" and tax_rate:
                new_tax_amount = flt(new_taxable * tax_rate / 100.0)
                
                tax.tax_amount = new_tax_amount
                tax.tax_amount_after_discount_amount = new_tax_amount
                
                conversion_rate = flt(self.conversion_rate or 1)
                tax.base_tax_amount = new_tax_amount * conversion_rate
                tax.base_tax_amount_after_discount_amount = tax.base_tax_amount

             
                if tax.item_wise_tax_detail:
                    try:
                        detail = json.loads(tax.item_wise_tax_detail)
                        for item_code in detail:
                            ratio = new_tax_amount / flt(tax.get("tax_amount") or 1) if tax.get("tax_amount") else 1
                            detail[item_code][1] = flt(detail[item_code][1]) * ratio
                        tax.item_wise_tax_detail = json.dumps(detail)
                    except:
                        pass

        self.recalculate_final_totals(down_payment_net)

    def recalculate_final_totals(self, down_payment_amount):
        new_total_taxes = sum(flt(d.tax_amount) for d in self.get("taxes"))
        self.total_taxes_and_charges = new_total_taxes
        self.base_total_taxes_and_charges = flt(new_total_taxes) * flt(self.conversion_rate or 1)
        current_cumulative_total = flt(self.net_total) - flt(down_payment_amount)
        for t in self.get("taxes"):
            current_cumulative_total += flt(t.tax_amount)
            t.total = current_cumulative_total

      
        if self.apply_discount_on == "Net Total":
            self.net_total = (flt(self.net_total) - flt(down_payment_amount))
            self.base_net_total = flt(self.net_total) * flt(self.conversion_rate or 1)
            self.grand_total = (flt(self.net_total) + flt(new_total_taxes))
            self.base_grand_total = flt(self.grand_total) * flt(self.conversion_rate or 1)
        else:
            self.grand_total = (flt(self.net_total) + flt(new_total_taxes) - flt(down_payment_amount) )
            self.base_grand_total = flt(self.grand_total) * flt(self.conversion_rate or 1)
        
        precision = self.precision("grand_total") or 2
        self.rounded_total = round(self.grand_total, precision)
        self.base_rounded_total = round(self.base_grand_total, precision)
        self.outstanding_amount = self.rounded_total

    def get_gl_entries(self, warehouse_account=None):
        gl_entries = super(CustomSalesInvoice, self).get_gl_entries(warehouse_account)
        if not getattr(self, "custom_include_down_payment", 0):
            return gl_entries
        total_debit = sum(flt(e.get("debit", 0)) for e in gl_entries)
        total_credit = sum(flt(e.get("credit", 0)) for e in gl_entries)
        difference = flt(total_credit - total_debit, self.precision("grand_total"))
        if abs(difference) > 0.01:
            clearing_account = frappe.db.get_single_value("Down Payment Setting", "income_account")
            if not clearing_account:
                frappe.throw("برجاء تحديد حساب الدفعة المقدمة في إعدادات Down Payment Setting")
            gl_entries.append(
                self.get_gl_dict({
                    "account": clearing_account,
                    "party_type": "Customer",
                    "party": self.customer,
                    "debit": difference if difference > 0 else 0,
                    "credit": -difference if difference < 0 else 0,
                    "against": self.customer,
                    "cost_center": self.cost_center,
                    "remarks": f"Down Payment Adjustment: {self.name}"
                }, item=self)
            )

        return gl_entries