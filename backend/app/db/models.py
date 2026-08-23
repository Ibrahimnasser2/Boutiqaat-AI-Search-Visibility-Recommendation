from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Query(Base):
    __tablename__ = "queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String(500), unique=True)
    intent: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))
    geography: Mapped[str] = mapped_column(String(50), default="GCC")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    runs: Mapped[list["AIRun"]] = relationship(back_populates="query", cascade="all, delete-orphan")


class AIRun(Base):
    __tablename__ = "ai_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query_id: Mapped[int] = mapped_column(ForeignKey("queries.id"))
    provider: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    raw_answer: Mapped[str] = mapped_column(Text)
    structured_answer: Mapped[str] = mapped_column(Text)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="completed")

    query: Mapped["Query"] = relationship(back_populates="runs")
    visibility: Mapped["VisibilityAnalysis | None"] = relationship(
        back_populates="run", uselist=False, cascade="all, delete-orphan"
    )
    competitors: Mapped[list["Competitor"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    sources: Mapped[list["Source"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    opportunities: Mapped[list["Opportunity"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class VisibilityAnalysis(Base):
    __tablename__ = "visibility_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("ai_runs.id"), unique=True)
    boutiqaat_mentioned: Mapped[bool] = mapped_column(Boolean, default=False)
    boutiqaat_recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    boutiqaat_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    competitor_count: Mapped[int] = mapped_column(Integer, default=0)
    visibility_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    explanation: Mapped[str] = mapped_column(Text, default="")

    run: Mapped["AIRun"] = relationship(back_populates="visibility")


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("ai_runs.id"))
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    recommended: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence: Mapped[str] = mapped_column(Text, default="")

    run: Mapped["AIRun"] = relationship(back_populates="competitors")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("ai_runs.id"))
    url: Mapped[str] = mapped_column(String(500))
    domain: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(300), default="")
    source_type: Mapped[str] = mapped_column(String(50), default="unknown")
    supports_boutiqaat: Mapped[bool] = mapped_column(Boolean, default=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.5)

    run: Mapped["AIRun"] = relationship(back_populates="sources")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("ai_runs.id"))
    category: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200))
    explanation: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text, default="")

    run: Mapped["AIRun"] = relationship(back_populates="opportunities")
