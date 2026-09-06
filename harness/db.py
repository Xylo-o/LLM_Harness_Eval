import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import JSON, ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column 

load_dotenv()

class Base(DeclarativeBase):
    pass


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    suite_name: Mapped[str]
    model_name: Mapped[str]
    model_version: Mapped[str]
    started_at: Mapped[datetime] = mapped_column(default=datetime.now)
    finished_at: Mapped[datetime | None]
    git_sha: Mapped[str | None]


class TestCase(Base):
    __tablename__ = "test_cases"
    __table_args__ = (UniqueConstraint('suite_name', 'case_key'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    suite_name: Mapped[str]
    case_key: Mapped[str]
    prompt: Mapped[str]
    case_metadata: Mapped[dict] = mapped_column(JSON)
    scorer_config: Mapped[dict] = mapped_column(JSON)


class Result(Base):
    __tablename__ = "results"
    __table_args__ = (UniqueConstraint('run_id', 'test_case_id'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    test_case_id: Mapped[int] = mapped_column(ForeignKey("test_cases.id"))
    raw_response: Mapped[str | None]
    latency_ms: Mapped[int | None]
    tokens_in: Mapped[int | None]
    tokens_out: Mapped[int | None]
    cost: Mapped[float | None]
    error: Mapped[str | None]


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    result_id: Mapped[int] = mapped_column(ForeignKey("results.id"))
    scorer_name: Mapped[str]
    passed: Mapped[bool]
    score: Mapped[float | None]
    detail: Mapped[dict] = mapped_column(JSON)


class FailureLabel(Base):
    __tablename__ = "failure_labels"

    id: Mapped[int] = mapped_column(primary_key=True)
    result_id: Mapped[int] = mapped_column(ForeignKey("results.id"))
    category: Mapped[str]
    note: Mapped[str | None]

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///harness.db"))

def init_db():
    Base.metadata.create_all(engine)
