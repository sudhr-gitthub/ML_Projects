from __future__ import annotations

from datetime import datetime, date
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Date, ForeignKey, Text, Enum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import LargeBinary

STAT_TYPES = ("knowledge", "guts", "proficiency", "kindness", "charm")
MISSION_TYPES = ("study", "fitness", "sleep", "nutrition", "reflection", "social")
DIFFICULTY = ("easy", "medium", "hard")
MISSION_STATUS = ("pending", "completed", "failed")
SCOPE = ("global", "local")
PERIOD = ("weekly", "alltime")
VOICE_ROLE = ("user", "assistant")
MEM_KIND = ("journal", "summary", "goal")
MOOD = ("great", "good", "okay", "low", "rough")

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    handle: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    consent_leaderboard: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_location: Mapped[bool] = mapped_column(Boolean, default=False)

    city: Mapped[str | None] = mapped_column(String(64), nullable=True)
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    stats: Mapped[list["Stat"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    assignments: Mapped[list["MissionAssignment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    voice_messages: Mapped[list["VoiceMessage"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    voice_memory: Mapped[list["VoiceMemory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    journal: Mapped[list["JournalEntry"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit: Mapped[list["AuditLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    goals_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")

class Stat(Base):
    __tablename__ = "stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(Enum(*STAT_TYPES, name="stat_type"), index=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="stats")

class Mission(Base):
    __tablename__ = "missions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(140))
    type: Mapped[str] = mapped_column(Enum(*MISSION_TYPES, name="mission_type"), index=True)
    difficulty: Mapped[str] = mapped_column(Enum(*DIFFICULTY, name="difficulty"), index=True)
    xp_reward: Mapped[int] = mapped_column(Integer, default=10)

    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    geo_rule_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_for_date: Mapped[date] = mapped_column(Date, index=True)
    created_by_system: Mapped[bool] = mapped_column(Boolean, default=True)

    assignments: Mapped[list["MissionAssignment"]] = relationship(back_populates="mission", cascade="all, delete-orphan")

class MissionAssignment(Base):
    __tablename__ = "mission_assignments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), index=True)

    date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(Enum(*MISSION_STATUS, name="mission_status"), default="pending", index=True)

    proof_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(back_populates="assignments")
    mission: Mapped["Mission"] = relationship(back_populates="assignments")

class RankSnapshot(Base):
    __tablename__ = "rank_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    scope: Mapped[str] = mapped_column(Enum(*SCOPE, name="rank_scope"), index=True)
    period: Mapped[str] = mapped_column(Enum(*PERIOD, name="rank_period"), index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    rank: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class VoiceMessage(Base):
    __tablename__ = "voice_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    role: Mapped[str] = mapped_column(Enum(*VOICE_ROLE, name="voice_role"), index=True)
    text: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    embedding_vector: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    user: Mapped["User"] = relationship(back_populates="voice_messages")

class VoiceMemory(Base):
    __tablename__ = "voice_memory"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    kind: Mapped[str] = mapped_column(Enum(*MEM_KIND, name="mem_kind"), index=True)
    content: Mapped[str] = mapped_column(Text)

    vector: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="voice_memory")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    mood: Mapped[str] = mapped_column(Enum(*MOOD, name="mood"), index=True)
    text: Mapped[str] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(String(256), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="journal")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    event_type: Mapped[str] = mapped_column(String(64), index=True)
    meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="audit")
