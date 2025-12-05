// Copyright (c) 2025, Mahmoud Abd El Hamied Omr Haggag and contributors
// For license information, please see license.txt

frappe.ui.form.on("Down Payment Setting", {
	onload: function(frm) {
        let com = frm.doc.company;
        if (com) {
            frappe.db.get_value("Company", com, "cost_center")
                .then(r => {
                    let cost = r.message.cost_center;
                    frm.set_value("cost_center", cost);
                });
        }
        frm.set_query('down_payment_item', function () {
            return {
                filters:[
                    ['is_stock_item','=',0],
                    ['is_fixed_asset','=',0],
                    ['has_variants','=',0],
                    ['disabled','=',0],
                    ['allow_alternative_item','=',0]
                ]
            }
        })
        frm.set_value('company',com )
        frm.set_query('cost_center', function() {
            return {
                filters:[
                    ['company','=',com],
                    ['is_group','=',0]
                    ['disabled','=',0]
                ]
            }
        })
        frm.set_query('tax_template', function() {
            return{
                filters:[
                    ['company','=',com ],
                    ["Sales Taxes and Charges", "included_in_print_rate", "=", 1],
                    ['disabled','=',0]
                ]
            }
        })
        frm.set_query('income_account',function(){
            return {
                filters:[
                    ['root_type','=','Income'],
                    ['company','=',com],
                    ['is_group','=',0],
                    ['disabled','=',0]
                ]
            }
        })

	},
});







