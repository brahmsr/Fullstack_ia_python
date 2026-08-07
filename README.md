# fullstack IA com Python

- [x] setup de ambiente virtual
- [x] instalação de dependências
- [x] iniciar notebook
- [x] carregar dados do pdf
- [x] testar com ollama
- [x] carregar dados do csv
- [x] gerar embeddings e vectorstore
- [x] implementar RAG
- [x] implementar modelo preditivo
- [x] treinar modelo preditivo
- [x] testar modelo preditivo
- [x] configurar StreamLit (melhor para interface e plotagem de gráficos)
- [x] integrar tudo

## Programas necessários

- **Ollama**: baixe via powershell (windows) `irm https://ollama.com/install.ps1 | iex` ou via curl (linux/mac) `curl -fsSL https://ollama.com/install.sh | sh`. _Reponsável por rodar o modelo de linguagem._
- **Tesseract-OCR**: acesse o site: [Tesseract OCR](https://tesseractocr.org/). _Reponsável por extrair o texto de imagens._

### Start venv
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Fontes

Caso queira aprender mais sobre, utilizei esses vídeos como base: [RAG com python](https://www.youtube.com/watch?v=G3EUlIFy1fk) e  [Machine Learning com Python](https://www.youtube.com/watch?v=L4atvlp_FUE&list=PLI-bpOj6_aWGz89aONnhAUT3GpMP2VvW7&index=11), [Identificando falhas e manutenções preventivas](https://www.youtube.com/watch?v=JwZ5ffZk-fM).

_O conhecimento liberta_