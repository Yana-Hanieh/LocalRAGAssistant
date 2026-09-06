# Offline Local RAG Assistant

A local Q&A assistant that answers questions using only the content
of a local document. It doesn't use any internet connection once it's set up. 
It was built for the Microsoft Foundry Local summer program, using Foundry Local for
on-device model inference and the RAG (Retrieval-Augmented Generation)
pattern.
It currently answers questions about dog facts, since it's the only document available. 
But you can add any document that discusses any topic, and it would answer based on that file.

## Purpose

The main point of RAG is to stop the model from making things up. A plain LLM
with no context will confidently answer *any* question, correct or not. I tested 
it by making up a completely wrong definition of what RAG is, and it made up a definition.
This project fixes that by only letting the model answer from real text it's been given,
and having it say "I don't have that information currently" when the answer isn't included in the document.

Everything runs locally, so no cloud account, no API key, and no internet
dependency once the models are downloaded.

## How It Works

```
[ docs/*.md ] → [ Split into chunks ] → [ Embed with Foundry Local ] → [ Store in SQLite ]
                                                                              ↓
[ User Question ] → [ Embed Question ] → [ Cosine Similarity Search ] → [ Answer via Chat Model ]
```

1. **`create_db.py`**: creates `knowledge.db`, a SQLite file with one table
   (`chunks`) to hold every chunk of text plus its embedding.
2. **`ingest.py`**: reads every file in `docs/`, splits it into paragraph
   chunks, generates an embedding for each chunk using Foundry Local's
   `qwen3-embedding-0.6b` model, and inserts everything into `knowledge.db`.
3. **`retrieval.py`**: takes a question, embeds it the same way ingest embeds
   the doc info, pulls every stored chunk back out of the database, and scores
   each one against the question using cosine similarity and then returns the top matches.
5. **`answer.py`**: takes those top matches, adds them into a prompt which
   tells the model to answer *only* from that context (and refuse if it's
   not there), and sends it to Foundry Local's `qwen2.5-0.5b` chat model.
6. **`app.py`**: a small Streamlit page wrapping all of the above so you
   have a user friendly interfact where you can type a question and see an
   answer instead of running scripts from the terminal.---

## Setup Instructions

### 1. Requirements
* Python 3.11 or later
* Windows/macOS/Linux — no special hardware needed, this runs fine on CPU

### 2. Install dependencies
```bash
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
pip install -r requirements.txt
```

### 3. Build the database
```bash
python create_db.py
python ingest.py
```

### 4. Run it
```bash
streamlit run app.py
```
The first run downloads two small models (embedding + chat), which 
need internet once. Every run after that is fully offline.

## 🛠️ Design Decisions

* **Standard `foundry-local-sdk`, not the WinML variant**: my laptop's GPU
  is old, so hardware acceleration wasn't going to help much, so I stuck with
  the simpler CPU-only package instead of chasing driver complexity for no real benefit.
* **`qwen2.5-0.5b` for chat, not a bigger model**: I actually tried
  swapping in `phi-3.5-mini` (a much bigger, more capable model) to see if
  it handled edge cases better. It did briefly, but running both the
  embedding model and a bigger chat model was heavier than what my RAM could
  handle, and the whole thing crashed mid-request. So I reverted back to the
  small model, which fits comfortably.
* **SQLite, embeddings stored as JSON text**: no need for a real vector
  database at this scale, since a small amount of information chunks fit
  easily in memory, so the brute-force cosine similarity in Python is
  fast enough, and SQLite needs zero setup since it's built into Python.
* **A similarity threshold before calling the model at all**: early on,
  the assistant would confidently answer completely unrelated questions
  ("what color is the sky?") because it was still handing the prompt to
  the model as "context," even when nothing relevant existed. Adding a
  cutoff (`score < 0.5` → refuse immediately) ensured that the prompt
  isn't sent to the model.

## ⚠️ Limitations

* **Small model, occasional garbled output.**: `qwen2.5-0.5b` is tiny
  (0.5B parameters), and every so often it'll mix up a number that should
  be the correct answer (e.g., once returned "four twenty-two tooth
  count" instead of "42 teeth"). Re-running the same question usually
  fixes it. This is an inconsistent generation, not a retrieval bug.
* **Weak on topics adjacent to, but not actually in, the document.**: Before
  I added puppy-teeth info to the document, asking about puppies (a topic
  never covered) made the model guess a plausible-sounding but wrong number,
  and a *different* wrong number every time I asked. Expanding the
  document to actually cover that topic fixed it, which says more about
  the importance of good document coverage than about a bug in the code.
* **CPU-only, 8GB RAM ceiling.**: Confirmed directly: this setup can't
  comfortably run a bigger, more accurate model alongside the embedding
  model at the same time on this hardware. The trade-off of using a small
  on-device model is that even though it's faster and lighter, it's also
  less sharp on edge cases.
* **Plain text/markdown only.**: No PDF or OCR support. Documents need to
  be `.md` or `.txt`. Anything from Word or RTF carries hidden formatting
  that would pollute the chunks.
