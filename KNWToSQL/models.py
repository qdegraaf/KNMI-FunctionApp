from sqlalchemy import (
    Column,
    DateTime,
    Float,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class KNWData(Base):  # type: ignore
    """
    From file header:
    F (wind speed) in m/s, D (wind from direction) in degree and clockwise from North,
    T (temperature) in Kelvin, Q (specific humidity) in kg/kg, P (pressure) in Pascal
    """

    __tablename__ = "knw_data"

    dtg = Column(DateTime, primary_key=True, nullable=False)
    f010 = Column(Float, nullable=False)
    d010 = Column(Float, nullable=False)
    t010 = Column(Float, nullable=False)
    q010 = Column(Float, nullable=False)
    p010 = Column(Float, nullable=False)
    f020 = Column(Float, nullable=False)
    d020 = Column(Float, nullable=False)
    t020 = Column(Float, nullable=False)
    q020 = Column(Float, nullable=False)
    p020 = Column(Float, nullable=False)
    f040 = Column(Float, nullable=False)
    d040 = Column(Float, nullable=False)
    t040 = Column(Float, nullable=False)
    q040 = Column(Float, nullable=False)
    p040 = Column(Float, nullable=False)
    f060 = Column(Float, nullable=False)
    d060 = Column(Float, nullable=False)
    t060 = Column(Float, nullable=False)
    q060 = Column(Float, nullable=False)
    p060 = Column(Float, nullable=False)
    f080 = Column(Float, nullable=False)
    d080 = Column(Float, nullable=False)
    t080 = Column(Float, nullable=False)
    q080 = Column(Float, nullable=False)
    p080 = Column(Float, nullable=False)
    f100 = Column(Float, nullable=False)
    d100 = Column(Float, nullable=False)
    t100 = Column(Float, nullable=False)
    q100 = Column(Float, nullable=False)
    p100 = Column(Float, nullable=False)
    f150 = Column(Float, nullable=False)
    d150 = Column(Float, nullable=False)
    t150 = Column(Float, nullable=False)
    q150 = Column(Float, nullable=False)
    p150 = Column(Float, nullable=False)
    f200 = Column(Float, nullable=False)
    d200 = Column(Float, nullable=False)
    t200 = Column(Float, nullable=False)
    q200 = Column(Float, nullable=False)
    p200 = Column(Float, nullable=False)
