import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

FLOW_KEY = os.getenv("FLOW_KEY")
SUBWAY_KEY = os.getenv("SUBWAY_KEY")

if not FLOW_KEY or not SUBWAY_KEY:
    raise ValueError(".env 파일에서 API 키를 찾을 수 없습니다. 키 설정을 확인하세요.")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "urban_traffic.db"))