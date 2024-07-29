import frappe
from frappe.model.document import Document
import os
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize

class ProcessFromMeeting(Document):
    def before_save(self):
        self.create_tasks_from_meeting(self.meeting_transcript,self.project_selector)
    
    def create_tasks_from_meeting(self, transcript_file, project_name):
        # Load spaCy model
        nlp = spacy.load('en_core_web_sm')

        # Construct the full path to the file
        file_path = frappe.get_site_path("private", "files", os.path.basename(transcript_file))

        # Ensure the file exists
        if not os.path.exists(file_path):
            frappe.throw(f"File not found: {file_path}")


        # Read the content of the file
        with open(file_path, 'r') as file:
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

        # Initialize TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english')

        # Create vectorized definitions
        def_vecs = vectorizer.fit_transform(definitions)

        # Store tasks to be created
        tasks = []

        # Compare each sentence to action definitions
        for sentence in sentences:
            sent_vec = vectorizer.transform([sentence])
            similarities = cosine_similarity(sent_vec, def_vecs).flatten()
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
