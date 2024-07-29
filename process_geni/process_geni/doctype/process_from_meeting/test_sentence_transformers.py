from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
sentences = ["This is an example sentence", "Each sentence is converted"]

embeddings = model.encode(sentences)

print(embeddings)
