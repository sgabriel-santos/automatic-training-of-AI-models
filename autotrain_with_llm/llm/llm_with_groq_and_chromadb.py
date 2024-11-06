import chromadb
from sentence_transformers import SentenceTransformer
from groq import AuthenticationError
from fastapi import HTTPException, status
from autotrain_with_llm.middleware.utils_llm import get_llm_instance, get_text_model_to_llm

# Constants
COLLECTION_NAME = 'treinamento_modelo'
LLM_MODEL = 'llama3-8b-8192'
ST_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

chroma_client = chromadb.Client()
collection = None
        
def generate_collection():
    global collection
    if collection: chroma_client.delete_collection(name=COLLECTION_NAME)        
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

def embed_text(text):
    embeddings = ST_MODEL.encode([text], convert_to_tensor=True)
    return embeddings.cpu().numpy()[0]

def chunk_text(text, chunk_size=512):
    return [text[i: i + chunk_size] for i in range(0, len(text), chunk_size)]

# Recuperador
def search_similar_documents(query, top_k = 5):
    global collection
    query_embedding = embed_text(query).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    similar_documents = [metadata['content'] for metadata in results['metadatas'][0]]
    return similar_documents

def generate_decision(new_document, similar_documents):
    llm = get_llm_instance()
    
    input_text = f"Texto novo: {new_document}\n\nTextos Similares: {' '.join(similar_documents)}"
    try:
        result = llm.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """
                        Você é um assistente inteligente dentro de uma ferramenta No Code dedicada ao treinamento e avaliação de modelos de visão computacional. 
                        Sua função é responder de maneira clara, precisa e concisa a perguntas dos usuários relacionadas ao treinamento do modelo de visão computacional.
                        O usuário poderá fazer perguntas, antes, durante ou após o treinamento do modelo.
                        Use exemplos práticos quando necessário e evite termos muito técnicos, a menos que solicitado. 
                        Sempre que possível, ofereça sugestões para otimizar o treinamento, melhorar a precisão dos modelos ou corrigir erros comuns. 
                        Se não souber a resposta ou se a pergunta estiver fora do escopo da ferramenta, informe o usuário de forma educada e sugira recursos adicionais ou próximo passo lógico dentro da ferramenta.
                    """
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            model=LLM_MODEL,
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Erro de comunicação com o assitente virtual"
        )
        
    return result.choices[0].message.content
    
def send_answer(user_question):
    training_text = get_text_model_to_llm()
    generate_collection()
    
    chunks = chunk_text(training_text)
    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk).tolist()
        collection.add(embeddings=[embedding], ids=[f"uploaded_chunk_{i}"], metadatas=[{"filename": "Resultados do treinamento", "content": chunk}])
        
    similar_docs = search_similar_documents(user_question)
    return generate_decision(user_question, similar_docs)