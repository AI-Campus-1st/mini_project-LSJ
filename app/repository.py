import os
import pandas as pd
import pymysql
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", os.getenv("HOST", "localhost")),
        port=int(os.getenv("DB_PORT", os.getenv("PORT", 3306))),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", os.getenv("PASSWORD", "")),
        database=os.getenv("DB_NAME", "urban_traffic"),
        charset="utf8mb4"
    )

def _apply_region_mapping(df):
    region_mapping = {
        '11110': '종로구', '11140': '중구', '11170': '용산구', '11200': '성동구',
        '11215': '광진구', '11230': '동대문구', '11245': '중랑구', '11260': '성북구',
        '11290': '강북구', '11305': '도봉구', '11320': '노원구', '11350': '은평구',
        '11380': '서대문구', '11410': '마포구', '11440': '양천구', '11470': '강서구',
        '11500': '구로구', '11530': '금천구', '11545': '영등포구', '11560': '동작구',
        '11590': '관악구', '11620': '서초구', '11650': '강남구', '11680': '강남구', 
        '11710': '송파구', '11740': '강동구', '11000': '서울시전체'
    }
    
    if 'region_code' in df.columns:
        def get_name(val):
            if pd.isna(val): 
                return "기타"
            val_str = str(val).split('.')[0].strip()
            prefix = val_str[:5] if len(val_str) >= 5 else val_str
            return region_mapping.get(prefix, val_str)
            
        # 기존 region_code는 유지하고, 시각화용 'region_name' 컬럼을 별도로 생성
        df['region_name'] = df['region_code'].apply(get_name)
        
    return df

def get_subway_time_df():
    conn = get_connection()
    query = "SELECT stats_date AS base_ymd, 시간 AS time_slot, line_num, station_name, 승차인원 AS ride_count, 하차인원 AS alight_count FROM subway_time"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_flow_df():
    conn = get_connection()
    query = "SELECT * FROM mart_region_monthly"
    df = pd.read_sql(query, conn)
    conn.close()
    return _apply_region_mapping(df)

def get_commute_pressure_df():
    conn = get_connection()
    try:
        query = "SELECT * FROM mart_region_monthly"
        df = pd.read_sql(query, conn)
    except:
        df = get_flow_df()
    conn.close()
    
    df = _apply_region_mapping(df)
    
    if 'pressure' not in df.columns:
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            df['pressure'] = df[numeric_cols[0]]
        else:
            df['pressure'] = 0
            
    return df