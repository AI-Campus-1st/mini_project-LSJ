import streamlit as st

def render_header():
    st.title("서울시 생활인구 및 시간대별 지하철 혼잡도 대시보드")
    st.markdown("---")
    st.info(" **핵심 분석 질문**: 주간 생활인구 집중 지역과 시간대별 지하철 승하차 집중 거점을 연계하여 출퇴근 혼잡 리스크 분석")