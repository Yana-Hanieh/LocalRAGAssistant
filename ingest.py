import os 
import json 
import sqlite3
from foundry_local_sdk import Configuration, FoundryLocalManager

#setup foundry local manager configuration
config = Configuration(app_name='rag_assistant')
FoundryLocalManager.initialize(config)
manager = FoundryLocalManager.instance 

#load the embedding model from catalog
model = manager.catalog.get_model("qwen3-embedding-0.6b")

print("Downloading embedding model")
model.download()

print("Loading into memory...")
model.load()
embed_client = model.get_embedding_client()

#connect to the database 
conn = sqlite3.connect("knowledge.db")
cursor = conn.cursor()

#reading every document (in docs) and divide them into chunks
docs_folder = "docs"

for filename in os.listdir(docs_folder): #get every filename inside docs/
    filepath = os.path.join(docs_folder, filename) #read the content of each file
    with open(filepath,'r',encoding='utf-8') as f: #for every chunk of data, generate an embedding equivalent
        text=f.read()

    #split documen by paragraphs and clean whitespace
    chunks = [p.strip() for p in text.split('\n\n') if p.strip()]
    print(f'{filename}: {len(chunks)} chunk(s) found')

    #embed each text chunk and store it into SQLite DB
    for chunk_text in chunks:
        response = embed_client.generate_embedding(chunk_text)
        embedding_vector = response.data[0].embedding

        cursor.execute(
            "INSERT INTO chunks(source, content, embedding) VALUES (?,?,?)",
            (filename, chunk_text, json.dumps(embedding_vector))
        )
        print(f'Inserted chunk: {chunk_text[:50]}...')

#save all the embeddings of the document
conn.commit() 
conn.close()
print('\n Ingestion complete')