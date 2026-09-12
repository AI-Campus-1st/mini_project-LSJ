def transform_subway_time(raw_list):
    transformed = []
    for item in raw_list:
        try:
            stats_date = str(item.get("USE_MM", ""))
            line_num = str(item.get("SBWY_ROUT_LN_NM", ""))
            station_name = str(item.get("STTN", ""))
            
            for k, v in item.items():
                if "GET_ON_NOPE" in k.upper():
                    hour_part = k.split("_")[1] if "_" in k else "Total"
                    try:
                        ride = int(float(v or 0))
                    except:
                        ride = 0
                    
                    off_key = k.replace("GET_ON_NOPE", "GET_OFF_NOPE")
                    try:
                        alight = int(float(item.get(off_key, 0) or 0))
                    except:
                        alight = 0
                    
                    transformed.append((
                        stats_date,
                        line_num,
                        station_name,
                        hour_part,
                        ride,
                        alight
                    ))
        except Exception:
            continue
            
    return transformed

def transform_flow(raw_list):
    transformed = []
    for item in raw_list:
        try:
            # 다양한 API 스키마 키 변형에 대응하는 유연한 매핑
            base_date = str(
                item.get("STD_YM") or item.get("BASE_DATE") or 
                item.get("STDR_DE") or item.get("STDR_DE_ID") or ""
            )
            signgu_code = str(
                item.get("SIGNGU_CODE") or item.get("SIGNGU_CD") or 
                item.get("CODE") or ""
            )
            signgu_name = str(
                item.get("SIGNGU_NM") or item.get("SIGNGU_NAME") or 
                item.get("NAME") or ""
            )
            
            total_pop = 0.0
            for pop_key in ["TOT_LVPOP_CO", "POP_CNT", "POP", "TOTAL_POP"]:
                if pop_key in item and item[pop_key] is not None:
                    try:
                        total_pop = float(item[pop_key])
                        break
                    except:
                        pass
            
            # 값이 비어있을 경우 순서 기반 대체 처리
            if not base_date and len(item) > 0:
                base_date = str(list(item.values())[0])
            if not signgu_code and len(item) > 1:
                signgu_code = str(list(item.values())[1])

            transformed.append((base_date, signgu_code, signgu_name, total_pop))
        except Exception:
            continue
    return transformed