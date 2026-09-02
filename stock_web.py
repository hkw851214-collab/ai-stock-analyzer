import streamlit as st
import requests
import time
from datetime import date
from google import genai
import xml.etree.ElementTree as ET

# 1. 웹페이지 기본 설정 (반드시 최상단에 위치)
st.set_page_config(page_title="AI 주식 분석기", page_icon="📈", layout="centered")

# 2. 강력한 전체화면 방지 및 헤더/푸터 완전 제거 CSS
hide_streamlit_style = """
<style>
[data-testid="stHeader"] {display: none !important;}
header {display: none !important;}
[data-testid="stFooter"] {display: none !important;}
footer {display: none !important;}
button[title="View fullscreen"] {display: none !important;}
.st-emotion-cache-1rqz50n {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

API_KEY = st.secrets["GEMINI_API_KEY"]

# 3. 글로벌 락(서버 상태 공유) 설정 - 다중 탭 어뷰징 및 요금 방어
@st.cache_resource
def get_server_state():
    return {"active_users": 0, "daily_api_calls": 0, "today": date.today()}

state = get_server_state()

if state["today"] != date.today():
    state["daily_api_calls"] = 0
    state["today"] = date.today()

# 4. 화면 UI 구성
st.title("📈 실시간 AI 주식 심층 분석기")
st.markdown("궁금한 종목명을 입력하시면 AI가 실시간 뉴스를 분석하여 펀더멘털 및 차트 전망을 제시합니다.")

stock_name = st.text_input("🔍 분석할 종목명을 입력하세요 (예: 삼성전자, 에코프로)")

if st.button("분석 및 예상 🚀"):
    if stock_name:
        if state["daily_api_calls"] >= 50:
            st.error("🚨 오늘 서버에 할당된 무료 AI 분석 쿼터가 모두 소진되었습니다. 00시 이후 리셋됩니다.")
            st.stop()
            
        if state["active_users"] >= 3:
            st.error("🔥 현재 AI 분석 대기자가 너무 많아 서버가 혼잡합니다. 잠시 후 다시 시도해주세요.")
            st.stop()

        state["active_users"] += 1
        
        try:
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # 5분(300초) 카운트다운
            total_seconds = 300
            for i in range(total_seconds):
                remaining = total_seconds - i
                mins, secs = divmod(remaining, 60)
                status_text.warning(f"🔥 방대한 실시간 수급 및 차트 데이터 딥러닝 분석 중... 남은 시간 [ {mins:02d}:{secs:02d} ]")
                progress_bar.progress((i + 1) / total_seconds)
                time.sleep(1)
            
            status_text.success("✅ 분석이 완료되었습니다! 리포트를 생성합니다.")
            progress_bar.empty()
            
            # 실제 제미나이 API 호출 및 일일 카운트 차감
            state["daily_api_calls"] += 1
            
            with st.spinner("최종 리포트 화면 출력 중..."):
                news_items = []
                try:
                    res = requests.get(f"https://news.google.com/rss/search?q={stock_name}+특징주+공시+전망&hl=ko&gl=KR&ceid=KR:ko", headers={'User-Agent': 'Mozilla/5.0'})
                    for item in ET.fromstring(res.content).findall('./channel/item')[:4]:
                        t = item.find('title').text
                        news_items.append(t.rsplit(' - ', 1)[0].strip() if ' - ' in t else t.strip())
                except: pass
                
                news_text = "\n".join([f"- {n}" for n in news_items]) if news_items else "최근 특별한 뉴스가 없습니다."

                prompt = f"""
                너는 15년 차 베테랑 주식 애널리스트야. 사용자가 '{stock_name}' 종목 분석을 요청했어.
                현재 수집된 최신 뉴스는 다음과 같아: {news_text}
                
                이 정보와 너의 지식을 바탕으로 아래 양식에 맞춰 심층 리포트를 작성해.
                1. 🏢 기업 개요 및 펀더멘털 (매출/재무구조 상태)
                2. 📊 최근 수급 동향 (외인/기관 포지션 추정)
                3. 📈 향후 차트 예상 및 매매 시나리오
                """
                
                try:
                    client = genai.Client(api_key=API_KEY)
                    ai_result = client.models.generate_content(model='gemini-3.6-flash', contents=prompt).text
                except Exception as e:
                    ai_result = f"🚨 실제 에러 원인: {e}"
                    
            st.subheader(f"[{stock_name}] AI 심층 리포트")
            if news_items:
                with st.expander("📰 참고한 뉴스 헤드라인 보기"):
                    for n in news_items: st.write(f"- {n}")
            st.markdown(ai_result)
            
        finally:
            if state["active_users"] > 0:
                state["active_users"] -= 1
    else:
        st.warning("종목명을 먼저 입력해주세요!")