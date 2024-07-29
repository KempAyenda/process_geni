

# Copyright (c) 2024, Ayenda Kemp and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
import os

class ProcessFromMeeting(Document):
	pass

@frappe.whitelist()
def create_tasks_from_meeting(transcript_file, project_name):
    # Construct the full path to the file
    file_path = frappe.get_site_path("private", "files", os.path.basename(transcript_file))

    # Ensure the file exists
    if not os.path.exists(file_path):
        frappe.throw(f"File not found: {file_path}")

    # Read the content of the file
    with open(file_path, 'r') as file:
        transcript_text = file.read()

    # Processing logic: split into sentences and take the first 5 as tasks
    sentences = transcript_text.split('.')
    tasks = sentences[:5]

    for task in tasks:
        if task.strip():  # Ensure the task is not empty
            truncated_task = task.strip()[:100]  # Truncate task to 140 characters
            doc = frappe.get_doc({
                "doctype": "Task",
                "subject": truncated_task,
                "project": project_name
            })
            doc.insert()
            frappe.db.commit()

    return f"Created {len(tasks)} tasks for project {project_name}"
