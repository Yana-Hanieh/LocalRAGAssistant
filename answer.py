from foundry_local_sdk import Configuration, FoundryLocalManager
from retrieval import get_top_chunks

#we didnt create a config or initialize the foundrylocal since we already did it previously in the retrieval.py
manager = FoundryLocalManager.instance

chat_model = manager.catalog.get_model("qwen2.5-0.5b")
print("Downloading chat model...")
chat_model.download()

print("Loading into memory...")
chat_model.load()
chat_client = chat_model.get_chat_client()

def answer_query(question):
    top_chunks = get_top_chunks(question, k=2)
    
    #do not ask the model if the match is weak or the answer doesnt exist in the knowledge base
    if not top_chunks or top_chunks[0][0] < 0.5:
        return "I dont have that information currently"

    context = '\n\n'.join(content for score, source, content in top_chunks)

    system_prompt = (
        "You are an intelligent assitant that answers user's questions according to the context given"
        "below ONLY. You must NEVER use any outside knowledge, even if you know the answer. If the answer is NOT found in the content"
        " DO NOT make any information up, regardless if that information is true or not!"
        "just reply with 'That information is not provided by your document'"
        " If multiple numbers appear, pick the one that matches the subject of the question only \n\n"  
    )

    user_prompt =(
        f"Context:\n{context}\n\n"
        f"Question:{question}\n\n"
        "Answer using ONLY the context above. If it's not there, say "
        "'I don't have that information currently.'"
    )

    messages =[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content":user_prompt}
    ]

    response = chat_client.complete_chat(messages)
    return response.choices[0].message.content

if __name__=="__main__":
    print(answer_query("How many teeth do dogs have?"))
    print()
    print(answer_query("How many planets are in our solar system"))