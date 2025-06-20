import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(
    page_title="서평 피드백 봇",
    page_icon="📚",
    layout="wide"
)

# 제목과 설명
st.title("📚 서평 피드백 봇")
st.write(
    "**당신의 서평을 더 풍성하게 만들어드립니다!** 📝\n\n"
    "서평을 작성하거나 공유하시면, AI가 긍정적인 피드백과 함께 개선점을 제안해드립니다. "
    "OpenAI API 키가 필요합니다. [여기서 발급받으세요](https://platform.openai.com/account/api-keys)."
)

# 사이드바에 사용법 안내
with st.sidebar:
    st.header("📖 사용법")
    st.markdown("""
    1. **OpenAI API 키 입력**
    2. **책 제목과 저자 입력** (선택사항)
    3. **서평 작성 또는 공유**
    4. **AI 피드백 받기**
    
    ### 💡 팁
    - 구체적인 감상과 느낌을 적어주세요
    - 책의 어떤 부분이 인상적이었는지 언급해보세요
    - 다른 독자들에게 추천하고 싶은 이유를 써보세요
    """)
    
    st.header("🎯 피드백 유형")
    feedback_type = st.selectbox(
        "원하는 피드백 유형을 선택하세요:",
        ["종합적인 피드백", "구체성 향상", "감정 표현 개선", "구조적 개선", "추천 포인트 강화"]
    )

# API 키 입력
openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")

if not openai_api_key:
    st.info("OpenAI API 키를 입력해주세요! 🗝️", icon="🔑")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)
    
    # 책 정보 입력 섹션
    st.subheader("📖 책 정보 (선택사항)")
    col1, col2 = st.columns(2)
    with col1:
        book_title = st.text_input("책 제목", placeholder="예: 해리포터와 마법사의 돌")
    with col2:
        book_author = st.text_input("저자", placeholder="예: J.K. 롤링")
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 시스템 프롬프트 정의
    def get_system_prompt(feedback_type, book_title="", book_author=""):
        book_info = f"책: {book_title} (저자: {book_author})" if book_title else ""
        
        feedback_instructions = {
            "종합적인 피드백": "서평의 전반적인 품질을 높이는 방법을 제안하세요.",
            "구체성 향상": "더 구체적이고 상세한 표현 방법을 제안하세요.",
            "감정 표현 개선": "감정과 느낌을 더 생생하게 표현하는 방법을 제안하세요.",
            "구조적 개선": "서평의 구성과 흐름을 개선하는 방법을 제안하세요.",
            "추천 포인트 강화": "다른 독자들에게 더 매력적으로 어필하는 방법을 제안하세요."
        }
        
        return f"""당신은 친근하고 전문적인 서평 피드백 전문가입니다. 
        
        역할:
        - 사용자의 서평에 대해 항상 긍정적이고 격려하는 태도를 유지
        - 좋은 점들을 먼저 칭찬하고 인정
        - 건설적인 개선 제안을 친근하게 제공
        - {feedback_instructions[feedback_type]}
        
        {book_info}
        
        응답 형식:
        1. 👍 **잘하신 점들** - 서평의 장점들을 구체적으로 칭찬
        2. 💡 **개선 제안** - 친근한 톤으로 발전 방향 제시
        3. ✨ **추가 아이디어** - 서평을 더 풍성하게 만들 수 있는 팁
        
        항상 한국어로, 친근하고 격려하는 말투로 답변하세요."""
    
    # 기존 대화 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 채팅 입력
    if prompt := st.chat_input("서평을 작성하거나 공유해주세요! 📝"):
        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
        try:
            # 시스템 프롬프트와 사용자 메시지 결합
            messages_for_api = [
                {"role": "system", "content": get_system_prompt(feedback_type, book_title, book_author)}
            ] + [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=messages_for_api,
                stream=True,
                temperature=0.7,
                max_tokens=1500
            )
            
            # 스트리밍 응답 표시
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            
            # 응답 저장
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")
            st.info("API 키가 올바른지 확인해주세요.")
    
    # 대화 초기화 버튼
    if st.session_state.messages:
        if st.button("🔄 새로운 서평으로 시작하기", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    # 사용 예시
    if not st.session_state.messages:
        st.subheader("💬 사용 예시")
        example_reviews = [
            "이 책 정말 재미있었어요! 주인공이 성장하는 모습이 감동적이었습니다.",
            "스릴러 소설인데 끝까지 범인을 못 맞췄어요. 반전이 대박이었습니다!",
            "자기계발서인데 실용적인 조언들이 많아서 도움이 됐어요. 특히 시간관리 부분이 좋았습니다."
        ]
        
        st.write("이런 식으로 서평을 작성해보세요:")
        for i, example in enumerate(example_reviews, 1):
            st.write(f"{i}. {example}")
