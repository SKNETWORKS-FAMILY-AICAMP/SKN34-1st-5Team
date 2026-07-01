import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import streamlit as st
from src.service.FAQService import get_faq  # 파일 받으면 주석 풀기
from src.type.manufacturer import Manufacturer
# from src.type.faq_item import FAQItem
from src.type.page import Page


# 화면 설정
st.set_page_config(layout="wide")
st.title("🚗 자동차 기업 FAQ")
st.caption("궁금한 내용을 제조사별로 검색해보세요")
st.divider()



# 제조사 선택
manufacturer_options = {"현대": Manufacturer.HYUNDAI, "기아": Manufacturer.KIA}
selected_name = st.selectbox("제조사 선택", list(manufacturer_options.keys()))
selected_manufacturer = manufacturer_options[selected_name]

# 페이지 번호 기억
if "faq_page" not in st.session_state:
    st.session_state.faq_page = 1

# 데이터 !!! 생김
result = get_faq(page=st.session_state.faq_page, size=5, manufacturer=selected_manufacturer)

st.divider()

# FAQ 목록 출력
if not result.item:
    st.warning("검색 결과가 없습니다.")
else:
    for faq in result.item:
        with st.expander(f"❓ [{faq.category}] {faq.question}"):
            st.write(faq.answer)

    st.divider()


# 이전/다음 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀ 이전", use_container_width=True) and st.session_state.faq_page > 1:
            st.session_state.faq_page -= 1
            st.rerun()
    with col2:
        st.markdown(
            f"<p style='text-align:center;'>{st.session_state.faq_page} / {result.total_page} 페이지</p>",
            unsafe_allow_html=True,
        )
    with col3:
        if st.button("다음 ▶", use_container_width=True) and st.session_state.faq_page < result.total_page:
            st.session_state.faq_page += 1
            st.rerun()