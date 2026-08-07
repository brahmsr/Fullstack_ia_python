from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import os
from pathlib import Path
from urllib.parse import quote_plus

config_path = Path(__file__).resolve().parent.parent / "config" / "config.json"

with open (config_path, "r") as f:
    config = json.load(f)


# As variáveis de ambiente têm precedência sobre o config.json. Isso permite
# que o mesmo código rode local (host=localhost) e em container (host=postgres,
# o nome do serviço na rede Docker) sem nenhuma alteração.
DB_USER = os.getenv("DB_USER", config["DB_USER"])
DB_PASSWORD = os.getenv("DB_PASSWORD", config["DB_PASSWORD"])
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", str(config["DB_PORT"]))
DB_NAME = os.getenv("DB_NAME", config["DB_NAME"])

# quote_plus escapa caracteres que têm significado especial numa URL — sem ele, uma senha com '@', '/' ou ':' trunca a string de conexão.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)

# pool_pre_ping descarta conexões mortas antes de usá-las: em Docker o postgres pode reiniciar sob a aplicação, deixando o pool com sockets inválidos.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)