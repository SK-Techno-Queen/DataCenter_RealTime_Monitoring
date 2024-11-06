from google.colab import drive 
drive.mount('/content/drive')

import pandas as pd
from datetime import datetime, timedelta
import os
import fastavro

# 로그 데이터 생성
log_data = []
timestamp = datetime.now()

# 초기 값 설정
temperature = 27.0
humidity = 40
oxygen_level = 20.9
airflow = 3
power_usage = 275  # 초기 전력 사용량을 낮춰 정상 상태에서 시작
ups_temp = 33  # 초기 UPS 온도를 낮춰 정상 상태에서 시작
battery_health = "Good"
voltage_variation = "None"  # 초기 전압 변동을 안정적인 상태로 설정
smoke_level = 0.0
heat_sensor_trigger = "No"
sprinkler_status = "Active"

# 위험 점수 계산 함수 (조정된 임계값)
def get_score(log_entry):
    power_usage_score = 3 if log_entry["power_usage"] >= 315 else 2 if log_entry["power_usage"] >= 305 else 1 if log_entry["power_usage"] >= 295 else 0
    ups_temp_score = 3 if log_entry["ups_temp"] >= 45 else 2 if log_entry["ups_temp"] >= 40 else 1 if log_entry["ups_temp"] >= 35 else 0
    voltage_variation_score = 3 if log_entry["voltage_variation"] == "High" else 2 if log_entry["voltage_variation"] == "Medium" else 1 if log_entry["voltage_variation"] == "Low" else 0
    battery_health_score = 3 if log_entry["battery_health"] == "Poor" else 2 if log_entry["battery_health"] == "Fair" else 1 if log_entry["battery_health"] == "Good" else 0
    
    total_score = power_usage_score + ups_temp_score + voltage_variation_score + battery_health_score
    return total_score

# 위험 수준 분류 함수
def classify_level(total_score):
    if total_score >= 9:
        return "정전 발생"
    elif total_score >= 6:
        return "위험"
    elif total_score >= 3:
        return "경고"
    else:
        return "정상"

# 0.5초 간격으로 1분 동안 총 3600개의 로그 생성
for i in range(3600):
    # 각 단계별로 값 변화를 설정
    if i < 900:  # 정상 단계 유지
        power_usage += 0.01  # 소폭 증가
        ups_temp += 0.01
        battery_health = "Good"
        voltage_variation = "None"
    elif i < 1800:  # 경고 단계
        power_usage += 0.1
        ups_temp += 0.04
        voltage_variation = "Low" if i % 200 < 100 else "Medium"
        battery_health = "Good" if i % 200 < 100 else "Fair"
    elif i < 2700:  # 위험 단계
        power_usage += 0.3
        ups_temp += 0.06
        voltage_variation = "Medium" if i % 100 < 50 else "High"
        battery_health = "Fair" if i % 100 < 50 else "Poor"
    else:  # 정전 발생 단계
        power_usage += 0.5
        ups_temp += 0.1
        voltage_variation = "High"
        battery_health = "Poor"

    # 로그 엔트리 생성
    log_entry = {
        "data_id": i + 1,  # data_id는 1부터 시작하여 순차적으로 증가
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "temperature": round(temperature, 1),
        "humidity": round(humidity, 1),
        "oxygen_level": oxygen_level,
        "airflow": airflow,
        "power_usage": round(power_usage, 1),
        "ups_temp": round(ups_temp, 1),
        "battery_health": battery_health,
        "voltage_variation": voltage_variation,
        "smoke_level": round(smoke_level, 2),
        "heat_sensor_trigger": heat_sensor_trigger,
        "sprinkler_status": sprinkler_status
    }

    # 위험 점수 및 수준 분류
    total_score = get_score(log_entry)
    log_entry["level"] = classify_level(total_score)

    log_data.append(log_entry)
    timestamp += timedelta(seconds=0.5)

# CSV 파일 저장
directory = '/content/drive/My Drive/DataCenter_disaster'
csv_path = os.path.join(directory, 'data_center_log.csv')
if not os.path.exists(directory):
    os.makedirs(directory)

log_df = pd.DataFrame(log_data)
log_df.to_csv(csv_path, index=False)
print("CSV 파일이 DataCenter_disaster 폴더에 저장되었습니다.")

# CSV 파일 읽기 및 Avro 파일로 저장
df = pd.read_csv(csv_path)
avro_path = os.path.join(directory, 'data_center_log_with_level.avro')

schema = {
    "type": "record",
    "name": "DataCenterLog",
    "fields": [
        {"name": "data_id", "type": "int"},
        {"name": "timestamp", "type": "string"},
        {"name": "temperature", "type": "float"},
        {"name": "humidity", "type": "float"},
        {"name": "oxygen_level", "type": "float"},
        {"name": "airflow", "type": "int"},
        {"name": "power_usage", "type": "float"},
        {"name": "ups_temp", "type": "float"},
        {"name": "battery_health", "type": "string"},
        {"name": "voltage_variation", "type": "string"},
        {"name": "smoke_level", "type": "float"},
        {"name": "heat_sensor_trigger", "type": "string"},
        {"name": "sprinkler_status", "type": "string"},
        {"name": "level", "type": "string"}
    ]
}

with open(avro_path, 'wb') as out:
    fastavro.writer(out, schema, df.to_dict(orient='records'))

print("Avro 파일이 DataCenter_disaster 폴더에 저장되었습니다.")