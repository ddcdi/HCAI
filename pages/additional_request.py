import streamlit as st
import openai
import re,os
import json
import utils

st.title("동화생성 🎈")

# api키 설정
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 세션 상태 변수 초기화
if 'select_language' not in st.session_state:
    st.session_state.select_language = 'zh-cn'
if "check" not in st.session_state:
    st.session_state.check=False

# 첫번째 동화 생성
if 'first_tale' not in st.session_state:
    with st.spinner("동화 만들 재료 수집 하는 중..."):
        llm_1 = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 다문화 가정 아동들의 이중 언어 발달을 돕기 위한 동화책 작가입니다."},
                {"role":"user","content": f'''
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
                2. 만일 아동 나이가 ‘유아’이면, 20~24페이지, 각 페이지 당 글자 수 20자 이상 80자 이하로 만들어줘.
            
                위의 조건들을 모두 포함하여 제 1언어로만 동화를 써줘. 
                동화는 예시처럼 출력해줘 
            
                예시: 한국어 버전 
                페이지 1: 아침이 밝았어요. 오늘은 파란 하늘이 펼쳐진 맑은 날이에요. 루피는 창밖을 보며 기분이 좋아졌어요. 
                페이지 2: "오늘은 젤리와 숨바꼭질을 해야지!" 루피는 좋아하는 고양이 인형, 젤리를 꼭 안고 이야기했어요. 
                페이지 3: 루피는 젤리를 데리고 집 앞 공원으로 나갔어요. 공원에는 사람들이 아이스 하키를 즐기고 있었어요. "와, 아이스 하키야!" 루피는 눈이 반짝였어요. 
                '''
                }
            ]
        )
        first_tale = llm_1.choices[0].message.content.strip().split('\n')
        st.session_state.first_tale=first_tale

# 최종 동화 생성
if 'final_tale' not in st.session_state:
    st.session_state.final_tale = []
    with st.spinner("동화를 만들고 있는 중..."):
        llm_2 = client.chat.completions.create(
            model = "gpt-4",
            messages=[
                {"role": "system", "content": f"""당신은 다문화 가정 아동들의 이중 언어 발달을 돕기 위한 동화책 작가입니다.
            제 2언어는 {st.session_state.select_language}입니다.
            다음 지시사항을 엄격히 따라 동화를 작성해주세요:
        
            1. 형식:
               - 홀수 페이지: 한국어 내용
               - 짝수 페이지: 직전 홀수 페이지의 내용을 제 2언어로 번역
               - 각 페이지는 반드시 "페이지 N: " 형식으로 시작해야 합니다 (N은 페이지 번호)
               - 페이지 번호는 1부터 시작하여 순차적으로 증가
        
            2. 내용:
               - 다음 요소들을 반드시 포함: {{중국, 유아, 한국어, 중국어, 날씨 표현, 중국의 차 문화}}, {{젤리, 고양이, 하늘색, 블럭쌓기, 하츄핑}}
               - 새로운 캐릭터를 추가하여 상호작용을 통해 동화를 더 흥미롭게 만들어주세요
               - 새로운 사건을 추가하여 동화를 더 매력적으로 만들어주세요
               - '날씨 표현'과 관련된 단어 사용을 늘려 강조해주세요
               - '중국의 차 문화'에 대한 설명을 강화하여 강조해주세요
               - 모든 요소들을 자연스럽게 포함시켜 동화를 진행해주세요
        
            3. 길이: 총 48페이지 (한국어 24페이지, 제 2언어 24페이지)
        
            4. 주의사항:
               - 설명 없이 이야기만 출력해주세요
               - 각 페이지의 내용은 2-3문장으로 제한해주세요
        
            예시 형식:
            페이지 1: [한국어 내용]
            페이지 2: [제 2언어로 번역된 내용]
            페이지 3: [한국어 내용]
            ...
        
            이전에 생성된 동화를 기반으로 위 지시사항에 맞게 수정하여 새로운 동화를 작성해주세요.
            """
             },
            {"role": "user", "content": f'''
            이전에 생성된 동화:
            {st.session_state.first_tale}
        
            위 지시사항에 따라 이 동화를 수정하고 확장하여 새로운 버전을 만들어주세요.
            '''}
            ]
        )
        gpt_response = llm_2.choices[0].message.content.strip().split('\n')

    for page in gpt_response:
        # 빈 줄 건너뛰기
        if not page.strip():
            continue

        # ':' 를 기준으로 분리하고, 오른쪽 내용만 저장
        parts = page.split(':', 1)
        if len(parts) > 1:
            content = parts[1].strip()
            st.session_state.final_tale.append({"role": "assistant", "content": content})
        else:
            print(f"Warning: Unexpected format in line: {page}")

    # 언어가 중국어일 때 한어 병음 추가
    if st.session_state.select_language == 'zh-cn':
        st.session_state['messages_2'] = []

        # 중국어 내용만 추출
        chinese_content = "\n".join([page["content"] for page in st.session_state.final_tale if
                                     int(page["content"].split(":")[0].split()[1]) % 2 == 0])

        # 한어병음 생성
        llm_3 = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 중국어 텍스트를 한어병음으로 변환하는 전문가입니다. 주어진 중국어 텍스트의 한어병음만을 제공해주세요."},
                {"role": "user", "content": f'''
                다음 중국어 이야기의 한어병음만 출력해주세요. 각 페이지는 "페이지 N:"으로 시작해야 합니다(N은 페이지 번호).

                이야기:
                {chinese_content}
                '''}
            ]
        )

        gpt_response = llm_3.choices[0].message.content.strip().split('\n')

        for page in gpt_response:
            # 빈 줄 건너뛰기
            if not page.strip():
                continue

            # 페이지 번호와 내용 분리
            if page.startswith("페이지"):
                parts = page.split(":", 1)
                if len(parts) > 1:
                    page_num = parts[0]
                    content = parts[1].strip()
                    st.session_state.messages_2.append({"role": "assistant", "content": f"{page_num}: {content}"})
                else:
                    print(f"Warning: Unexpected format in line: {page}")
            else:
                print(f"Warning: Line does not start with '페이지': {page}")

