# process_from_meeting.py
import frappe
from frappe.model.document import Document
import os
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import numpy as np
import chardet


class ProcessFromMeeting(Document):
    pass

@frappe.whitelist()
def create_tasks_from_meeting(transcript_file, project_name):
    # Load the SentenceTransformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Construct the full path to the file
    base_path = frappe.utils.get_site_path("private", "files")
    full_path = os.path.join(base_path, os.path.basename(transcript_file))
    #file_path = frappe.get_site_path("private", "files", os.path.basename(transcript_file))

    # Ensure the file exists
    if not os.path.exists(full_path):
        frappe.throw(f"File not found: {fill_path}")

   # Detect the encoding of the file
    with open(full_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    
    # Read the file with the detected encoding
    with open(full_path, 'r', encoding=encoding) as file:
        transcript_text = file.read()
     
    # Processing logic: split into sentences
    sentences = sent_tokenize(transcript_text)

    # Get action definitions from the database
    action_definitions = frappe.get_all("Action Definition", fields=["action", "definition"])

    if not action_definitions:
        frappe.throw("No action definitions found.")

    # Extract actions and definitions
    actions = [action["action"] for action in action_definitions]
    definitions = [definition["definition"] for definition in action_definitions]

    # Generate embeddings for the definitions
    def_embeddings = model.encode(definitions)

    # Store tasks to be created
    tasks = []

    # Compare each sentence to action definitions
    for sentence in sentences:
        sent_embedding = model.encode([sentence])
        similarities = cosine_similarity(sent_embedding, def_embeddings).flatten()
        max_similarity_idx = similarities.argmax()
        max_similarity = similarities[max_similarity_idx]

        if max_similarity > 0.5:  # Adjust threshold as needed
            action = actions[max_similarity_idx]
            task_description = sentence.strip()
            tasks.append({
                "subject": action,
                "description": task_description,
                "project": project_name
            })

    # Create tasks in ERPNext
    for task in tasks:
        task_doc = frappe.get_doc({
            "doctype": "Task",
            "subject": task["subject"],
            "description": task["description"],
            "project": task["project"]
        })
        task_doc.insert()
        frappe.db.commit()

    return f"Created {len(tasks)} tasks for project {project_name}"
