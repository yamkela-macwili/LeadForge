from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    company = Column(String)
    role = Column(String)
    niche = Column(String)
    source = Column(String)
    url = Column(String)
    location = Column(String)
    date_added = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'phone': self.phone,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'role': self.role,
            'niche': self.niche,
            'source': self.source,
            'url': self.url,
            'location': self.location,
            'date_added': self.date_added
        }

class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    url = Column(String)
    status = Column(String)
    last_scraped = Column(DateTime)

class Export(Base):
    __tablename__ = 'exports'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    query_params = Column(String)

class Blacklist(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    identifier = Column(String, unique=True) # Phone or Email
    reason = Column(String)

# Database Setup
DATABASE_URL = "sqlite:///leads.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
