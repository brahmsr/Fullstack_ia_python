"""
OBS: Garante que os modelos exigidos pela aplicação existem no servidor Ollama,
é idempotente: se o modelo já estiver no volume do Ollama, nada é baixado.
"""

import json
import os
import sys
from pathlib import Path

import ollama

CONFIG_PATH = Path(__file__).resolve().parent.parent / "src" / "config" / "config.json"


def normalizar(nome: str) -> str:
    """Ollama trata 'Qwen3-Embedding' e 'Qwen3-Embedding:latest' como o mesmo modelo."""
    nome = nome.strip()
    return nome if ":" in nome else f"{nome}:latest"


def baixar(client: ollama.Client, modelo: str) -> None:
    print(f"[modelos] Baixando {modelo} (pode levar alguns minutos)...", flush=True)
    ultimo_status = None
    for progresso in client.pull(modelo, stream=True):
        status = progresso.get("status", "")
        total = progresso.get("total")
        completo = progresso.get("completed")

        if total and completo:
            percentual = completo / total * 100
            print(f"\r[modelos] {status}: {percentual:6.2f}%", end="", flush=True)
        elif status != ultimo_status:
            print(f"\n[modelos] {status}", end="", flush=True)
            ultimo_status = status

    print(f"\n[modelos] {modelo} pronto.", flush=True)


def main() -> int:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    desejados = [config["MODEL"], config["EMBEDDING_MODEL"]]

    # host=None faz o client cair no fallback OLLAMA_HOST do próprio pacote.
    client = ollama.Client(host=os.getenv("OLLAMA_HOST"))

    instalados = {normalizar(m.model).lower() for m in client.list().models}
    print(f"[modelos] Já disponíveis: {sorted(instalados) or 'nenhum'}", flush=True)

    for modelo in desejados:
        alvo = normalizar(modelo)
        if alvo.lower() in instalados:
            print(f"[modelos] {alvo} já existe — pulando.", flush=True)
            continue
        try:
            baixar(client, modelo.strip())
        except Exception as erro:
            # Falha aqui é fatal: sem o modelo, o RAG quebra na primeira consulta com um erro bem menos claro do que este.
            print(f"\n[modelos] ERRO ao baixar '{modelo}': {erro}", file=sys.stderr)
            print(
                "[modelos] Verifique se o nome em src/config/config.json "
                "corresponde a um modelo publicado no registro do Ollama.",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
