import json #ler o arquivo json
import os #lista os arquivos do diretório


from langchain_classic.chains import RetrievalQA # orquestra o processo do RAG (Modelo + recuperador)\n
from langchain_ollama import ChatOllama # instanciando o modelo de linguagem (para testes)
from langchain_community.document_loaders import UnstructuredPDFLoader #carregar documentos PDF
from langchain_text_splitters import RecursiveCharacterTextSplitter #cortador de texto (caracteres recursivos)\n
from langchain_community.vectorstores import FAISS #busca por similaridade (vetores)
from langchain_ollama import OllamaEmbeddings #instanciando o modelo de embeddings (vetores)

with open ("../config/config.json", "r") as f:
    config = json.load(f)
    
llm = ChatOllama(model=config["MODEL"], temperature=0)
embeddings = OllamaEmbeddings(model=config["EMBEDDING_MODEL"])
DATA_DIR = config["DATA_DIR"]
VECTOR_STORE_DIR = config["VECTOR_STORE_DIR"]

# Cortar os PDFs que vem por padrão
def carregar_cortar_pdfs(data_dir):
    all_docs = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            loader = UnstructuredPDFLoader(
                os.path.join(data_dir, filename),
                strategy="hi_res",
                extract_images_in_pdf=True,
                languages=["por"])
            docs = loader.load()
            all_docs.extend(docs)

    if not all_docs:
        raise ValueError("Sem PDFs na pasta de dados")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, #aprox 1k caractere por bloco
        chunk_overlap=200 #sobreposição em aprox 200 caracteres (continuidade)
        )
    chunks = splitter.split_documents(all_docs)
    return chunks

chunks = carregar_cortar_pdfs(f"../{DATA_DIR}")
print(f"carregado e cortado em {len(chunks)} chunks.")

# Criação dos vectorstores
def criar_vectorstore(chunks, vectorstoreDir):
    embeddings = OllamaEmbeddings(model=config["EMBEDDING_MODEL"]) #instanciando o modelo de embeddings (vetores)
    vectorstore = FAISS.from_documents(chunks, embeddings) # cria o vetorstore a partir dos chunks e do modelo de embeddings
    vectorstore.save_local(vectorstoreDir) # salva o vetorstore localmente
    
    print(f"Vectorstore criado e salvo em {vectorstoreDir}")

vectorstoreDir = f"../{VECTOR_STORE_DIR}"
criar_vectorstore(chunks, vectorstoreDir)

vector_dir = f"../{VECTOR_STORE_DIR}"

# Carregar os vectorstores
def carregar_vectorstore(vectorstoreDir):
    embeddings = OllamaEmbeddings(model=config["EMBEDDING_MODEL"]) #instanciando o modelo de embeddings (vetores)
    vectorstore = FAISS.load_local(
        folder_path=vectorstoreDir, 
        embeddings=embeddings,
        allow_dangerous_deserialization = True
        ) #carrega o vetorstore localmente
    return vectorstore

# Perguntar ao RAG
def perguntar_ao_rag(pergunta):
    vectorstore = carregar_vectorstore(vector_dir)
    retriever = vectorstore.as_retriever() #recuperador de documento
    llm = ChatOllama(model=config["MODEL"], temperature=0) #instanciando o modelo de linguagem (para testes)
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever) #orquestra o processo do RAG (Modelo + recuperador)
    return qa.run(pergunta) #retorna a resposta do RAG
