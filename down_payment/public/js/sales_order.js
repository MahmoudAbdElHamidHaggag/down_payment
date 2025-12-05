frappe.ui.form.on("Sales Order", {
    refresh(frm) {
        if (!frm.doc.docstatus) return;

        frm.add_custom_button("Create Down Payment Invoice", async () => {
            let d = new frappe.ui.Dialog({
                title: "Create Down Payment",
                fields: [
                    {
                        fieldname: "type",
                        label: "Down Payment Method",
                        fieldtype: "Select",
                        options: ["Percentage", "Fixed Amount"],
                        reqd: 1
                    },
                    {
                        fieldname: "percentage",
                        label: "Percentage (%)",
                        fieldtype: "Float",
                        depends_on: "eval:doc.type=='Percentage'",
                    },
                    {
                        fieldname: "amount",
                        label: "Amount (SAR)",
                        fieldtype: "Float",
                        depends_on: "eval:doc.type=='Fixed Amount'"
                    }
                ],
                primary_action_label: "Create",
                primary_action: async (values) => {

                    const order_total = frm.doc.grand_total;

                    let dp_amount = 0;

                    if (values.type === "Percentage") {
                        dp_amount = (order_total * values.percentage) / 100;
                    } else {
                        dp_amount = values.amount;
                    }

                    // تحقق
                    if (dp_amount <= 0) {
                        frappe.msgprint("Down Payment must be greater than zero.");
                        return;
                    }
                    if (dp_amount > order_total) {
                        frappe.msgprint("Down Payment cannot exceed total order value.");
                        return;
                    }

                    d.hide();

                    frappe.call({
                        method: "down_payment.api.create_sales_invoice_on_sales_order",
                        args: {
                            docname: frm.doc.name,
                            amount: dp_amount
                        },
                        freeze: true,
                        freeze_message: "Creating Down Payment Invoice...",
                        callback(r) {
                            frappe.show_alert("Down Payment Invoice Created");
                            frappe.set_route("Form", "Sales Invoice", r.message);
                        }
                    });
                }
            });

            d.show();
        });
    }
});
