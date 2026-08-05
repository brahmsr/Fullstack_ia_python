from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkService:

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, #aprox 1k caractere por bloco
            chunk_overlap=200 #sobreposição em aprox 200 caracteres (continuidade)
        )

    def gerar_chunks(self, documentos):

        return self.splitter.split_documents(documentos)