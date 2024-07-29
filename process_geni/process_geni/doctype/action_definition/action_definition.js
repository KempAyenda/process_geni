frappe.ui.form.on('Action Definition', {
    refresh: function(frm) {
        frm.set_df_property('action', 'read_only', frm.doc.__islocal ? 0 : 1);
        frm.set_df_property('definition', 'read_only', frm.doc.__islocal ? 0 : 1);
    },
    before_save: function(frm) {
        // Add any client-side validation or processing here if needed
    }
});
