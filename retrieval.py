import json 
import sqlite3
import numpy as np 
from foundry_local_sdk import Configuration, FoundryLocalManager

#initialize foundry local instance safely without re-initializing if active
config = Configuration(app_name = "rag_assistant")
try: 
    FoundryLocalManager.initialize(config)
except Exception:
    pass #Foundry Local is already initialized
manager = FoundryLocalManager.instance

#get embedding model instance for querying
model = manager.catalog.get_model("qwen3-embedding-0.6b")
print("Downloading embedding model...")
model.download()

print("Loading into memory...")
model.load()
embed_client = model.get_embedding_client()

#calculate the similarity angle between vector embeddings
def cosine_similarity(a,b):
    a,b = np.array(a), np.array(b)
    return np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_top_chunks(query, k=2):
    #convert each search question into embedding vector
    query_embedding = embed_client.generate_embedding(query).data[0].embedding

    #fetch all stored embeddings from the sqlite db
    conn = sqlite3.connect("knowledge.db")
    cursor= conn.cursor()
    cursor.execute("SELECT source, content, embedding FROM chunks")
    rows= cursor.fetchall()
    conn.close()

    #rank chunks based on cosine similarity score
    scored =[]
    for source, content, embedding_json in rows: 
        embedding = json.loads(embedding_json)
        score = cosine_similarity(query_embedding, embedding)
        scored.append((score,source,content))

    #sort matches by highest score first and return top k
    scored.sort(reverse=True, key=lambda x:x[0])
    return scored[:k]

if __name__=='__main__':
    #quick test execution to print top matches
    results = get_top_chunks("How many teeth do dogs have?")
    for score, source, content in results:
        print(f"[{score:.3f}] ({source}) {content[:80]}...")
        