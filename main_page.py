import streamlit as st
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI
import utils
import warnings, os, re, random
from pydub import AudioSegment
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import torch, torchaudio
import numpy as np
warnings.simplefilter(action='ignore')

# 하이퍼파라미터 세팅
use_gpu = False # True: 0번 single-GPU 사용 & False: CPU 사용
os.environ["CUDA_VISIBLE_DEVICES"] = "0" if use_gpu else "-1"
seed_num = 777 # 수정가능, 결과값 고정을 위함
torch.manual_seed(seed_num)
torch.cuda.manual_seed(seed_num)
torch.cuda.manual_seed_all(seed_num) # if use multi-GPU
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(seed_num)
random.seed(seed_num)


# TTS 모델 캐싱
@st.cache_resource(show_spinner=True)
def Caching_XTTS_Model():
    config = XttsConfig()
    config.load_json("./tts_models--multilingual--multi-dataset--xtts_v2.0.2/config.json")
    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config, 
        checkpoint_dir="./tts_models--multilingual--multi-dataset--xtts_v2.0.2", 
    )
    if use_gpu:
        model.cuda()
    return model
model = Caching_XTTS_Model()

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

if 'select_language' not in st.session_state:
    st.session_state.select_language = False

# 음성에 나올 언어 선택
if not st.session_state.select_language:
    supported_languages = [
        "  : -- Select Your Language -- :  ",
        "Arabic(아랍어) : ar", 
        "Brazilian Portuguese(포르투갈어) : pt", 
        "Mandarin Chinese(중국어) : zh-cn", 
        "Czech(체코어) : cs", 
        "Dutch(네덜란드어) : nl", 
        "English(영어) : en", 
        "French(프랑스어) : fr", 
        "German(독일어) : de", 
        "Italian(이탈리아어) : it", 
        "Polish(폴란드어) : pl", 
        "Russian(러시아어) : ru", 
        "Spanish(스페인어) : es", 
        "Turkish(터키어) : tr", 
        "Japanese(일본어) : ja", 
        "Korean(한국어) : ko", 
        "Hungarian(헝가리어) : hu", 
        "Hindi(힌디어) : hi"
    ]
    chosen_lang = st.selectbox("언어를 선택해주세요.", supported_languages)
    lang_code = chosen_lang.split(" : ")[-1]
    st.session_state.select_language = lang_code

    name = st.text_input("성함을 영어로 작성해주세요. EX) 홍길동 -> gildong hong", value="")
    button0 = st.button("Confirm")
    if button0:
        if lang_code == ' ':
            st.warning("언어가 선택되지 않았습니다.", icon="⚠️")
        if name == '':
            st.warning("성함이 입력되지 않았습니다.", icon="⚠️")
        else:
            st.success(f"사용될 언어 코드와 성함: {lang_code} & {name}")
    name = "_".join(name.lower().split())

    st.markdown(f"선택한 '언어_이름' 으로 경로를 생성합니다. EX) ko_gildong_hong")
    button1 = st.button("Submit")
    personal_path_inputs = f"./voices/{lang_code}_{name}/inputs/"
    personal_path_outputs = f"./voices/{lang_code}_{name}/outputs/"
    if button1:
        # 경로설정
        os.makedirs(personal_path_inputs, exist_ok=True)  # 개별 음성파일 저장 경로
        os.makedirs(personal_path_outputs, exist_ok=True) # TTS 결과파일 저장 경로
        st.success('경로 생성됨')

    # Part2: 개별 목소리 업로드/변환 및 로컬 저장
    with st.form("upload-then-clear-form", clear_on_submit=True):
            file_list  = st.file_uploader(
                '음성파일을 업로드 하세요. 여러 파일을 한번에 업로드 하셔도 됩니다.', 
                type=['m4a','wav'], accept_multiple_files=True
            )
            button2 = st.form_submit_button("Convert")
            if button2:

                # 업로드 된 파일 로컬에 저장
                for file in file_list:
                    with open(personal_path_inputs + file.name.lower(), 'wb') as f:
                        f.write(file.getbuffer())

                # 확장자 변환 및 trim
                for file in os.listdir(personal_path_inputs):
                    # m4a 파일의 경우
                    if len(file.split(".m4a")[0]) != len(file):
                        tobesaved = personal_path_inputs + file.split(".m4a")[0]+".wav"
                        audio = AudioSegment.from_file(personal_path_inputs + file, format="m4a")
                        audio.export(tobesaved, format="wav")
                        os.remove(personal_path_inputs + file) # m4a 파일 제거
                        audio = AudioSegment.from_wav(tobesaved)
                        audio = audio[:-200] # 윈도우 녹음기 사용시 마지막 노이즈 제거
                        audio.export(tobesaved, format="wav") # 덮어쓰기

                    # wav 파일의 경우
                    else:
                        tobesaved = personal_path_inputs + file
                        audio = AudioSegment.from_wav(tobesaved)
                        audio = audio[:-200] # 윈도우 녹음기 사용시 마지막 노이즈 제거
                        audio.export(tobesaved, format="wav") # 덮어쓰기

                del file_list
                st.success('변환 완료')

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
