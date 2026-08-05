# fullstack IA com Python

- [ ] setup de ambiente virtual
- [ ] instalação de dependências
- [ ] iniciar notebook
- [ ] carregar dados do pdf
- [ ] testar com ollama
- [ ] configurar flask
- [ ] criar api
- [ ] criar interface
- [ ] integrar tudo

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

Caso queira aprender mais sobre, utilizei 2 vídeos como base: [RAG com python](https://www.youtube.com/watch?v=G3EUlIFy1fk) e  [Machine Learning com Python](https://www.youtube.com/watch?v=L4atvlp_FUE&list=PLI-bpOj6_aWGz89aONnhAUT3GpMP2VvW7&index=11)