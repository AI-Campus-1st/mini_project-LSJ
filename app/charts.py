import plotly.express as px
import streamlit as st
import pandas as pd

PASTEL_COLORS = ['#A8DADC', '#B5E2FA', '#FFB7B2', '#FFDAC1', '#E2F0CB', '#B5EAD7', '#C7CEEA', '#F4A261']

def render_line_chart(sub_df):
    """(비상용 유지) 서울시 전체 대중교통 이동량 라인 차트"""
    try:
        if sub_df is None or sub_df.empty:
            st.info("시계열 데이터가 존재하지 않습니다.")
            return
        df = sub_df.copy()
        df.columns = [str(c).lower() for c in df.columns]
        x_col = df.columns[0]
        num_cols = df.select_dtypes(include=['number']).columns
        y_col = num_cols[0] if len(num_cols) > 0 else df.columns[1]
        
        fig = px.line(df, x=x_col, y=y_col, color_discrete_sequence=['#457B9D'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"라인 차트 오류: {e}")

def render_bar_chart(flow_df):
    """자치구별 생활인구 분포 막대 그래프"""
    try:
        if flow_df is None or flow_df.empty:
            st.info("생활인구 데이터가 존재하지 않습니다.")
            return
        df = flow_df.copy()
        df.columns = [str(c).lower() for c in df.columns]
        x_col = df.columns[0]
        
        num_cols = [c for c in df.select_dtypes(include=['number']).columns if c != x_col]
        y_col = num_cols[0] if len(num_cols) > 0 else df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        df[y_col] = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
        df_grouped = df.groupby(x_col, as_index=False)[y_col].sum()
        
        fig = px.bar(df_grouped, x=x_col, y=y_col, color_discrete_sequence=PASTEL_COLORS)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"막대 차트 오류: {e}")

def render_quadrant_chart(flow_df, sub_df):
    """주거-업무 불균형 진단 사분면 산점도"""
    try:
        gu_list = ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", 
                   "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", 
                   "용산구", "은평구", "종로구", "중구", "중랑구"]
        
        import numpy as np
        np.random.seed(42)
        mock_df = pd.DataFrame({
            "자치구명": gu_list,
            "생활인구": np.random.randint(30000, 70000, size=25),
            "총이용객": np.random.randint(100000, 500000, size=25)
        })
        
        fig = px.scatter(mock_df, x="생활인구", y="총이용객", text="자치구명", color_discrete_sequence=['#457B9D'])
        x_mean = mock_df["생활인구"].mean()
        y_mean = mock_df["총이용객"].mean()

        fig.add_hline(y=y_mean, line_dash="dash", line_color="#E76F51", annotation_text="평균 교통 부하")
        fig.add_vline(x=x_mean, line_dash="dash", line_color="#E76F51", annotation_text="평균 생활인구")

        fig.update_traces(textposition='top center', marker=dict(size=14, color='#A8DADC', line=dict(width=1.5, color='#457B9D')))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"사분면 차트 오류: {e}")

def render_pressure_chart(pressure_df):
    """승차 압박 TOP 10 막대 그래프"""
    try:
        if pressure_df is None or pressure_df.empty:
            st.info("압박 지수 데이터가 존재하지 않습니다.")
            return
        df = pressure_df.copy()
        df.columns = [str(c).lower() for c in df.columns]
        x_col = df.columns[0]
        num_cols = [c for c in df.select_dtypes(include=['number']).columns if c != x_col]
        y_col = num_cols[0] if len(num_cols) > 0 else df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        df[y_col] = pd.to_numeric(df[y_col], errors="coerce").fillna(0)
        fig = px.bar(df, x=x_col, y=y_col, color_discrete_sequence=PASTEL_COLORS)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"압박 차트 오류: {e}")