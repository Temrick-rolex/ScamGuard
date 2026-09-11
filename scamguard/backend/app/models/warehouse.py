from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class Label(StrEnum):
    FRAUDE = "FRAUDE"
    LEGITIME = "LEGITIME"
    DOUTEUX = "DOUTEUX"


class ContentType(StrEnum):
    SMS = "SMS"
    URL = "URL"
    PHONE = "PHONE"


class DimSource(Base):
    __tablename__ = "dw_dim_source"

    source_key: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String(60), unique=True)
    source_type: Mapped[str] = mapped_column(String(30))
    reliability: Mapped[int] = mapped_column(Integer, default=3)


class DimLabel(Base):
    __tablename__ = "dw_dim_label"

    label_key: Mapped[int] = mapped_column(primary_key=True)
    label_name: Mapped[str] = mapped_column(String(20), unique=True)


class DimType(Base):
    __tablename__ = "dw_dim_type"

    type_key: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(20), unique=True)


class DimDate(Base):
    __tablename__ = "dw_dim_date"

    date_key: Mapped[int] = mapped_column(primary_key=True)
    day: Mapped[date] = mapped_column(Date, unique=True)
    week: Mapped[int] = mapped_column(Integer)
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)


class EtlRun(Base):
    __tablename__ = "dw_etl_runs"

    run_id: Mapped[int] = mapped_column(primary_key=True)
    script_version: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    rows_extracted: Mapped[int] = mapped_column(Integer, default=0)
    rows_loaded: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(String(500), default="")


class FactContent(Base):
    __tablename__ = "dw_fact_content"
    __table_args__ = (UniqueConstraint("content_hash", name="uq_fact_content_hash"),)

    content_key: Mapped[int] = mapped_column(primary_key=True)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    content_anonymise: Mapped[str] = mapped_column(Text)

    source_key: Mapped[int] = mapped_column(ForeignKey("dw_dim_source.source_key"))
    label_key: Mapped[int] = mapped_column(ForeignKey("dw_dim_label.label_key"))
    type_key: Mapped[int] = mapped_column(ForeignKey("dw_dim_type.type_key"))
    date_key: Mapped[int] = mapped_column(ForeignKey("dw_dim_date.date_key"))
    run_id: Mapped[int] = mapped_column(ForeignKey("dw_etl_runs.run_id"))

    langue: Mapped[str] = mapped_column(String(10), default="fr")
    longueur: Mapped[int] = mapped_column(Integer, default=0)
    nb_liens: Mapped[int] = mapped_column(Integer, default=0)
    nb_numeros: Mapped[int] = mapped_column(Integer, default=0)
