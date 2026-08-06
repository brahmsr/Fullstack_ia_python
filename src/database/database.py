# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
import json
from pathlib import Path

config_path = Path(__file__).resolve().parent.parent / "config" / "config.json"

with open (config_path, "r") as f:
    config = json.load(f)


DATABASE_URL = f"postgresql://{config['DB_USER']}:{config['DB_PASSWORD']}@localhost:{config['DB_PORT']}/{config['DB_NAME']}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)