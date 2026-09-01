import streamlit as st
import time
from datetime import date
from google import genai
import requests
import xml.etree.ElementTree as ET

# 1. 펌웨어의 전역 변수(글로벌 락) 역할: 서버 전체가 공유하는 메모리
@st.cache_resource
def get_server_state():
    return {"active_users": 0, "daily_api_calls": 0, "today": date.today()}

state = get_server_state()

# 날짜가 바뀌면 일일 한도 리셋
if state["today"] != date.today():
    state["daily_api_calls"] = 0
    state["today"] = date.today()

# (헤더 숨김 CSS 및 UI 텍스트 인풋 등 기존 설정 생략)
# ...

if st.button("분석 및 예상 🚀"):
    if stock_name:
        # [방어 1] 일일 API 호출 한도 차단 (예: 하루 50회)
        if state["daily_api_calls"] >= 50:
            st.error("🚨 오늘 서버에 할당된 무료 AI 분석 쿼터가 모두 소진되었습니다. 00시 이후 리셋됩니다.")
            st.stop() # 실행 즉시 중단
            
        # [방어 2] 새 탭 어뷰징 차단 (서버 전체 동시 대기자 3명으로 제한)
        if state["active_users"] >= 3:
            st.error("🔥 현재 AI 분석 대기자가 너무 많아 서버가 혼잡합니다. 잠시 후 다시 시도해주세요.")
            st.stop()

        # 분석 시작: 대기열 진입 (락 획득)
        state["active_users"] += 1
        
        try:
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # 5분(300초) 카운트다운 루프
            total_seconds = 300
            for i in range(total_seconds):
                remaining = total_seconds - i
                mins, secs = divmod(remaining, 60)
                status_text.warning(f"🔥 방대한 실시간 수급 및 차트 분석 중... 남은 시간 [ {mins:02d}:{secs:02d} ]")
                progress_bar.progress((i + 1) / total_seconds)
                time.sleep(1)
            
            status_text.success("✅ 분석 완료! 리포트를 생성합니다.")
            progress_bar.empty()
            
            with st.spinner("최종 리포트 화면 출력 중..."):
                # 실제 제미나이 API가 호출되는 시점에 일일 카운트 +1
                state["daily_api_calls"] += 1
                
                # (이후 기존의 뉴스 수집 및 제미나이 리포트 출력 코드 그대로 삽입)
                # ...
                
        finally:
            # 에러가 나거나 사용자가 창을 닫아도 반드시 대기열에서 해제 (락 반환)
            if state["active_users"] > 0:
                state["active_users"] -= 1
    else:
        st.warning("종목명을 먼저 입력해주세요!")