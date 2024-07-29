import frappe
from frappe.model.document import Document
from docx import Document as DocxDocument
import os

class BulkUpdateActionsList(Document):
    pass

@frappe.whitelist()
def upload_word_file(word_file):
    file_path = frappe.get_site_path("private", "files", os.path.basename(word_file))
    
    # Ensure the file exists
    if not os.path.exists(file_path):
        frappe.throw(f"File not found: {file_path}")

    # Read the content of the file and process it
    table_data = table_from_docx_to_dict(file_path)
    
    # Save the action definitions to the database
    for action, definition in table_data.items():
        doc = frappe.get_doc({
            "doctype": "Action Definition",
            "action": action.strip(),
            "definition": definition.strip()
        })
        doc.insert()
    
    frappe.msgprint(f"Uploaded and processed file: {os.path.basename(word_file)}")

def table_from_docx_to_dict(document_path):
    doc = DocxDocument(document_path)
    tables = doc.tables
    if not tables:
        frappe.throw("No tables found in the document.")
    
    table = tables[0]
    table_data = {}
    for i in range(1, len(table.rows)):  # start from 1 to skip header row
        row = table.rows[i]
        key = row.cells[0].text
        value = row.cells[1].text
        table_data[key] = value
    
    return table_data
