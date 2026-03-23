import json as json_module

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config
from src.embedding import create_documents, get_embedding_model
from src.vectorstore import load_vectorstore, build_and_save
from src.retriever import get_advanced_retriever, get_base_retriever

# 추천 프롬프트 템플릿 (스트리밍용)
RECOMMEND_PROMPT = ChatPromptTemplate.from_template("""당신은 카드 추천 전문가입니다.

사용자 정보:
{persona}

참고할 카드 정보:
{context}

사용자의 소비 패턴과 니즈를 분석하여 가장 적합한 카드 3장을 추천해주세요.
각 카드에 대해 다음을 포함하세요:
1. 카드명과 카드사
2. 이 사용자에게 추천하는 구체적인 이유
3. 예상 월 절약 금액 (가능한 경우)

추천 사유는 사용자의 소비 패턴과 연결하여 논리적으로 설명해주세요.""")

# 구조화된 JSON 추천 프롬프트
STRUCTURED_PROMPT = ChatPromptTemplate.from_template("""당신은 카드 추천 전문가입니다.

사용자 정보:
{persona}

참고할 카드 정보:
{context}

사용자의 소비 패턴과 니즈를 분석하여 가장 적합한 카드 3장을 추천해주세요.

반드시 아래 JSON 형식으로만 응답하세요. JSON 외의 텍스트는 절대 포함하지 마세요:
[
  {{
    "card_name": "카드명",
    "card_company": "카드사",
    "reason": "이 사용자에게 추천하는 구체적인 이유 (소비 패턴과 연결하여 3~4문장으로 설명)",
    "monthly_saving": "예상 월 절약 금액 (예: 약 15,000원)"
  }}
]""")


def format_docs(docs) -> str:
    """Document 리스트를 프롬프트용 텍스트로 포맷팅"""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def extract_source_cards(docs) -> list[dict]:
    """Document metadata에서 카드 정보 추출"""
    seen = set()
    cards = []
    for doc in docs:
        name = doc.metadata.get("card_name", "")
        if name and name not in seen:
            seen.add(name)
            cards.append({
                "card_name": name,
                "card_company": doc.metadata.get("card_company", ""),
                "image_url": doc.metadata.get("image_url", ""),
                "card_url": doc.metadata.get("card_url", ""),
            })
    return cards


def _get_llm(streaming: bool = False):
    return ChatOpenAI(
        model=config.LLM_MODEL_NAME,
        temperature=config.LLM_TEMPERATURE,
        streaming=streaming,
    )


def _load_retriever_and_docs():
    """retriever와 documents를 로드. 인덱스가 없으면 자동 빌드."""
    documents = create_documents()
    try:
        vectorstore = load_vectorstore()
    except Exception:
        vectorstore = build_and_save()
    retriever = get_advanced_retriever(vectorstore, documents)
    return retriever, documents


def get_recommendation(persona_text: str) -> dict:
    """메인 인터페이스: 페르소나 텍스트 → 추천 결과"""
    retriever, _ = _load_retriever_and_docs()

    docs = retriever.invoke(persona_text)
    context = format_docs(docs)
    source_cards = extract_source_cards(docs)

    llm = _get_llm()
    chain = RECOMMEND_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "persona": persona_text})

    return {"answer": answer, "source_cards": source_cards}


def get_recommendation_stream(persona_text: str):
    """스트리밍 버전: 토큰 단위로 yield + source_cards 반환"""
    retriever, _ = _load_retriever_and_docs()

    docs = retriever.invoke(persona_text)
    context = format_docs(docs)
    source_cards = extract_source_cards(docs)

    llm = _get_llm(streaming=True)
    chain = RECOMMEND_PROMPT | llm | StrOutputParser()

    def stream_generator():
        for chunk in chain.stream({"context": context, "persona": persona_text}):
            yield chunk

    return stream_generator(), source_cards


def get_structured_recommendation(persona_text: str) -> dict:
    """구조화된 추천: JSON 형태로 카드별 추천 이유와 절약 금액 반환"""
    retriever, _ = _load_retriever_and_docs()

    docs = retriever.invoke(persona_text)
    context = format_docs(docs)
    source_cards = extract_source_cards(docs)

    llm = _get_llm()
    chain = STRUCTURED_PROMPT | llm | StrOutputParser()
    raw = chain.invoke({"context": context, "persona": persona_text})

    try:
        recommendations = json_module.loads(raw)
    except json_module.JSONDecodeError:
        # JSON 파싱 실패 시 ```json ... ``` 블록 추출 시도
        import re
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            recommendations = json_module.loads(match.group())
        else:
            recommendations = []

    # source_cards의 image_url, card_url을 recommendations에 병합
    source_map = {c["card_name"]: c for c in source_cards}
    for rec in recommendations:
        src = source_map.get(rec.get("card_name"), {})
        rec["image_url"] = src.get("image_url", "")
        rec["card_url"] = src.get("card_url", "")

    return {"recommendations": recommendations, "source_cards": source_cards}


def get_base_response(persona_text: str) -> str:
    """평가용: RAG 없이 GPT에 직접 질문"""
    prompt = ChatPromptTemplate.from_template(
        "당신은 카드 추천 전문가입니다.\n\n"
        "사용자 정보:\n{persona}\n\n"
        "사용자의 소비 패턴과 니즈를 분석하여 가장 적합한 카드 3장을 추천해주세요."
    )
    llm = _get_llm()
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"persona": persona_text})
