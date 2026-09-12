import os
import pymysql
from dotenv import load_dotenv
from collector.client import fetch_subway_time_data, fetch_flow_data
from collector.transform import transform_subway_time, transform_flow

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

def run_pipeline():
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("PASSWORD", os.getenv("DB_PASSWORD", ""))
    db_host = os.getenv("HOST", os.getenv("DB_HOST", "localhost"))
    db_port = int(os.getenv("PORT", os.getenv("DB_PORT", "3306")))
    db_name = os.getenv("DB_NAME", "urban_traffic")

    print(f"MariaDB 연결 중: {db_host}:{db_port} ({db_name})")

    connection = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # 테이블 초기화 및 재생성
            cursor.execute("DROP TABLE IF EXISTS subway_time")
            cursor.execute("DROP TABLE IF EXISTS flow_data")
            cursor.execute("DROP TABLE IF EXISTS raw_living_pop")

            cursor.execute("""
                CREATE TABLE subway_time (
                    stats_date VARCHAR(20), 
                    line_num VARCHAR(50), 
                    station_name VARCHAR(100), 
                    시간 VARCHAR(20), 
                    승차인원 FLOAT, 
                    하차인원 FLOAT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            cursor.execute("""
                CREATE TABLE flow_data (
                    base_date VARCHAR(20), 
                    signgu_code VARCHAR(20), 
                    signgu_name VARCHAR(50), 
                    total_pop FLOAT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            cursor.execute("""
                CREATE TABLE raw_living_pop (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    region_code VARCHAR(20),
                    base_date VARCHAR(20),
                    hour INT,
                    age_band VARCHAR(10),
                    pop_cnt FLOAT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            connection.commit()

            # 1. 지하철 데이터 수집 및 적재
            print("지하철 데이터 수집 중...")
            subway_raw = fetch_subway_time_data(month_str="202510")
            if subway_raw:
                subway_transformed = transform_subway_time(subway_raw)
                if subway_transformed:
                    insert_subway_query = """
                        INSERT INTO subway_time (stats_date, line_num, station_name, 시간, 승차인원, 하차인원)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(insert_subway_query, subway_transformed)
                    connection.commit()
                    print(f"지하철 데이터 {len(subway_transformed)}건 적재 완료.")

            # 2. 순수 API 생활인구 데이터 수집 및 적재
            print("생활인구 데이터 수집 중...")
            flow_raw = fetch_flow_data(date_str="20251201")
            
            insert_flow_query = "INSERT INTO flow_data (base_date, signgu_code, signgu_name, total_pop) VALUES (%s, %s, %s, %s)"
            insert_raw_query = "INSERT INTO raw_living_pop (region_code, base_date, hour, age_band, pop_cnt) VALUES (%s, %s, %s, %s, %s)"

            flow_transformed = transform_flow(flow_raw) if flow_raw else []
            
            if flow_transformed:
                for r in flow_transformed:
                    b_date = str(r[0]) if len(r) > 0 and r[0] is not None else ""
                    s_code = str(r[1]) if len(r) > 1 and r[1] is not None else ""
                    s_name = str(r[2]) if len(r) > 2 and r[2] is not None else ""
                    pop_val = float(r[3]) if len(r) > 3 and r[3] is not None else 0.0

                    cursor.execute(insert_flow_query, (b_date, s_code, s_name, pop_val))
                    cursor.execute(insert_raw_query, (s_code, b_date, 8, '20s', pop_val))
                
                connection.commit()
                print(f"순수 API 생활인구 데이터 {len(flow_transformed)}건 적재 완료.")
            else:
                print("수집된 생활인구 API 데이터가 없습니다.")

        print("[SUCCESS] 순수 API 기반 파이프라인 적재 완료!")

    except Exception as e:
        print(f"[ERROR] 파이프라인 실행 중 오류 발생: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    run_pipeline()