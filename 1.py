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

# CUDA가 사용 가능한 경우 GPU를 사용하고, 그렇지 않으면 CPU를 사용합니다.
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# LLM 모델 초기화
llm_model = None

def initialize_llm_model():
    global llm_model
    try:
        llm_model = LlamaCpp(
            model_path="./llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
            n_ctx=512,
            n_batch=512,
            n_gpu_layers=35,
            verbose=True,
        )
        print("LLM 모델이 성공적으로 초기화되었습니다.")
    except Exception as e:
        print(f"LLM 모델 초기화 실패: {e}")
        llm_model = None

# Stable Diffusion 모델 불러오기
def load_stable_diffusion_model():
    try:
        pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1").to(device)
        print("Stable Diffusion 모델이 성공적으로 로드되었습니다.")
        return pipe
    except Exception as e:
        print(f"Stable Diffusion 모델 불러오기 실패: {e}")
        return None

stable_diffusion_model = load_stable_diffusion_model()

# 생성형 이미지 생성 함수
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

# 성함 검증을 위한 프롬프트 생성 함수
def create_name_validation_prompt(name):
    return (
        f"다음은 사용자가 입력한 성함입니다: '{name}'\n"
        "성함이 올바른 형식인지 판단해 주세요. 성함은 2자에서 5자 사이의 한글이어야 합니다. 성함이 올바르지 않은 경우 '올바른 성함이 아닙니다. 다시 입력해 주세요.'라고 응답하고, 올바른 경우 '올바른 성함입니다.'라고 응답해 주세요."
    )

# 대화형 인터페이스 함수
def chat():
    print("안녕하세요! AI가 먼저 질문 드리겠습니다")

    # LLM 모델 초기화 시도
    initialize_llm_model()

    if llm_model is None:
        print("LLM 모델이 초기화되지 않았습니다.")
        return

    # ConversationBufferMemory 초기화
    memory = ConversationBufferMemory(return_messages=True)

    # ConversationChain 초기화
    conversation_chain = ConversationChain(
        llm=llm_model,
        memory=memory,
        prompt=ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("시스템 메시지"),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    )

    user_name = None

    while user_name is None:
        # 사용자의 이름 입력받기
        ai_question = "고객님의 성함을 말씀해 주세요. (성함은 2자에서 5자 사이로 입력해 주세요.)"
        print(f"AI 질문: {ai_question}")
        name_input = input("고객님 답변: ").strip()

        # LLM을 통해 성함 유효성 검증 요청
        validation_prompt = create_name_validation_prompt(name_input)
        
        try:
            validation_response = conversation_chain.run(input=validation_prompt)
            print(f"LLM 검증 응답: {validation_response}")

            # 응답을 처리하여 성함이 유효한지 여부를 확인
            if "올바른 성함입니다" in validation_response:
                user_name = name_input
                print(f"감사합니다, {user_name}님!")
            elif "올바른 성함이 아닙니다" in validation_response:
                print("성함이 올바르지 않습니다. 다시 입력해 주세요.")
            else:
                print("성함 검증 응답이 예상과 다릅니다. 다시 입력해 주세요.")
        except Exception as e:
            print(f"성함 검증 중 오류 발생: {e}")

    # AI가 질문하기 - 디자인 스타일 입력 요청
    ai_question = "어떤 스타일의 디자인을 원하시나요?"
    print(f"AI 질문: {ai_question}")
    user_response = input(f"{user_name}님 답변: ").strip()

    # 대화 종료 조건 추가 가능 (예를 들어 특정 단어 입력 시)
    if user_response.lower() == '그만':
        print("대화를 종료합니다.")
        return

    # LLM 모델에 디자인 스타일 질문 전달하여 응답 생성
    try:
        response = conversation_chain.run(input=user_response)
        print(f"AI 답변: {response}")
    except Exception as e:
        print(f"대화 중 오류 발생: {e}")

    # Stable Diffusion 모델을 통한 이미지 생성 요청
    if stable_diffusion_model is not None:
        print("이미지를 생성 중입니다...")
        generate_image_from_prompt(user_response)
    else:
        print("Stable Diffusion 모델을 초기화할 수 없습니다.")

# 대화 시작
if __name__ == "__main__":
    chat()

    # 모델 해제 시도
    if llm_model is not None:
        try:
            # 객체 삭제 시 close()가 아닌 del을 사용할 수 있음
            del llm_model
            print("LLM 모델이 해제되었습니다.")
        except Exception as e:
            print(f"LLM 모델 해제 중 오류 발생: {e}")
