import frappe
from frappe.model.document import Document

class ActionDefinition(Document):
    def before_save(self):
        # Add any server-side validation or processing here if needed
        pass
