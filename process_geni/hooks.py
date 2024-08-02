# process_geni/hooks.py

app_name = "process_geni"
app_title = "Process Geni"
app_publisher = "Ayenda Kemp"
app_description = "Process Geni"
app_email = "ayenda@eolaord.com"
app_license = ""

# Include JS, CSS files
# app_include_css = "/assets/process_geni/css/process_geni.css"
# app_include_js = "/assets/process_geni/js/process_geni.js"

# Doctype JS
doctype_js = {
    "Logeny Process Query": "process_geni/doctype/logeny_process_query/logeny_process_query.js",
    "Update Actions List": "process_geni/doctype/update_actions_list/update_actions_list.js",
    "Action Definition": "process_geni/doctype/action_definition/action_definition.js",
    "Bulk Update Actions List": "process_geni/doctype/bulk_update_actions_list/bulk_update_actions_list.js",
    "Process From Meeting": "process_geni/doctype/process_from_meeting/process_from_meeting.js"
#    "Google Drive Integration": "process_geni/doctype/google_drive_integration/google_drive_integration.js"
}
# Define the whitelist method for OAuth callback
#override_whitelisted_methods = {
#    "frappe.integrations.doctype.google_drive.google_drive.authorize_access": "process_geni.doctype.google_drive_integration.google_drive_integration.get_oauth_url"
#    "process_geni.doctype.google_drive_integration.google_drive_integration.google_drive_callback": "process_geni.doctype.google_drive_integration.google_drive_integration.google_drive_callback"
#}
