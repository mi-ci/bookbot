import torch
from PIL import Image
from diffusers import StableDiffusionPipeline
from langchain.llms import LlamaCpp
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
import re

# GPU 설정
device = torch.device("cpu")  # CPU를 강제로 사용하도록 설정

llm_model = None

def initialize_llm_model():
    global llm_model
    try:
        llm_model = LlamaCpp(
            model_path="./llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
            n_ctx=4000,
            n_batch=512,
            n_gpu_layers=35,
            verbose=True,
        )
        print("LLM 모델이 성공적으로 초기화되었습니다.")
    except Exception as e:
        print(f"LLM 모델 초기화 실패: {e}")
        llm_model = None

def load_stable_diffusion_model():
    try:
        model_name = "stabilityai/stable-diffusion-2-1"
        pipe = StableDiffusionPipeline.from_pretrained(model_name)
        pipe.to("cpu")  # 모델을 CPU로 이동
        print("Stable Diffusion 모델이 성공적으로 로드되었습니다.")
        return pipe
    except Exception as e:
        print(f"Stable Diffusion 모델 불러오기 실패: {e}")
        return None

stable_diffusion_model = load_stable_diffusion_model()

def generate_image_from_prompt(prompt):
    if stable_diffusion_model is None:
        print("Stable Diffusion 모델이 초기화되지 않았습니다.")
        return
    try:
        with torch.no_grad():
            image = stable_diffusion_model(prompt).images[0]
            image.save("generated_image.png")
            print("이미지 생성 완료: 'generated_image.png'")
    except Exception as e:
        print(f"이미지를 생성하는 중 오류 발생: {e}")

def is_valid_name(name):
    return bool(re.match(r'^[가-힣]{2,5}$', name))

def is_valid_phone_number(phone_number):
    return bool(re.match(r'^\d{3}-\d{4}-\d{4}$', phone_number))

def is_valid_email(email):
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

def get_user_info():
    while True:
        name = input("성함을 입력하세요: ")
        if is_valid_name(name):
            break
        else:
            print("올바른 성함을 입력해 주세요.")
    
    company = input("회사명을 입력하세요: ")
    
    while True:
        phone_number = input("휴대폰 번호를 입력하세요 (형식: 010-1234-5678): ")
        if is_valid_phone_number(phone_number):
            break
        else:
            print("올바른 휴대폰 번호를 입력해 주세요.")
    
    while True:
        email = input("이메일 주소를 입력하세요: ")
        if is_valid_email(email):
            break
        else:
            print("올바른 이메일 주소를 입력해 주세요.")
    
    return {
        "name": name,
        "company": company,
        "phone_number": phone_number,
        "email": email
    }

branding_questions = [
    "브랜드의 비전과 미션을 설명해 주세요.",
    "경쟁 업체의 브랜드를 어떻게 차별화하고 싶으신가요?",
]

multimedia_questions = [
    "멀티미디어 프로젝트의 주제나 목적은 무엇인가요?",
    "어떤 멀티미디어 형식을 원하시나요? (예: 비디오, 애니메이션, 오디오 등)",
    "타겟 오디언스는 누구인가요?",
    "프로젝트의 주요 메시지나 테마는 무엇인가요?",
    "특별히 원하는 스타일이나 톤이 있나요?"
]

printing_questions = [
    "인쇄 디자인의 목적은 무엇인가요?",
    "디자인에 포함될 주요 내용이나 메시지는 무엇인가요?",
    "어떤 인쇄 매체를 사용하고 싶으신가요? (예: 전단지, 포스터, 브로셔 등)",
    "타겟 오디언스는 누구인가요?",
    "특별히 원하는 디자인 스타일이나 색상이 있나요?"
]

web_design_questions = [
    "웹사이트의 주요 목적은 무엇인가요?",
    "타겟 오디언스는 누구인가요?",
    "웹사이트에 포함될 주요 기능이나 섹션은 무엇인가요?",
    "디자인의 스타일이나 테마에 대한 선호가 있나요?",
    "웹사이트가 지원해야 하는 특정 기술이나 플랫폼이 있나요?"
]

def summarize_category_conversations(memory_dict):
    summaries = {}
    for category, memory in memory_dict.items():
        if not memory.chat_memory.messages:
            summaries[category] = "대화 내용이 없습니다."
            continue
        
        summary_prompt = (
            "다음은 사용자의 대화 내용입니다. 이 대화를 요약해 주세요:\n"
            + "\n".join(f"Q: {item['content']}" for item in memory.chat_memory.messages if 'content' in item)
        )
        try:
            summary = llm_model(summary_prompt)
            summaries[category] = summary
        except Exception as e:
            print(f"카테고리 '{category}' 요약 중 오류 발생: {e}")
            summaries[category] = "요약을 생성하지 못했습니다."
    return summaries

def chat():
    initialize_llm_model()

    memory_dict = {
        "브랜딩": ConversationBufferMemory(return_messages=True),
        "멀티미디어": ConversationBufferMemory(return_messages=True),
        "인쇄 디자인": ConversationBufferMemory(return_messages=True),
        "웹 디자인": ConversationBufferMemory(return_messages=True)
    }

    conversation_chains = {
        category: ConversationChain(
            llm=llm_model,
            memory=memory,
            prompt=ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(
                    f"You are an expert in {category}. Please provide responses to the user's queries."
                ),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="history")
            ])
        )
        for category, memory in memory_dict.items()
    }

    user_info = get_user_info()
    print(f"사용자 정보: {user_info}")

    ai_question = """어떤 형식의 디자인을 희망하시나요?

    1: 브랜딩 2: 멀티미디어 3: 인쇄 4: 웹

    4가지 카테고리 가운데 1개 번호를 선택해서 숫자를 입력해주세요!"""

    print(f"AI 질문: {ai_question}")
    design_choice = input("고객님 답변: ").strip()

    if design_choice == '1':
        category = "브랜딩"
        questions = branding_questions
    elif design_choice == '2':
        category = "멀티미디어"
        questions = multimedia_questions
    elif design_choice == '3':
        category = "인쇄 디자인"
        questions = printing_questions
    elif design_choice == '4':
        category = "웹 디자인"
        questions = web_design_questions
    else:
        print("잘못된 선택입니다. 1에서 4까지의 번호를 입력해 주세요.")
        return

    print(f"카테고리 '{category}'에 대한 질문을 시작하겠습니다.")
    for i, question in enumerate(questions):
        print(f"\n질문 {i+1}: {question}")
        user_input = input("답변 (종료는 '종료' 입력): ")
        if user_input.lower() == "종료":
            break
        
        response = conversation_chains[category].run(input=user_input)
        print(f"응답: {response}")

        memory_dict[category].chat_memory.messages.append({
            'role': 'user',
            'content': user_input
        })
        memory_dict[category].chat_memory.messages.append({
            'role': 'assistant',
            'content': response
        })
    
    summaries = summarize_category_conversations(memory_dict)
    summary = summaries.get(category, "요약을 생성하지 못했습니다.")
    
    print(f"카테고리 '{category}'의 대화 요약: {summary}")

    if summary and summary != "대화 내용이 없습니다.":
        generate_image_from_prompt(summary)
    else:
        print("유효한 대화 요약이 없으므로 이미지 생성을 건너뜁니다.")

# 실제 채팅 실행
chat()