# 최종 동화 출력
if st.session_state.final_tale:
    for message in st.session_state.final_tale:
        if message["role"] == "assistant":
            with st.chat_message(message["role"]):
                # 텍스트 출력
                st.write(message["content"])
                # # 음성 출력
                # # Part3: 모델 인퍼런스
                # st.markdown("사용될 모델은 multilingual_xtts_v2.0.2 입니다.")
                # output_name = st.text_input(
                #     "TTS로 생성될 파일명을 입력하세요. \
                #     중복될 시 덮어씌워 집니다. \
                #     파일 확장자는 입력하지 않으셔도 됩니다.",
                #     value=""
                #     )
                # tts_input = message.content
                # prompt= re.sub("([^\x00-\x7F]|\w)(\.|\。|\?)",r"\1 \2\2", tts_input)
                # button3 = st.button("Run")
                #
                # if button3:
                #     # st.write(prompt)
                #     with st.spinner("변환 중..."):
                #         # 확인
                #         st.write("레퍼런스 파일: " + ", ".join(os.listdir(personal_path_inputs)))
                #         gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
                #             gpt_cond_len=30, gpt_cond_chunk_len=4, max_ref_length=60,
                #             audio_path=[
                #                 personal_path_inputs + x for x in os.listdir(personal_path_inputs)
                #             ]
                #         )
                #         out = model.inference(
                #             prompt,
                #             lang_code,
                #             gpt_cond_latent,
                #             speaker_embedding,
                #             repetition_penalty=5.0,
                #             temperature=0.75,
                #         )
                #         # HTML Display
                #         st.audio(np.expand_dims(np.array(out["wav"]), 0), sample_rate=24000)
                #         # 자동 저장
                #         torchaudio.save(personal_path_outputs+f"{output_name}.wav",
                #                         torch.tensor(out["wav"]).unsqueeze(0), 24000)
                #
                #         st.success('TTS 생성 및 저장 완료')

        # 이미지 출력
        # 여기에 이미지 생성 코드 넣으면 될 것 같습니다
        elif message["role"] == "image":
            st.image(message["content"],use_column_width=True)

    # 메시지를 json 파일로 저장하는 버튼
    if st.button("종료"):
        st.session_state.check = True

    if st.session_state.check :
        filename = st.session_state.session_id+".json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([utils.chat_message_to_dict(message) for message in st.session_state["messages"]], f, ensure_ascii=False, indent=4)
        st.success("성공적으로 종료했습니다!!")