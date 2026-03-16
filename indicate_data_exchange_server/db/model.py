import enum
from datetime import datetime

from sqlalchemy import Integer, VARCHAR, Enum, NUMERIC, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class IndicatorInfo(Base):
    __tablename__ = "indicator_info"

    concept_id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(VARCHAR)

    description: Mapped[str] = mapped_column(VARCHAR)

class AggregationKind(enum.Enum):
    daily   = "daily"
    weekly  = "weekly"
    monthly = "monthly"
    yearly  = "yearly"

class AggregatedResult(Base):
    __tablename__ = 'aggregated_results'

    result_id: Mapped[int] = mapped_column(primary_key=True)

    provider_id: Mapped[str] = mapped_column(VARCHAR(36))

    indicator_concept_id: Mapped[int] = mapped_column(Integer)

    aggregation_kind: Mapped[AggregationKind] = mapped_column(Enum(AggregationKind,
                                                                   name="aggregation_kind"))

    period_start: Mapped[datetime] = mapped_column(TIMESTAMP)

    average_value: Mapped[float] = mapped_column(NUMERIC)

    observation_count: Mapped[int] = mapped_column(Integer)

    upload_time: Mapped[datetime] = mapped_column(TIMESTAMP)