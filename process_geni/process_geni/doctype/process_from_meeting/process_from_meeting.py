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
    # Load the model once for efficiency
    model = "gpt2"

    tokenizer = AutoTokenizer.from_pretrained(model)

    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        #torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto",
    )
    sequences = pipeline(
        text_inputs= "Here is a excerpt of a meeting transcript" + transcript_text + "Here is a list of action items to follow based on that transcript:",
        #text_inputs= "marco is a tall boy",

        max_length=200,
        do_sample=True,
        top_k=10,
        num_return_sequences=1,
        eos_token_id=tokenizer.eos_token_id,
    )

    return(sequences)

@frappe.whitelist()
def create_tasks_from_meeting(transcript_file, project_name):
    # Load the SentenceTransformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Construct the full path to the file
    base_path = frappe.utils.get_site_path("private", "files")
    full_path = os.path.join(base_path, os.path.basename(transcript_file))

    # Ensure the file exists
    if not os.path.exists(full_path):
        frappe.throw(f"File not found: {full_path}")

    # Read the file
    transcript_text = read_docx(full_path)


    # Get action definitions from the database
    action_definitions = frappe.get_all("Action Definition", fields=["action", "definition"])

    if not action_definitions:
        frappe.throw("No action definitions found.")

    # Extract actions and definitions
    actions = [action["action"] for action in action_definitions]
    definitions = [definition["definition"] for definition in action_definitions]

    # Generate embeddings for the definitions
    def_embeddings = model.encode(definitions, convert_to_tensor=True)

    # Store tasks to be created
    tasks = []

    # Compare each sentence to action definitions
    transcriptChunks = sent_tokenize(list(chunks(transcript_text, size=500)))
    
    for transcriptChunk in transcriptChunks:

        llmResponse = task_list_from_llm(transcriptChunk) # prompt + response
        sentences = sent_tokenize(llmResponse)
        sentences_embeddings = model.encode(sentences, convert_to_tensor=True)
        
        for sentence in sentences:
        
            sent_embedding = model.encode([sentence])
            
            similarities = cosine_similarity(sent_embedding, def_embeddings).flatten()
            max_similarity_idx = similarities.argmax()
            max_similarity = similarities[max_similarity_idx]
    
            if max_similarity > 0.7:  # Adjust threshold as needed
                action = actions[max_similarity_idx]
                task_description = sentence.strip()
                if action:  # Ensure there is a subject for the task
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
