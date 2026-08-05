from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

with open ("../config/config.json", "r") as f:
    config = json.load(f)


DATABASE_URL = f"postgresql://{config['DB_USER']}:{config['DB_PASSWORD']}@postgres:{config['DB_PORT']}/{config['DB_NAME']}"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)