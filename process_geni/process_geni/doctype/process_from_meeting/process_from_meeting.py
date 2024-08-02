import frappe
from frappe.model.document import Document
import os
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
import numpy as np
import chardet
import docx

from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch

class ProcessFromMeeting(Document):
    pass

@frappe.whitelist()
def read_docx(file_path):
    """Read the content of a .docx file and return as a string."""
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def chunks(text, size):
    """Yield successive size chunks from text."""
    for i in range(0, len(text), size):
        yield text[i:i + size]

def task_list_from_llm(transcript_text):
    """Generates a list of tasks from transcript text using a language model."""
    model = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model)
    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map="auto",
    )
    sequences = pipeline(
        text_inputs="Here is an excerpt of a meeting transcript: " + transcript_text + " Here is a list of action items to follow based on that transcript:",
        max_length=200,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )


    #if sequences:
    #    generated_text = sequences[0].get('generated_text', '')
    #else:
    #    generated_text = ''

    return sequences[0]

@frappe.whitelist()
def create_tasks_from_meeting(transcript_file, project_name):
    """Creates tasks in ERPNext from a meeting transcript file."""
    model = SentenceTransformer('all-MiniLM-L6-v2')

    base_path = frappe.utils.get_site_path("private", "files")
    full_path = os.path.join(base_path, os.path.basename(transcript_file))

    if not os.path.exists(full_path):
        frappe.throw(f"File not found: {full_path}")

    transcript_text = read_docx(full_path)

    action_definitions = frappe.get_all("Action Definition", fields=["action", "definition"])
    if not action_definitions:
        frappe.throw("No action definitions found.")

    actions = [action["action"] for action in action_definitions]
    definitions = [definition["definition"] for definition in action_definitions]

    def_embeddings = model.encode(definitions, convert_to_tensor=True)

    tasks = []
    transcriptChunks = chunks(transcript_text, size=500)

    for transcriptChunk in transcriptChunks:
        llmResponse = task_list_from_llm(transcriptChunk[0])
        if llmResponse:
            sentences = sent_tokenize(llmResponse)
            sentences_embeddings = model.encode(sentences, convert_to_tensor=True)

            for sentence in sentences:
                sent_embedding = model.encode([sentence])
                similarities = cosine_similarity(sent_embedding, def_embeddings).flatten()
                max_similarity_idx = similarities.argmax()
                max_similarity = similarities[max_similarity_idx]

                if max_similarity > 0.7:
                    action = actions[max_similarity_idx]
                    task_description = sentence.strip()
                    if action:
                        tasks.append({
                            "subject": action,
                            "description": task_description,
                            "project": project_name
                        })

            task.append({
		"subject": "test",
		"description": llmResponse,
		"projec": project_name
		})		

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

