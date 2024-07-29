frappe.ui.form.on('Bulk Update Actions List', {
    refresh: function(frm) {
        frm.add_custom_button(__('Upload and Process'), function() {
            if (frm.doc.word_file) {
                frappe.call({
                    method: "process_geni.process_geni.doctype.bulk_update_actions_list.bulk_update_actions_list.upload_word_file",
                    args: {
                        word_file: frm.doc.word_file
                    },
                    callback: function(response) {
                        frappe.msgprint(__('File processed successfully.'));
                        frm.refresh_fields();
                    }
                });
            } else {
                frappe.msgprint(__('Please upload a Word document first.'));
            }
        });
    }
});
