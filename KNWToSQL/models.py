from sqlalchemy import Column, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class KNWData(Base):
    """
    From file header:
    F (wind speed) in m/s, D (wind from direction) in degree and clockwise from North,
    T (temperature) in Kelvin, Q (specific humidity) in kg/kg, P (pressure) in Pascal
    """
    __tablename__ = "knw_data"

    dtg = Column(DateTime, primary_key=True, nullable=False)
    f010 = Column(Float, nullable=False, )
    d010 = Column(Float, nullable=False)
    to10 = Column(Float, nullable=False)
    q010 = Column(Float, nullable=False)
    p010 = Column(Float, nullable=False)
    f020 = Column(Float, nullable=False)
    d020 = Column(Float, nullable=False)
    to20 = Column(Float, nullable=False)
    q020 = Column(Float, nullable=False)
    p020 = Column(Float, nullable=False)
    f040 = Column(Float, nullable=False)
    d040 = Column(Float, nullable=False)
    to40 = Column(Float, nullable=False)
    q040 = Column(Float, nullable=False)
    p040 = Column(Float, nullable=False)
    f060 = Column(Float, nullable=False)
    d060 = Column(Float, nullable=False)
    to60 = Column(Float, nullable=False)
    q060 = Column(Float, nullable=False)
    p060 = Column(Float, nullable=False)
    f080 = Column(Float, nullable=False)
    d080 = Column(Float, nullable=False)
    to80 = Column(Float, nullable=False)
    q080 = Column(Float, nullable=False)
    p080 = Column(Float, nullable=False)
    f0100 = Column(Float, nullable=False)
    d0100 = Column(Float, nullable=False)
    to100 = Column(Float, nullable=False)
    q0100 = Column(Float, nullable=False)
    p0100 = Column(Float, nullable=False)
    f0150 = Column(Float, nullable=False)
    d0150 = Column(Float, nullable=False)
    to150 = Column(Float, nullable=False)
    q0150 = Column(Float, nullable=False)
    p0150 = Column(Float, nullable=False)
    f0200 = Column(Float, nullable=False)
    d0200 = Column(Float, nullable=False)
    to200 = Column(Float, nullable=False)
    q0200 = Column(Float, nullable=False)
    p0200 = Column(Float, nullable=False)
