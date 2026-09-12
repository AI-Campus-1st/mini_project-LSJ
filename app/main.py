import streamlit as st
import pandas as pd
import plotly.express as px
from repository import get_flow_df, get_subway_time_df, get_commute_pressure_df

st.set_page_config(page_title="Urban Traffic Dashboard", layout="wide")

st.title("서울시 생활인구 및 교통 압박 분석 리포트")
st.markdown("> **핵심 요약**: 서울시의 생활인구와 교통 혼잡은 특정 도심·업무 지구에 심각하게 편중되어 있으며, 구조적 불균형을 해소하기 위한 대책이 필요합니다.")

tabs = st.tabs([
    "1. 도심·강남권 인구 편중", 
    "2. 주거·업무 불균형 진단", 
    "3. 출퇴근 승하차 압박 TOP 10"
])

with tabs[0]:
    st.subheader("도심·강남권에 생활인구가 극심하게 편중되어 있습니다")
    st.caption("💡 **인사이트**: 상위 3개 자치구가 전체 생활인구의 상당 부분을 점유하고 있으며, 외곽 지역과의 격차가 매우 뚜렷합니다.")
    
    df_flow = get_flow_df()
    chart_df = df_flow[df_flow['region_code'] != '11000'] if 'region_code' in df_flow.columns else df_flow
        
    fig1 = px.bar(
        chart_df,
        x='region_name',
        y='avg_daily_pop',
        labels={'region_name': '자치구', 'avg_daily_pop': '평균 일일 생활인구 (명)'},
        color_discrete_sequence=['#8AB6D6']
    )
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True, key="bar_region_pop")

with tabs[1]:
    st.subheader("주거 인구 대비 업무 기능이 과도하게 집중된 지역이 존재합니다")
    st.caption("**인사이트**: 주거인구 규모에 비해 생활인구가 비정상적으로 높은 지역은 출퇴근 시간대 교통 수용 한계에 직면할 위험이 큽니다.")
    
    df_pressure = get_commute_pressure_df()
    chart_df2 = df_pressure[df_pressure['region_code'] != '11000'] if 'region_code' in df_pressure.columns else df_pressure
        
    fig2 = px.scatter(
        chart_df2,
        x='resident_pop',
        y='avg_daily_pop',
        text='region_name',
        labels={'resident_pop': '주거인구 (명)', 'avg_daily_pop': '생활인구 (명)'}
    )
    fig2.update_traces(textposition='top center')
    st.plotly_chart(fig2, use_container_width=True, key="scatter_pressure")

with tabs[2]:
    st.subheader("출퇴근 시간대 특정 역사의 승하차 압박이 임계점에 달했습니다")
    st.caption("**인사이트**: 승하차 총량이 집중되는 상위 역사 주변은 환승 체계 개선 및 집중 배차 등 우선적 개입이 필요합니다.")
    
    df_subway = get_subway_time_df()
    if not df_subway.empty:
        df_subway['total_traffic'] = df_subway['ride_count'] + df_subway['alight_count']
        top10_subway = df_subway.groupby(['line_num', 'station_name'], as_index=False)['total_traffic'].sum()
        top10_subway = top10_subway.sort_values(by='total_traffic', ascending=False).head(10)
        st.dataframe(top10_subway, use_container_width=True)
    else:
        st.info("표시할 데이터가 없습니다.")

# 데이터 한계 명시 영역 
st.markdown("---")
st.markdown(
    "<p style='font-size: 12px; color: gray; text-align: center;'>"
    "⚠️ <b>데이터 한계 안내</b>: 본 대시보드의 생활인구 및 지하철 데이터는 표본 조사 및 월별 집계 특성상 "
    "실시간 돌발 상황이나 미세한 시간대별 변동 폭을 온전히 반영하지 못할 수 있으며, 통계 추정 과정에서 오차가 존재할 수 있습니다."
    "</p>", 
    unsafe_allow_html=True
)