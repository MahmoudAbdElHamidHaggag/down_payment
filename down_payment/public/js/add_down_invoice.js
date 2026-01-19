frappe.ui.form.on("Sales Invoice", {
    customer: frm => run_all(frm),
    custom_is_down_payment: frm => run_all(frm),
    custom_include_down_payment: frm => run_all(frm),

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
                    ['status', '!=', 'Completed'],
                    ['custom_down_payment_invoice_ref', 'in', ['', null]]
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
                    ['custom_down_payment_link_sales_order', 'in', ['', null]],
                ]
            };
        });
    },
    custom_reload(frm) {
        window.location.reload(true);
    }
});

function run_all(frm) {
    validate_down(frm);
    if (frm.doc.custom_is_down_payment) {
        add_item(frm);
        frm.set_df_property("custom_is_down_payment", "read_only", 1)
    }
}

function validate_down(frm) {
    let down = frm.doc.custom_is_down_payment;
    let includ = frm.doc.custom_include_down_payment;
    let cust = frm.doc.customer;

    if (!cust) {
        if (down) {
            frm.set_value("custom_is_down_payment", 0);
            frappe.msgprint("Please choose the customer first");
        }
        if (includ) {
            frm.set_value("custom_include_down_payment", 0);
            frappe.msgprint("Please choose the customer first");
        }
    }

    frm.set_df_property("custom_include_down_payment", "read_only", down && cust ? 1 : 0);
    frm.set_df_property("custom_is_down_payment", "read_only", includ && cust ? 1 : 0);
}


async function add_item(frm) {
    console.log("Checking conditions...", frm.doc.customer, frm.doc.custom_is_down_payment);
    let down = frm.doc.custom_is_down_payment;
    let cust = frm.doc.customer;
    let includ = frm.doc.custom_include_down_payment;
    if (!(cust && down && !includ)) return;
    if (frm.doc.items && frm.doc.items.length > 0) {
        frm.clear_table("items");
    };

    let settings = await frappe.db.get_value("Down Payment Setting", "Down Payment Setting", 
        ["down_payment_item", "tax_template", "cost_center", "company", "income_account", "uom", "item_name"]
    );
    
    if (!settings || !settings.message.down_payment_item) {
        frappe.msgprint(__("Down Payment Item not found in settings"));
        return;
    }

    let s = settings.message;

    
    frm.set_value("company", s.company);
    frm.set_value("cost_center", s.cost_center);
    frm.set_value("taxes_and_charges", s.tax_template);

    
    frm.clear_table("items");
    let row = frm.add_child("items");
    
    
    frappe.model.set_value(row.doctype, row.name, {
        "item_code": s.down_payment_item,
        "item_name": s.item_name,
        "income_account": s.income_account,
        "uom": s.uom,
        "qty": 1,
        "cost_center": s.cost_center
    });

    
    let grid = frm.fields_dict["items"].grid;
    
    grid.wrapper.find('.grid-add-row').hide(); 
    grid.cannot_add_rows = true;
    grid.cannot_delete_rows = true;
    
    grid.update_docfield_property("item_code", "read_only", 1);
    grid.update_docfield_property("uom", "read_only", 1);
    grid.update_docfield_property("qty", "read_only", 1);

    frm.refresh_field("items");
}





