import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client
import random

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def recommend_books(category, keyword):
    prompt = f"""
    [{category}] 장르에서 '{keyword}' 키워드를 주제로 한 책 10권을 추천해줘. 유명한 책보다는 다양한 책을 포함해줘. 간결하게 알려줘야하니 쪼금씩만 설명하고 문장 하나가 길어지면 중간에 띄어쓰기를 넣어.
    각 책은 다음 형식으로 출력해줘:
    제목 (저자)
    요약 설명 간단히
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"에러 발생: {e}"

def recommend_study_books(subject):
    prompt = f"""
    '{subject}' 과목에 대한 추천 문제집 5권을 알려줘. 간결하게 알려줘야하니 쪼금씩만 설명하고 문장 하나가 길어지면 중간에 띄어쓰기를 넣어.
    각 책은 다음 형식으로 출력해줘:
    제목 (출판사)
    설명 한 줄
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"에러 발생: {e}"

st.set_page_config(page_title="책 추천기", layout="centered")
st.markdown("<h2 style='text-align:center;'> AI 책 추천기 </h2>", unsafe_allow_html=True)

menu = st.radio(
    "원하는 메뉴를 선택하세요:",
    ["경제경영", "소설", "비문학", "문제집 추천", "리뷰쓰기", "리뷰 보기"],
    horizontal=True
)

if menu in ["경제경영", "소설", "비문학"]:
    keyword = st.text_input(f"'{menu}' 장르에서 원하는 키워드를 입력하세요")
    if keyword:
        with st.spinner("AI가 책을 추천 중입니다..."):
            result = recommend_books(menu, keyword)
        st.subheader("추천 결과")
        st.code(result, language='markdown')

elif menu == "문제집 추천":
    subject = st.text_input("어떤 과목의 문제집을 찾고 있나요? (예: 수학, 영어, 과학 등)")
    if subject:
        with st.spinner("AI가 문제집을 찾는 중입니다..."):
            result = recommend_study_books(subject)
        st.subheader("추천 문제집")
        st.code(result, language='markdown')

elif menu == "리뷰쓰기":
    st.subheader("책 리뷰 쓰기")
    title = st.text_input("책 제목")
    review = st.text_area("감상평")
    rating = st.slider("별점", 1, 5, 3)

    if st.button("리뷰 저장"):
        if title and review:
            try:
                response = supabase.table("reviews").insert({
                    "title": title,
                    "review": review,
                    "rating": rating
                }).execute()
                st.success("리뷰가 성공적으로 저장되었습니다.")
            except Exception as e:
                st.error(f"저장 실패: {e}")
        else:
            st.warning("책 제목과 감상평을 입력해주세요.")
elif menu == "리뷰 보기":
    try:
        response = supabase.table("reviews").select("*").execute()
        reviews = response.data

        if reviews:
            random_review = random.choice(reviews)

            st.markdown(f"""
            ### {random_review['title']}
            **별점:** {'⭐' * random_review['rating']}  
            **감상평:**  
            {random_review['review']}
            """)
            if st.button("다른 리뷰 보기"):
                st.rerun()
        else:
            st.info("아직 등록된 리뷰가 없습니다.")
    except Exception as e:
        st.error(f"리뷰를 불러오지 못했습니다: {e}")

st.markdown("---")

#st.markdown("<div style='text-align:center;'><small>Google 광고 자리</small></div>", unsafe_allow_html=True)