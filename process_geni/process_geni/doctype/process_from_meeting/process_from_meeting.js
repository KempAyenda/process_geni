// process_from_meeting.js
frappe.ui.form.on('Process From Meeting', {
    refresh: function(frm) {
        frm.add_custom_button(__('Create Tasks'), function() {
            frappe.call({
                method: 'process_geni.process_geni.doctype.process_from_meeting.process_from_meeting.create_tasks_from_meeting',
                args: {
                    transcript_file: frm.doc.meeting_transcript,
                    project_name: frm.doc.project_selector
                },
                callback: function(r) {
                    if (!r.exc) {
                        frappe.msgprint(__('Tasks created successfully'));
                    }
                }
            });
        });
    }
});
