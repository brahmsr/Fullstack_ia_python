from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    chunk = Column(String, nullable=False)
    source = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    edited_at = Column(DateTime, onupdate=datetime.now)
    