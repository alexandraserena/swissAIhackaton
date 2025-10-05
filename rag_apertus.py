'''import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import re
import unicodedata
import openai

# --- Funzioni preprocessing ---
def clean_text(text):
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'[^\w\s\.,;:\-]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return unicodedata.normalize('NFKC', text).strip()

def preprocess_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text += f"[Page {page_num}] {page_text} "
    return clean_text(text)

def preprocess_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    for tag in soup(["script", "style", "header", "footer", "nav"]):
        tag.decompose()
    return clean_text(soup.get_text(separator=" "))

# --- Carica documenti e chunk ---
docs = [
    {"source": "BLI_Vivre_a_Lausanne_2023_A5-IT-WEB.pdf", "text": preprocess_pdf("BLI_Vivre_a_Lausanne_2023.pdf")},
    {"source": "Benvenuti_nel_Canton_Zurigo.pdf", "text": preprocess_pdf("Benvenuti_nel_Canton_Zurigo.pdf")},
    {"source": "Canton_Zurigo.pdf", "text": preprocess_pdf("Canton_Zurigo.pdf")},
    {"source": "Citta_Zurigo.pdf", "text": preprocess_pdf("Citta_Zurigo.pdf")},
    {"source": "[EN]LN_BCI_BrochureBienvenue_241113.pdf", "text": preprocess_pdf("[EN]LN_BCI_BrochureBienvenue_241113.pdf")},
    {"source": "canton_NEUCHATEL.pdf", "text": preprocess_pdf("canton_NEUCHATEL.pdf")},
    {"source": "cantone_NEUCHATEL.pdf", "text": preprocess_pdf("cantone_NEUCHATEL.pdf")},
    {"source": "neuchatel_site.html", "text": preprocess_html("neuchatel_site.html")},
    {"source": "vaud_site.html", "text": preprocess_html("vaud_site.html")},
    {"source": "zurich_site.html", "text": preprocess_html("zurich_site.html")}
]


def chunk_text(text, max_chars=1000):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

chunks = []
for doc in docs:
    for chunk in chunk_text(doc["text"]):
        chunks.append({"source": doc["source"], "content": chunk})

# --- Embeddings e FAISS ---
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
chunk_texts = [c['content'] for c in chunks]
embeddings = embed_model.encode(chunk_texts, convert_to_numpy=True)
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# --- Apertus Client ---
client = openai.OpenAI(
    api_key=os.getenv("SWISS_AI_PLATFORM_API_KEY"),
    base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
)

# Aggiungi questa variabile globale per lo storico
chat_history = []

def answer_query_with_history(query, top_k=3):
    global chat_history

    # Trova i chunk più simili
    query_emb = embed_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, k=top_k)
    
    # Prepara i chunk con fonte
    prompt_chunks = []
    sources = []
    for idx in I[0]:
        chunk = chunks[idx]
        prompt_chunks.append(f"Source: {chunk['source']}\n{chunk['content']}")
        sources.append(chunk['source'])

    context = "\n\n".join(prompt_chunks)

    # Aggiungi la nuova domanda alla storia
    chat_history.append({"role": "user", "content": query})

    # Costruisci messaggi: contesto + storico
    messages = [{"role": "system", "content": context}] + chat_history

    # Chiamata al modello
    response = client.chat.completions.create(
        model="swiss-ai/Apertus-70B",
        messages=messages
    )

    answer = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": answer})

    # Restituisci anche le fonti
    return answer, sources'''


import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import re
import unicodedata
import openai

# --- Funzioni preprocessing ---
def clean_text(text):
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'[^\w\s\.,;:\-]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return unicodedata.normalize('NFKC', text).strip()

def preprocess_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page_num, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            text += f"[Page {page_num}] {page_text} "
    return clean_text(text)

def preprocess_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        for tag in soup(["script", "style", "header", "footer", "nav"]):
            tag.decompose()
        return clean_text(soup.get_text(separator=" "))

# --- Carica documenti e chunk ---
docs = [
    {"source": "BLI_Vivre_a_Lausanne_2023_A5-IT-WEB.pdf", "text": preprocess_pdf("BLI_Vivre_a_Lausanne_2023.pdf")},
    {"source": "Benvenuti_nel_Canton_Zurigo.pdf", "text": preprocess_pdf("Benvenuti_nel_Canton_Zurigo.pdf")},
    {"source": "Canton_Zurigo.pdf", "text": preprocess_pdf("Canton_Zurigo.pdf")},
    {"source": "Citta_Zurigo.pdf", "text": preprocess_pdf("Citta_Zurigo.pdf")},
    {"source": "[EN]LN_BCI_BrochureBienvenue_241113.pdf", "text": preprocess_pdf("[EN]LN_BCI_BrochureBienvenue_241113.pdf")},
    {"source": "canton_NEUCHATEL.pdf", "text": preprocess_pdf("canton_NEUCHATEL.pdf")},
    {"source": "cantone_NEUCHATEL.pdf", "text": preprocess_pdf("cantone_NEUCHATEL.pdf")},
    {"source": "neuchatel_site.html", "text": preprocess_html("neuchatel_site.html")},
    {"source": "vaud_site.html", "text": preprocess_html("vaud_site.html")},
    {"source": "zurich_site.html", "text": preprocess_html("zurich_site.html")}
]

def chunk_text(text, max_chars=1000):
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

chunks = []
for doc in docs:
    for chunk in chunk_text(doc["text"]):
        chunks.append({"source": doc["source"], "content": chunk})

# --- Embeddings e FAISS ---
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
chunk_texts = [c['content'] for c in chunks]
embeddings = embed_model.encode(chunk_texts, convert_to_numpy=True)
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# --- Apertus Client ---
client = openai.OpenAI(
    api_key=os.getenv("SWISS_AI_PLATFORM_API_KEY"),
    base_url="https://api.swisscom.com/layer/swiss-ai-weeks/apertus-70b/v1"
)

# --- Variabile globale per lo storico ---
chat_history = []

def answer_query_with_history(query):
    global chat_history

    # Trova i 3 chunk più simili
    query_emb = embed_model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_emb, k=3)
    prompt_chunks = [f"Source: {chunks[i]['source']}\n{chunks[i]['content']}" for i in I[0]]
    context = "\n\n".join(prompt_chunks)

    # Aggiungi la nuova domanda alla storia
    chat_history.append({"role": "user", "content": query})

    # Costruisci messaggi: contesto + storico
    messages = [{"role": "system", "content": context}] + chat_history

    # Chiamata al modello
    response = client.chat.completions.create(
        model="swiss-ai/Apertus-70B",
        messages=messages
    )

    answer = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": answer})

    return answer
