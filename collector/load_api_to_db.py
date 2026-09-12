import os
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

def fetch_and_save_all_api_data():
    service_key = os.getenv("SUBWAY_KEY") or os.getenv("SEOUL_API_KEY")
    
    if not service_key:
        print("오류: .env 파일에 'SUBWAY_KEY'가 설정되어 있지 않습니다.")
        return
        
    target_ym = "202601" 
    all_rows = []
    page_size = 1000
    start_idx = 1
    
    print("API 전체 데이터 수집 시작...")
    
    while True:
        end_idx = start_idx + page_size - 1
        url = f"http://openapi.seoul.go.kr:8088/{service_key}/json/CardSubwayTime/{start_idx}/{end_idx}/{target_ym}"
        
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200:
                print(f"API 응답 에러 (코드: {response.status_code})")
                break
                
            try:
                data = response.json()
            except Exception:
                print(f"서버가 JSON이 아닌 응답을 반환했습니다.")
                break
            
            items = []
            if "CardSubwayTime" in data:
                items = data.get("CardSubwayTime", {}).get("row", [])
            elif "RESULT" in data:
                print(f"API 서버 메시지: {data.get('RESULT', {}).get('MESSAGE')}")
                break
            elif isinstance(data, list):
                items = data
                
            if not items:
                break
                
            all_rows.extend(items)
            print(f"데이터 수집 중... 누적 데이터: {len(all_rows)}건")
            
            if len(items) < page_size:
                break
                
            start_idx += page_size
            
        except Exception as e:
            print(f"수집 중 예외 발생: {e}")
            break
            
        if start_idx > 50000:
            break
            
    if not all_rows:
        print("수집된 데이터가 없습니다.")
        return
        
    df = pd.DataFrame(all_rows)
    df.columns = [str(c).strip() for c in df.columns]
    
    # 시간대별 분리
    long_data = []
    hours = list(range(4, 24)) + list(range(0, 4))
    
    for _, r in df.iterrows():
        use_mm = str(r.get('USE_MON', target_ym))
        line_nm = str(r.get('SBWY_ROUT_LN_NM', ''))
        sttn = str(r.get('STTN_NM', r.get('STTN', '')))
        
        for h in hours:
            if h == 23:
                t_key = "23~00"
            elif h == 3:
                t_key = "03~04"
            elif h < 9:
                t_key = f"0{h}~0{h+1}"
            elif h == 9:
                t_key = f"09~10"
            else:
                t_key = f"{h}~{h+1}"
                
            on_col = f"HR_{h}_GET_ON_NOPE"
            off_col = f"HR_{h}_GET_OFF_NOPE"
            
            on_val = pd.to_numeric(r.get(on_col, 0), errors='coerce')
            off_val = pd.to_numeric(r.get(off_col, 0), errors='coerce')
            
            if pd.isna(on_val): on_val = 0.0
            if pd.isna(off_val): off_val = 0.0
            
            long_data.append({
                'base_ymd': use_mm,
                'time_slot': t_key,
                'SBWY_ROUT_LN_NM': line_nm,
                'STTN': sttn,
                'ride_count': on_val,
                'alight_count': off_val
            })
            
    final_df = pd.DataFrame(long_data)

    # DB 연결 설정
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("PASSWORD", os.getenv("DB_PASSWORD", ""))
    db_host = os.getenv("HOST", os.getenv("DB_HOST", "localhost"))
    db_port = os.getenv("PORT", os.getenv("DB_PORT", "3306"))
    db_name = os.getenv("DB_NAME", "urban_traffic")
    
    engine_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    engine = create_engine(engine_url)

    # 적재 실행 
    try:
        final_df.to_sql(name="subway_time_table", con=engine, if_exists="replace", index=False)
        print(f"총 {len(final_df)}건의 시간대별 상세 데이터가 MariaDB에 완벽하게 적재되었습니다!")
    except Exception as load_err:
        print(f"데이터 적재 중 오류 발생: {load_err}")

if __name__ == "__main__":
    fetch_and_save_all_api_data()