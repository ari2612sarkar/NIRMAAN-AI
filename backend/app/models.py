"""SQLAlchemy ORM models.

Scope note: this is the trimmed, hackathon-MVP schema (no auth tables — the
app is a single open demo instance; no `predictions`/`scenarios` persistence
tables — forecasts and simulations are computed on demand and returned
directly, not stored, which keeps the system simpler and removes a class of
stale-cache bugs for a short demo).
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    zone_type: Mapped[str] = mapped_column(String(30))  # residential/commercial/institutional/mixed
    population_estimate: Mapped[int] = mapped_column(Integer)

    locations: Mapped[list["Location"]] = relationship(back_populates="zone")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"))
    name: Mapped[str] = mapped_column(String(150))
    location_type: Mapped[str] = mapped_column(String(30))  # household/commercial/institutional/public
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    zone: Mapped[Zone] = relationship(back_populates="locations")
    bins: Mapped[list["Bin"]] = relationship(back_populates="location")
    waste_records: Mapped[list["WasteRecord"]] = relationship(back_populates="location")


class Bin(Base):
    __tablename__ = "bins"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    bin_code: Mapped[str] = mapped_column(String(20), unique=True)
    capacity_litres: Mapped[float] = mapped_column(Float)
    waste_category: Mapped[str] = mapped_column(String(20))  # mixed/wet/dry/recyclable
    last_known_fill_pct: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="active")

    location: Mapped[Location] = relationship(back_populates="bins")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_code: Mapped[str] = mapped_column(String(20), unique=True)
    vehicle_type: Mapped[str] = mapped_column(String(30))
    capacity_kg: Mapped[float] = mapped_column(Float)
    purchase_date: Mapped[dt.date] = mapped_column(Date)
    odometer_km: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="active")

    maintenance_records: Mapped[list["MaintenanceRecord"]] = relationship(back_populates="vehicle")


class WasteRecord(Base):
    """Daily waste generated at a location, by category."""

    __tablename__ = "waste_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    zone_id: Mapped[int] = mapped_column(ForeignKey("zones.id"))
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    waste_category: Mapped[str] = mapped_column(String(20))  # mixed/wet/dry/recyclable
    quantity_kg: Mapped[float] = mapped_column(Float)
    is_anomalous_seed: Mapped[bool] = mapped_column(Boolean, default=False)  # ground-truth marker for eval only

    location: Mapped[Location] = relationship(back_populates="waste_records")


class CollectionEvent(Base):
    __tablename__ = "collection_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    fill_pct_at_collection: Mapped[float] = mapped_column(Float)
    quantity_kg: Mapped[float] = mapped_column(Float)
    missed: Mapped[bool] = mapped_column(Boolean, default=False)


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    event_type: Mapped[str] = mapped_column(String(20))  # scheduled/emergency/inspection
    cost: Mapped[float] = mapped_column(Float)
    downtime_hours: Mapped[float] = mapped_column(Float)
    odometer_km_at_event: Mapped[float] = mapped_column(Float)

    vehicle: Mapped[Vehicle] = relationship(back_populates="maintenance_records")


class CostRecord(Base):
    """Daily aggregated operating cost, by category, org-wide or per zone."""

    __tablename__ = "cost_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("zones.id"), nullable=True)
    cost_category: Mapped[str] = mapped_column(String(20))  # fuel/labour/maintenance/infrastructure
    amount: Mapped[float] = mapped_column(Float)


class DataProvenance(Base):
    __tablename__ = "data_provenance"

    id: Mapped[int] = mapped_column(primary_key=True)
    seed: Mapped[int] = mapped_column(Integer)
    generator_version: Mapped[str] = mapped_column(String(20))
    generated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)
    note: Mapped[str] = mapped_column(String(300))
