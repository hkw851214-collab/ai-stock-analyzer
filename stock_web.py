import streamlit as st
import requests
import time
from google import genai
import xml.etree.ElementTree as ET

# 웹페이지 기본 설정 및 전체화면 버튼/헤더/푸터 강제 숨김 CSS
st.set_page_config(page_title="AI 주식 분석기", page_icon="📈", layout="centered")

hide_streamlit_style = """
<style>
/* 전체화면(Full screen) 버튼 강제 삭제 */
button[title="View fullscreen"] {display: none !important;}
.st-emotion-cache-1rqz50n {display: none !important;}
/* 우측 상단 기본 헤더 및 메뉴바 제거 */
header {visibility: hidden !important;}
/* 하단 Streamlit 워터마크 제거 */
footer {visibility: hidden !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

API_KEY = st.secrets["GEMINI_API_KEY"]

st.title("📈 실시간 AI 주식 심층 분석기")
st.markdown("궁금한 종목명을 입력하시면 AI가 실시간 뉴스를 분석하여 펀더멘털 및 차트 전망을 제시합니다.")

# 종목 입력 칸
stock_name = st.text_input("🔍 분석할 종목명을 입력하세요 (예: 삼성전자, 에코프로)")

# [분석 및 예상] 버튼을 눌렀을 때 실행되는 로직
if st.button("분석 및 예상 🚀"):
    if stock_name:
        # 1차 로딩 바 (방문자 체류시간 확보용)
        with st.spinner(f"'{stock_name}' 실시간 수급 데이터 및 뉴스 크롤링 중... (약 10초 소요)"):
            time.sleep(4) # 체류시간 강제 지연
            
            news_items = []
            try:
                res = requests.get(f"https://news.google.com/rss/search?q={stock_name}+특징주+공시+전망&hl=ko&gl=KR&ceid=KR:ko", headers={'User-Agent': 'Mozilla/5.0'})
                for item in ET.fromstring(res.content).findall('./channel/item')[:4]:
                    t = item.find('title').text
                    news_items.append(t.rsplit(' - ', 1)[0].strip() if ' - ' in t else t.strip())
            except: pass
            
            news_text = "\n".join([f"- {n}" for n in news_items]) if news_items else "최근 특별한 뉴스가 없습니다."

        # 2차 로딩 바
        with st.spinner("AI가 기업 재무구조 파악 및 향후 차트 방향성을 분석하고 있습니다..."):
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
                ai_result = client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text
            except Exception as e:
                ai_result = "오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        
        # 결과 출력
        st.success("✨ 분석이 완료되었습니다!")
        st.subheader(f"[{stock_name}] AI 심층 리포트")
        if news_items:
            with st.expander("📰 참고한 뉴스 헤드라인 보기"):
                for n in news_items: st.write(f"- {n}")
        st.markdown(ai_result)
    else:
        st.warning("종목명을 먼저 입력해주세요!")