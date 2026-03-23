import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 경로
BASE_DIR = Path(__file__).parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
# FAISS는 한글 경로를 지원하지 않으므로 영문 경로 사용
VECTORDB_DIR = Path.home() / ".card_recommend_ai" / "vectordb"
FAISS_INDEX_PATH = VECTORDB_DIR / "faiss_index"

# 임베딩 모델
EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"

# LLM
LLM_MODEL_NAME = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.3

# 검색 파라미터
RETRIEVER_TOP_K = 5
BM25_WEIGHT = 0.4
VECTOR_WEIGHT = 0.6

# API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
