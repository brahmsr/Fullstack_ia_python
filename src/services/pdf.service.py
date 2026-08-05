import os

from langchain_community.document_loaders import UnstructuredPDFLoader

class PDFService:
    def carregar_documentos(self, data_dir):

        documentos = []

        for arquivo in os.listdir(data_dir):

            if arquivo.endswith(".pdf"):

                loader = UnstructuredPDFLoader(
                    os.path.join(data_dir, arquivo),
                    strategy="hi_res",
                    extract_images_in_pdf=True,
                    languages=["por"]
                )

                documentos.extend(loader.load())

        if not documentos:
            raise Exception("Nenhum PDF encontrado.")

        return documentos