import json
import os
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="나만의 디지털 서재", page_icon="📚", layout="wide"
)

DATA_FILE = "books.json"


# 데이터 로드 함수
def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return []


# 데이터 저장 함수
def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# 세션 상태 초기화
if "books" not in st.session_state:
  st.session_state.books = load_data()

# 사이드바 메뉴 구성
st.sidebar.title("📚 독서 아카이브")
menu = st.sidebar.radio(
    "메뉴 선택", ["대시보드 & 통계", "내 서재", "새 책 기록하기"]
)

# ----------------------------------------------------
# 1. 대시보드 & 통계
# ----------------------------------------------------
if menu == "대시보드 & 통계":
  st.title("📊 나의 독서 통계 및 요약")

  books = st.session_state.books

  if not books:
    st.info(
        "아직 등록된 책이 없습니다. 왼쪽 메뉴에서 '새 책 기록하기'를 통해 책을"
        " 추가해 보세요!"
    )
  else:
    total_books = len(books)
    total_quotes = sum(len(b.get("quotes", [])) for b in books)
    avg_rating = (
        sum(b.get("rating", 0) for b in books) / total_books
        if total_books > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("읽은 책 총 권수", f"{total_books}권")
    col2.metric("모은 구절 수", f"{total_quotes}개")
    col3.metric("평균 평점", f"{avg_rating:.1f}점 / 5.0점")

    st.markdown("---")
    st.subheader("📖 최근 읽은 책")

    # 최근 등록된 순서로 3권 표시
    recent_books = books[::-1][:3]
    for b in recent_books:
      with st.expander(f"📌 {b['title']} - {b['author']} (평점: {b['rating']}점)"):
        st.write(f"**장르:** {b.get('genre', '미분류')} | **읽은 기간:** {b.get('read_date', '정보 없음')}")
        st.write(f"**감상평:** {b.get('review', '작성된 감상평이 없습니다.')}")
        if b.get("quotes"):
          st.markdown("**인상 깊은 구절:**")
          for q in b["quotes"]:
            st.markdown(f"> *\"{q}\"*")

# ----------------------------------------------------
# 2. 내 서재
# ----------------------------------------------------
elif menu == "내 서재":
  st.title("📖 내 서재")

  books = st.session_state.books

  if not books:
    st.info("서재가 비어있습니다. 책을 추가해 주세요.")
  else:
    # 검색 및 필터
    search_query = st.text_input(
        "🔍 책 제목 또는 저자 검색", ""
    )

    filtered_books = books
    if search_query:
      filtered_books = [
          b
          for b in books
          if search_query.lower() in b["title"].lower()
          or search_query.lower() in b["author"].lower()
      ]

    st.markdown("---")

    for idx, b in enumerate(filtered_books):
      cols = st.columns([4, 1])
      with cols[0]:
        st.markdown(f"### {b['title']}")
        st.caption(f"저자: {b['author']} | 장르: {b.get('genre', '미분류')} | 평점: {'⭐' * b.get('rating', 0)}")
        st.write(f"**읽은 시기:** {b.get('read_date', '-')}")
        
        with st.expander("자세히 보기 (감상 및 구절)"):
          st.markdown(f"**💡 감상평:**\n{b.get('review', '없음')}")
          if b.get("quotes"):
            st.markdown("**✍️ 인상 깊은 구절:**")
            for q in b["quotes"]:
              st.markdown(f"> *\"{q}\"*")

      with cols[1]:
        st.write("")
        if st.button("삭제", key=f"del_{idx}"):
          # 원본 리스트에서 해당 책 삭제 후 저장
          books.remove(b)
          st.session_state.books = books
          save_data(books)
          st.rerun()

      st.markdown("---")

# ----------------------------------------------------
# 3. 새 책 기록하기
# ----------------------------------------------------
elif menu == "새 책 기록하기":
  st.title("✍️ 새로운 독서 기록 추가")

  with st.form("book_form"):
    title = st.text_input("책 제목 *")
    author = st.text_input("저자 *")
    
    col1, col2 = st.columns(2)
    with col1:
      genre = st.selectbox("장르", ["소설", "인문/철학", "자기계발", "경제/경영", "에세이/시", "과학", "기타"])
    with col2:
      rating = st.slider("평점", 1, 5, 5)

    read_date = st.text_input("읽은 시기 (예: 2026년 3월 또는 2026.03)", value="2026년")
    
    review = st.text_area("독서 감상문 / 느낀 점")
    
    # 인상 깊은 구절 여러 개 입력받기
    st.markdown("---")
    st.subheader("인상 깊은 구절 (선택)")
    q1 = st.text_input("구절 1")
    q2 = st.text_input("구절 2")
    q3 = st.text_input("구절 3")

    submitted = st.form_submit_button("저장하기")

    if submitted:
      if not title or not author:
        st.error("책 제목과 저자는 필수 입력 항목입니다!")
      else:
        # 구절 리스트 정리 (빈 값 제외)
        quotes = [q for q in [q1, q2, q3] if q.strip()]

        new_book = {
            "title": title,
            "author": author,
            "genre": genre,
            "rating": rating,
            "read_date": read_date,
            "review": review,
            "quotes": quotes,
        }

        st.session_state.books.append(new_book)
        save_data(st.session_state.books)
        st.success(f"'{title}' 책이 서재에 성공적으로 추가되었습니다! 🎉")