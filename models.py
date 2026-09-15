from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), default='terapis')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class PasienPrana(Base):
    __tablename__ = 'pasien_prana'
    id = Column(Integer, primary_key=True)
    nama = Column(String(100), nullable=False)
    domisili = Column(String(100))
    nama_ibu = Column(String(100))
    tanggal_lahir = Column(Date, nullable=False)
    kunjungan = relationship('KunjunganPrana', backref='pasien', cascade="all, delete-orphan")

class KunjunganPrana(Base):
    __tablename__ = 'kunjungan_prana'
    id = Column(Integer, primary_key=True)
    pasien_id = Column(Integer, ForeignKey('pasien_prana.id'), nullable=False)
    tanggal_kunjungan = Column(Date, default=datetime.utcnow)
    keluhan = Column(Text)
    diagnosa = Column(Text)
    terapi = Column(Text)
    hasil = Column(Text)

class PasienHypno(Base):
    __tablename__ = 'pasien_hypno'
    id = Column(Integer, primary_key=True)
    nama = Column(String(100), nullable=False)
    domisili = Column(String(100))
    nama_ibu = Column(String(100))
    tanggal_lahir = Column(Date, nullable=False)
    kunjungan = relationship('KunjunganHypno', backref='pasien', cascade="all, delete-orphan")

class KunjunganHypno(Base):
    __tablename__ = 'kunjungan_hypno'
    id = Column(Integer, primary_key=True)
    pasien_id = Column(Integer, ForeignKey('pasien_hypno.id'), nullable=False)
    tanggal_kunjungan = Column(Date, default=datetime.utcnow)
    keluhan = Column(Text)
    diagnosa = Column(Text)
    terapi = Column(Text)
    hasil = Column(Text)

# Setup Database Connection
engine = create_engine('sqlite:///symmetria_mobile.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    if not session.query(User).filter_by(username='admin').first():
        admin = User(
            username='admin',
            role='admin',
            password_hash=generate_password_hash('admin123')
        )
        session.add(admin)
        session.commit()
    session.close()