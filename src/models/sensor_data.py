from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SensorData(Base):
    __tablename__ = "sensorsData"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    z_rms_velocity_in_s = Column(Float)
    z_rms_velocity_mm_s = Column(Float)
    temperature_f = Column(Float)
    temperature_c = Column(Float)
    x_rms_velocity_in_s = Column(Float)
    x_rms_velocity_mm_s = Column(Float)
    z_peak_acceleration_g = Column(Float)
    x_peak_acceleration_g = Column(Float)
    z_peak_vel_comp_freq_hz = Column(Float)
    x_peak_vel_comp_freq_hz = Column(Float)
    z_rms_acceleration_g = Column(Float)
    x_rms_acceleration_g = Column(Float)
    z_kurtosis = Column(Float)
    x_kurtosis = Column(Float)
    z_crest_factor = Column(Float)
    x_crest_factor = Column(Float)
    z_peak_velocity_in_s = Column(Float)
    z_peak_velocity_mm_s = Column(Float)
    x_peak_velocity_in_s = Column(Float)
    x_peak_velocity_mm_s = Column(Float)
    z_high_freq_rms_accel_g = Column(Float)
    x_high_freq_rms_accel_g = Column(Float)
    fault = Column(String)
    rpm = Column(Float)
