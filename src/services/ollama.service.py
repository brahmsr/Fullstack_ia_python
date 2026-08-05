# pyrefly: ignore [missing-import]
import ollama
import json

print("Baixando o modelo...")
with open ("config/config.json", "r") as f:
    config = json.load(f)

model = config["MODEL"].strip()
embedding_model = config["EMBEDDING_MODEL"].strip()

print(f"Baixando o modelo {model}")
try:
    for progress in ollama.pull(model, stream=True):
        status = progress.get("status", "")

        if "completed" in progress and "total" in progress:
            total = progress["total"]
            completed = progress["completed"]

            percent = completed / total * 100

            bar = "█" * int(percent / 2)
            bar += "-" * (50 - len(bar))

            print(f"\r[{bar}] {percent:6.2f}% - {status}", end="")

        else:
            print(f"\n{status}")
except Exception as e:
    print(f"Modelo já existe ou ocorreu um erro: {e}")

print(f"Baixando o modelo de embedding {embedding_model}")
try:
    for progress in ollama.pull(embedding_model, stream=True):
        status = progress.get("status", "")

        if "completed" in progress and "total" in progress:
            total = progress["total"]
            completed = progress["completed"]

            percent = completed / total * 100

            bar = "█" * int(percent / 2)
            bar += "-" * (50 - len(bar))

            print(f"\r[{bar}] {percent:6.2f}% - {status}", end="")

        else:
            print(f"\n{status}")
except Exception as e:
    print(f"Modelo já existe ou ocorreu um erro: {e}")


response = ollama.generate(model=config["MODEL"], prompt='você está vivo?')
print(response['response'])