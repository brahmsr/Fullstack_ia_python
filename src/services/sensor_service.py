import csv
import os
import sys
from datetime import datetime
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.database import engine, SessionLocal
from models.sensor_data import Base, SensorData

def parse_float(val):
    if val == '' or val is None:
        return None
    try:
        return float(val)
    except ValueError:
        return None

def importar_sensor_data(csv_path):
    print(f"Criando tabelas caso elas não existam...")
    Base.metadata.create_all(bind=engine)
    
    print(f"Lendo o CSV {csv_path}...")
    session = SessionLocal()
    try:
        # previnir inserção duplicada
        if session.query(SensorData).first():
            print("A tabela do Sensor já tem dados. Pulando import...")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            chunk = []
            chunk_size = 10000
            total_inserted = 0
            
            for row in reader:
                created_at_str = row['created_at'].split('+')[0] if '+' in row['created_at'] else row['created_at']
                try:
                    created_at_dt = datetime.fromisoformat(created_at_str)
                except ValueError:
                    created_at_dt = None
                    
                sensor = SensorData(
                    id=int(row['id']),
                    created_at=created_at_dt,
                    z_rms_velocity_in_s=parse_float(row['z_rms_velocity_in_s']),
                    z_rms_velocity_mm_s=parse_float(row['z_rms_velocity_mm_s']),
                    temperature_f=parse_float(row['temperature_f']),
                    temperature_c=parse_float(row['temperature_c']),
                    x_rms_velocity_in_s=parse_float(row['x_rms_velocity_in_s']),
                    x_rms_velocity_mm_s=parse_float(row['x_rms_velocity_mm_s']),
                    z_peak_acceleration_g=parse_float(row['z_peak_acceleration_g']),
                    x_peak_acceleration_g=parse_float(row['x_peak_acceleration_g']),
                    z_peak_vel_comp_freq_hz=parse_float(row['z_peak_vel_comp_freq_hz']),
                    x_peak_vel_comp_freq_hz=parse_float(row['x_peak_vel_comp_freq_hz']),
                    z_rms_acceleration_g=parse_float(row['z_rms_acceleration_g']),
                    x_rms_acceleration_g=parse_float(row['x_rms_acceleration_g']),
                    z_kurtosis=parse_float(row['z_kurtosis']),
                    x_kurtosis=parse_float(row['x_kurtosis']),
                    z_crest_factor=parse_float(row['z_crest_factor']),
                    x_crest_factor=parse_float(row['x_crest_factor']),
                    z_peak_velocity_in_s=parse_float(row['z_peak_velocity_in_s']),
                    z_peak_velocity_mm_s=parse_float(row['z_peak_velocity_mm_s']),
                    x_peak_velocity_in_s=parse_float(row['x_peak_velocity_in_s']),
                    x_peak_velocity_mm_s=parse_float(row['x_peak_velocity_mm_s']),
                    z_high_freq_rms_accel_g=parse_float(row['z_high_freq_rms_accel_g']),
                    x_high_freq_rms_accel_g=parse_float(row['x_high_freq_rms_accel_g']),
                    fault=row['fault'],
                    rpm=parse_float(row['rpm'])
                )
                chunk.append(sensor)
                
                if len(chunk) >= chunk_size:
                    session.bulk_save_objects(chunk)
                    session.commit()
                    total_inserted += len(chunk)
                    print(f"inseridos totais: {total_inserted} dados...")
                    chunk = []
            
            # insere o restante
            if chunk:
                session.bulk_save_objects(chunk)
                session.commit()
                total_inserted += len(chunk)
                print(f"Inseridos totais: {total_inserted} dados...")

        print("Import completo.")
    except Exception as e:
        session.rollback()
        print(f"Erro: {e}")
    finally:
        session.close()

def carregar_dados_bd():
    """
    Cria a conexão, carrega todos os dados do BD e retorna uma conexão com o Pandas.
    """
    print("Carregando dados do Banco de Dados...")
    session = SessionLocal()
    try:
        # pandas nativo para ler direto do banco, bypassando o ORM
        df = pd.read_sql(session.query(SensorData).statement, session.bind)
    finally:
        session.close()
        
    print("Dados carregados com sucesso!")
    return df

if __name__ == "__main__":
    csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'banner.csv'))
    importar_sensor_data(csv_file_path)
