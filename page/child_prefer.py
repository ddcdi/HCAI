import streamlit as st
from langchain import LLMChain
from langchain.llms import OpenAI
import re

# Streamlit 앱 제목
st.title("다문화가정 아동 자녀 상담 챗봇")

# OpenAI API 키 설정
openai_api_key = 'YOUR_API_KEY'
llm = OpenAI(openai_api_key=openai_api_key, model="gpt-3.5-turbo")

# 세션 상태 변수 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'question_complete' not in st.session_state:
    st.session_state.question_complete = False

if 'child_prefer' not in st.session_state:
    st.session_state.child_prefer = None

# 프롬프트 초기화
if 'prompt' not in st.session_state:
    st.session_state.prompt = f'''
    너는 아동과 대화하며 친구가 되어주기 위한 챗봇이야. 
    다음 요소를 기억해: {st.session_state.parent_prefer}

    1. 아동의 선호 요소(예: 좋아하는 음식, 캐릭터 등)를 파악해봐. 
    2. 이때 아동의 답변에서 핵심 키워드를 찾아줘.
    3. 총 다섯 가지 질문을 하되, 여러 질문을 한 번에 하지 마. 
    4. 아동이 답변하면 그 다음에 질문을 해. 마지막 답변을 듣고 나서 ‘너가 좋아하는 것들로 동화를 만들어 줄게’ 라는 식으로 말하되, 질문형으로 끝내지 마. 
    5. {{답변1의 키워드, 답변2의 키워드, 답변3의 키워드, 답변4의 키워드, 답변5의 키워드}} 형식으로 예시처럼 정리해줘

    예시: {{포도, 토끼, 하늘색, 숨바꼭질, 루피}}

    '''

# 사용자 입력 처리
if not st.session_state.question_complete :
    # 질문이 있는 경우
    if len(st.session_state.messages) == 0:
        # 첫 번째 질문 생성
        response = llm(st.session_state.prompt)
        gpt_response = response.strip()

        st.session_state.messages.append({"role": "assistant", "content": gpt_response})
        with st.chat_message("assistant"):
            st.write(gpt_response)  # 첫 번째 질문 출력

    # 음성 녹음
    audio_file = utils.record_audio(duration=5, fs=44100, filename="output.wav")
    while not audio_file:
        audio_file = utils.record_audio(duration=5, fs=44100, filename="output.wav")
        
    user_input = utils.recognize_speech(audio_file)
    # user_input = st.text_input("답변을 입력하세요:")
    
    if user_input:
        # 사용자 응답 저장
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 다음 질문 생성
        response = llm(st.session_state.prompt + "\n" +"\n".join([msg['content'] for msg in st.session_state.messages]))
        gpt_response = response.strip()

        st.session_state.messages.append({"role": "assistant", "content": gpt_response})

        # 답변의 마지막이 }로 끝나면 질문 완료
        if(gpt_response.strip().endswith('}')):
            st.session_state.question_complete = True
            # 중괄호 안의 내용 추출
            match = re.search(r'\{(.*?)\}', gpt_response.strip())
            if match:
                child_prefer = match.group(1)  # 중괄호 안의 내용을 가져옴
                st.session_state.child_prefer = child_prefer
                print("결과:", st.session_state.child_prefer)

        # 대화 내용 출력
        for message in st.session_state["messages"]:
            with st.chat_message(message.role):
                st.write(message.content)


# 모든 질문이 끝난 경우 결과 출력
if st.session_state.question_complete:
    st.write("모든 질문이 완료되었습니다. 결과를 정리합니다. 다음 버튼을 눌러주세요.")
    st.page_link("pages/additional_request.py", label="완성!", icon="1️⃣")
