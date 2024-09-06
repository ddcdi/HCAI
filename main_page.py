import streamlit as st
from langchain import LLMChain
from langchain.llms import OpenAI
import re

# Streamlit 앱 제목
st.title("다문화가정 아동 부모 상담 챗봇")

# OpenAI API 키 설정
openai_api_key = 'YOUR_API_KEY'
llm = OpenAI(openai_api_key=openai_api_key, model="gpt-3.5-turbo")

# 세션 상태 변수 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'question_complete' not in st.session_state:
    st.session_state.question_complete = False

if 'parent_prefer' not in st.session_state:
    st.session_state.parent_prefer = None

# 프롬프트 초기화
if 'prompt' not in st.session_state:
    st.session_state.prompt = '''
    너는 다문화가정 아동들의 부모와 대화하는 챗봇이야. 순서대로 5가지 질문을 하나씩 해줘. 부모가 답변하면 그 다음에 질문을 해. 

    1. 부모의 출신국가 
    2. 아동 나이 
    3. 자녀가 한국어와 부모의 출신국가 언어 중 어느 것을 더 어려워하는지 
    4. 부모가 자녀가 배웠으면 하는 언어 표현이 있는지 
    5. 부모가 자녀에게 알려주고 싶은 문화, 풍습, 단어, 설화 등의 문화적 요소가 있는지 

    2번 질문부터는 부모의 출신국가 언어로도 번역해줘. 
    아동의 나이가 0~3세이면 영아로 정리해줘. 
    아동의 나이가 4세~7세 이상이면 유아로 정리해줘. 
    5번의 답변을 듣고 답변에 대해 너가 이해한대로 설명해줘. 만일 사용자가 아니라고 하면, 다시 이해하고 맞는지 질문해.
    5번의 답변이 끝나면 다음과 같은 형식으로 예시처럼 정리해줘. 

    형식: {(1)의 답변, (2)의 답변, (3)에 답변하지 않은 언어, (3)의 답변, (4)의 답변, (5)의 답변} 
    예시: {캐나다, 유아, 한국어, 영어, 날씨에 대한 표현, 아이스 하키}
    '''

# 사용자 입력 처리
if not st.session_state.question_complete:
    # 질문이 있는 경우
    if len(st.session_state.messages) == 0:
        # 첫 번째 질문 생성
        response = llm(st.session_state.prompt)
        gpt_response = response.strip()

        st.session_state.messages.append({"role": "assistant", "content": gpt_response})
        with st.chat_message("assistant"):
            st.write(gpt_response)  # 첫 번째 질문 출력

    user_input = st.text_input("답변을 입력하세요:")
    
    if user_input:
        # 사용자 응답 저장
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 다음 질문 생성
        response = llm(st.session_state.prompt + "\n" +"\n".join([msg['content'] for msg in st.session_state.messages]))
        gpt_response = response.strip()

        st.session_state.messages.append({"role": "assistant", "content": gpt_response})

        # 답변의 마지막이 }로 끝나면 질문 완료
        if gpt_response.strip().endswith('}'):
            st.session_state.question_complete = True
            # 중괄호 안의 내용 추출
            match = re.search(r'\{(.*?)\}', gpt_response.strip())
            if match:
                parent_prefer = match.group(1)  # 중괄호 안의 내용을 가져옴
                st.session_state.parent_prefer = parent_prefer
                print("결과:", st.session_state.parent_prefer)

        # 대화 내용 출력
        for message in st.session_state["messages"]:
            with st.chat_message(message['role']):
                st.write(message['content'])

# 모든 질문이 끝난 경우 결과 출력
if st.session_state.question_complete:
    st.write("모든 질문이 완료되었습니다. 결과를 정리합니다. 다음 버튼을 눌러주세요.")
    st.page_link("pages/child_prefer.py", label="아동 선호도", icon="1️⃣")
