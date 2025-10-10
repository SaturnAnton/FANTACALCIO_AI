from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    squads = relationship("Squad", back_populates="owner")

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    team = Column(String, index=True)
    role = Column(String, index=True)
    price = Column(Float)
    stats = Column(JSON)
    fantacalcio_data = Column(JSON)
    predictions = relationship("Prediction", back_populates="player")
    squad_players = relationship("SquadPlayer", back_populates="player")

class Squad(Base):
    __tablename__ = "squads"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner = relationship("User", back_populates="squads")
    squad_players = relationship("SquadPlayer", back_populates="squad")

class SquadPlayer(Base):
    __tablename__ = "squad_players"
    id = Column(Integer, primary_key=True, index=True)
    squad_id = Column(Integer, ForeignKey("squads.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    squad = relationship("Squad", back_populates="squad_players")
    player = relationship("Player", back_populates="squad_players")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    matchday = Column(Integer)
    predicted_fantamedia = Column(Float)
    predicted_media_voto = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    player = relationship("Player", back_populates="predictions")
