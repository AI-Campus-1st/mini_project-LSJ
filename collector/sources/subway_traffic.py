import os
import requests
import pymysql
from dotenv import load_dotenv

load_dotenv()

def collect_subway_traffic():
    api_key = os.getenv("SUBWAY_KEY")
    if not api_key:
        print("API 키가 설정되지 않았습니다.")
        return

    conn = pymysql.connect(
        host=os.getenv("HOST", "localhost"),
        port=int(os.getenv("PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("PASSWORD", ""),
        database=os.getenv("DB_NAME", "urban_traffic"),
        charset="utf8mb4"
    )

    start_idx = 1
    step = 1000
    total_inserted = 0
    target_date = "20260901"

    print(f"실제 지하철 원본 데이터 수집 시작 (조회 일자: {target_date})...")

    while True:
        end_idx = start_idx + step - 1
        url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CardSubwayStatsNew/{start_idx}/{end_idx}/{target_date}"
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"통신 실패: {response.status_code}")
            break

        data = response.json()
        
        if "RESULT" in data:
            print(f"API 메시지: {data['RESULT'].get('MESSAGE')}")
            break

        if "CardSubwayStatsNew" not in data or "row" not in data["CardSubwayStatsNew"]:
            break

        rows = data["CardSubwayStatsNew"]["row"]
        if not rows:
            break

        records = []
        for item in rows:
            line = str(item.get("SBWY_ROUT_LN_NM", ""))
            station = str(item.get("SBWY_STNS_NM", ""))
            ride = float(item.get("GTON_TNOPE", 0))
            alight = float(item.get("GTOFF_TNOPE", 0))
            
            records.append((target_date, line, station, ride, alight))

        if records:
            query = """
                INSERT INTO subway_time_table (base_ymd, line_num, station_name, ride_count, alight_count)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                ride_count=VALUES(ride_count), alight_count=VALUES(alight_count)
            """
            with conn.cursor() as cursor:
                cursor.executemany(query, records)
                conn.commit()
            total_inserted += len(rows)

        start_idx += step
        if len(rows) < step:
            break

    conn.close()
    print(f"지하철 실제 원본 데이터 적재 완료: 총 {total_inserted}개 역 정보가 정상 저장되었습니다.")

if __name__ == "__main__":
    collect_subway_traffic()