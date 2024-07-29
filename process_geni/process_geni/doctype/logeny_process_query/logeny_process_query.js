
// For license information, please see license.txt
// Copyright (c) 2024, Ayenda Kemp and contributors
// For license information, please see license.txt

frappe.ui.form.on('LogenyProcessQuery', {
    onload: function(frm) {
        frm.set_query('doctype_selector', function() {
            return {
                query: 'process_geni.process_geni.doctype.logeny_process_query.logeny_process_query.get_all_doctypes'
            };
        });
    },
    refresh: function(frm) {
        frm.add_custom_button(__('Run Process Mining'), function() {
            const data = {
                doctype: frm.doc.doctype_selector,
                activity_key: frm.doc.activity_key,
                from_date: frm.doc.from_date,
                to_date: frm.doc.to_date
            };

            frappe.call({
                method: 'process_geni.process_geni.doctype.logeny_process_query.logeny_process_query.run_process_mining',
                args: { data: JSON.stringify(data) },
                callback: function(r) {
                    if (r.message) {
                        const process_statistics = r.message.statistics;
                        const petri_net_url = r.message.petri_net_url;

                        if (petri_net_url) {
                            frm.dashboard.add_section('<div><img src="' + petri_net_url + '" alt="Petri Net"></div>');
                        }
                    }
                }
            });
        });
    },
    doctype_selector: function(frm) {
        if (frm.doc.doctype_selector) {
            frappe.model.with_doctype(frm.doc.doctype_selector, function() {
                let meta = frappe.get_meta(frm.doc.doctype_selector);
                let fields = meta.fields.filter(df => ["Data", "Select", "Link"].includes(df.fieldtype));
                frm.set_df_property('activity_key', 'options', fields.map(df => df.fieldname));
            });
        }
    }
});
