import requests
from collector.config import SUBWAY_KEY, FLOW_KEY

def fetch_subway_time_data(month_str="202510"):
    all_data = []
    start = 1
    step = 1000
    while True:
        end = start + step - 1
        url = f"http://openAPI.seoul.go.kr:8088/{SUBWAY_KEY}/json/CardSubwayTime/{start}/{end}/{month_str}"
        print(f"[API Request] URL: {url}")
        try:
            res = requests.get(url)
            data = res.json()
            print(f"[API Response Raw]: {str(data)[:200]}...") # 응답 앞부분 출력
            
            if "CardSubwayTime" in data:
                rows = data["CardSubwayTime"].get("row", [])
                print(f"[API Success] 가져온 지하철 데이터 개수: {len(rows)}건")
                if not rows: break
                all_data.extend(rows)
                if len(rows) < step: break
                start += step
            else:
                print(f"[API Error Message]: {data}")
                break
        except Exception as e:
            print(f"[API Exception]: {e}")
            break
    return all_data

def fetch_flow_data(date_str="20251201"):
    all_data = []
    start = 1
    step = 1000
    while True:
        end = start + step - 1
        url = f"http://openAPI.seoul.go.kr:8088/{FLOW_KEY}/json/SPOP_DAILYSUM_JACHI/{start}/{end}/{date_str}"
        try:
            res = requests.get(url)
            data = res.json()
            if "SPOP_DAILYSUM_JACHI" in data:
                rows = data["SPOP_DAILYSUM_JACHI"].get("row", [])
                if not rows: break
                all_data.extend(rows)
                if len(rows) < step: break
                start += step
            else:
                break
        except:
            break
    return all_data