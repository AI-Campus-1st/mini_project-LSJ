import os
import pymysql
from dotenv import load_dotenv
from collector.client import fetch_subway_time_data, fetch_flow_data
from collector.transform import transform_subway_time, transform_flow

# 프로젝트 루트의 .env 파일 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

def run_pipeline():
    # MariaDB 접속 정보 가져오기 (.env 또는 기본값)
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("PASSWORD", os.getenv("DB_PASSWORD", ""))
    db_host = os.getenv("HOST", os.getenv("DB_HOST", "localhost"))
    db_port = int(os.getenv("PORT", os.getenv("DB_PORT", "3306")))
    db_name = os.getenv("DB_NAME", "urban_traffic")

    print(f"MariaDB 연결 시도: {db_host}:{db_port} ({db_name})")

    # MariaDB 연결
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
            # 기존 테이블 재생성 (MariaDB 문법)
            cursor.execute("DROP TABLE IF EXISTS subway_time")
            cursor.execute("DROP TABLE IF EXISTS flow_data")
            cursor.execute("DROP TABLE IF EXISTS raw_living_pop")

            # 테이블 생성
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

            # 대시보드와 마트 쿼리가 바라보는 raw_living_pop 테이블도 함께 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw_living_pop (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    region_code VARCHAR(20),
                    base_date VARCHAR(20),
                    hour INT,
                    age_band VARCHAR(10),
                    pop_cnt FLOAT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            connection.commit()

            # 지하철 데이터 수집 및 적재
            print("지하철 데이터 수집 중...")
            subway_raw = fetch_subway_time_data(month_str="202510")
            if subway_raw:
                subway_transformed = transform_subway_time(subway_raw)
                if subway_transformed:
                    # 튜플 데이터 -> MariaDB 형식으로 삽입
                    insert_subway_query = """
                        INSERT INTO subway_time (stats_date, line_num, station_name, 시간, 승차인원, 하차인원)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.executemany(insert_subway_query, subway_transformed)
                    connection.commit()
                    print(f"지하철 데이터 {len(subway_transformed)}건 적재 완료.")

            # 2. 생활인구 데이터 수집 및 적재
            print("생활인구 데이터 수집 중...")
            flow_raw = fetch_flow_data(date_str="20251201")
            if flow_raw:
                flow_transformed = transform_flow(flow_raw)
                if flow_transformed:
                    insert_flow_query = """
                        INSERT INTO flow_data (base_date, signgu_code, signgu_name, total_pop)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.executemany(insert_flow_query, flow_transformed)
                    
                    # raw_living_pop샘플/수집 데이터 동기화 매핑
                    insert_raw_query = """
                        INSERT INTO raw_living_pop (region_code, base_date, hour, age_band, pop_cnt)
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    # flow_transformed 데이터 raw_living_pop 구조에 맞게 변환 후 적재
                    for r in flow_transformed:
                        cursor.execute(insert_raw_query, (r[1], r[0], 8, '20s', r[3]))
                        
                    connection.commit()
                    print(f"생활인구 데이터 {len(flow_transformed)}건 적재 완료.")

        print("[SUCCESS] MariaDB 파이프라인 수집 및 적재가 모두 완료되었습니다!")

    except Exception as e:
        print(f"[ERROR] 파이프라인 실행 중 오류 발생: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    run_pipeline()