import streamlit as st
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI
import re
import json
import utils

st.title("동화생성 🎈")

# OpenAI API 키 설정
openai_api_key = 'YOUR_API_KEY'
llm = OpenAI(openai_api_key=openai_api_key, model="gpt-3.5-turbo")

# 세션 상태 변수 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'first_tale' not in st.session_state:
    st.session_state.first_tale = False

if 'final_tale' not in st.session_state:
    st.session_state.final_tale = False

# 프롬프트 초기화
if 'prompt' not in st.session_state:
    st.session_state.prompt = f'''
    너는 다문화 가정 아동들의 이중 언어 발달을 돕기 위한 동화책 작가야. 

    다음 요소들을 기억해: 부모의 선호 요소: {st.session_state.parent_prefer}, 아동의 선호 요소: {st.session_state.child_prefer} 

    그리고 다음 8가지 조건으로 동화를 구성해줘 
    1. 아동의 선호 요소를 넣어줘 
    2. ‘표현’ 을 학습할 수 있게 동화 안에 넣어줘 
    3. ‘출신 국가’ 를 동화의 사건, 배경, 등장인물 등에 적용해줘 
    4. ‘문화’ 에 대한 설명을 자연스럽게 넣어줘 
    5. 주어진 요소들을 이름으로 사용하지 마 
    6. 등장인물들은 모두 이름을 가지고 있어야 해 
    7. 만일 아동 나이가 ‘영아’이면, 0~3세 아동이 이해하기 쉬운 표현으로 의성어와 의태어를 추가해줘 
    8. 만일 아동 나이가 ‘유아’이면, 4~7세 아동의 표현력이 향상할 수 있도록 동화를 만들어줘. 

    동화의 분량은 다음 조건을 지켜줘. 
    1. 만일 아동 나이가 ‘영아’이면, 20~24페이지, 각 페이지 당 글자 수는 10자 이상 40자 이하로 만들어줘. 
    2. 만일 아동 나이가 ‘유아’이면, 20~24페이지, 각 페이지 당 글자 수 20자 이상 80자 이하로 만들어줘 

    위의 조건들을 모두 포함하여 제 1언어로만 동화를 써줘. 
    동화는 예시처럼 출력해줘 

    예시: {{제 1언어}} 버전 
    페이지 1: 아침이 밝았어요. 오늘은 파란 하늘이 펼쳐진 맑은 날이에요. 루피는 창밖을 보며 기분이 좋아졌어요. 
    페이지 2: "오늘은 젤리와 숨바꼭질을 해야지!" 루피는 좋아하는 고양이 인형, 젤리를 꼭 안고 이야기했어요. 
    페이지 3: 루피는 젤리를 데리고 집 앞 공원으로 나갔어요. 공원에는 사람들이 아이스 하키를 즐기고 있었어요. "와, 아이스 하키야!" 루피는 눈이 반짝였어요. 
    '''

if not st.session_state.first_tale:
    response = llm(st.session_state.prompt)
    gpt_response = response.strip()
    st.session_state.first_tale = gpt_response

    st.session_state.messages.append({"role": "assistant", "content": gpt_response})
    # 첫번째 동화 
    with st.chat_message("assistant"):
        st.write(gpt_response)

if st.session_state.first_tale:

    if 'prompt_add' not in st.session_state:
        st.session_state.prompt_add =f'''
        다음  6가지  조건으로  동화를  수정해줘.   
 
        1.  현재  이야기에서  이야기의  구성에  대한  설명을  삭제해줘.   
        2.  현재  이야기는  일반적이고  지루해.  새로운  캐릭터를  추가하여  상호작용해서  이야기를 
        더  흥미롭게  만들  수  있어.  이야기를  더  흥미롭게  만들어줘. 
        3.  현재  이야기는  보편적이고  따분해.  새로운  사건을  추가해  이야기를  매력적으로  만들 
        수  있어.  이야기를  더  매력적이게  만들어줘.   
        4.  현재  이야기에서  {{표현}}에  대해  더  강조해줘. {{표현}}과  관련된  단어의  사용을  늘려서 
        더  강조할  수  있어.   
        5.  현재  이야기에서  {{문화}}에  대해  더  강조해줘. {{문화}}에  대한  설명을  강화해서  더  강
        조할  수  있어.   
        6.  현재  이야기를  제  2언어로  출력해줘. 
        
        현재  이야기: {st.session_state.first_tale} 
        '''

    response = llm(st.session_state.prompt_add)
    gpt_response = response.strip()
    
    st.session_state.final_tale = gpt_response

    st.session_state.messages.append({"role": "assistant", "content": gpt_response})

if st.session_state.final_tale:
    # 대화 내용 출력
    for message in st.session_state["messages"]:
        if message.role == "assistant":
            with st.chat_message(message.role):
                # 텍스트 출력
                st.write(message.content)
                # 음성 출력
                # Part3: 모델 인퍼런스
                st.markdown("사용될 모델은 multilingual_xtts_v2.0.2 입니다.")
                output_name = st.text_input(
                    "TTS로 생성될 파일명을 입력하세요. \
                    중복될 시 덮어씌워 집니다. \
                    파일 확장자는 입력하지 않으셔도 됩니다.", 
                    value=""
                    )
                tts_input = message.content
                prompt= re.sub("([^\x00-\x7F]|\w)(\.|\。|\?)",r"\1 \2\2", tts_input)
                button3 = st.button("Run")

                if button3:
                    # st.write(prompt)
                    with st.spinner("변환 중..."):
                        # 확인
                        st.write("레퍼런스 파일: " + ", ".join(os.listdir(personal_path_inputs)))
                        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
                            gpt_cond_len=30, gpt_cond_chunk_len=4, max_ref_length=60,
                            audio_path=[
                                personal_path_inputs + x for x in os.listdir(personal_path_inputs)
                            ]
                        )
                        out = model.inference(
                            prompt,
                            lang_code,
                            gpt_cond_latent,
                            speaker_embedding,
                            repetition_penalty=5.0,
                            temperature=0.75,
                        )
                        # HTML Display
                        st.audio(np.expand_dims(np.array(out["wav"]), 0), sample_rate=24000)
                        # 자동 저장
                        torchaudio.save(personal_path_outputs+f"{output_name}.wav", 
                                        torch.tensor(out["wav"]).unsqueeze(0), 24000)

                        st.success('TTS 생성 및 저장 완료')                
        # 이미지 출력
        elif message.role == "image":
            st.image(message.content,use_column_width=True)

    # 메시지를 json 파일로 저장하는 버튼
    if st.button("종료"):
        st.session_state.check = True

    if st.session_state.check :
        filename = st.session_state.session_id+".json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([utils.chat_message_to_dict(message) for message in st.session_state["messages"]], f, ensure_ascii=False, indent=4)
        st.success("성공적으로 종료했습니다!!")