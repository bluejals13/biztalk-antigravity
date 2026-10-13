# app/core/rag_engine.py
import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# 설정값 (이전에 사용하셨던 로컬 서버 세팅 유지)
DATA_DIR = "./data/pdfs"
OLLAMA_BASE_URL = "http://192.168.45.175:11434"

# 1. 임베딩 모델 설정
print("🔄 Ollama 임베딩 초기화 중...")
embeddings = OllamaEmbeddings(
    model="nomic-embed-text", 
    base_url=OLLAMA_BASE_URL,
)

def init_vectorstore():
    """서버 시작 시 DATA_DIR의 PDF를 읽어 FAISS 벡터 DB를 초기화합니다."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    loader = DirectoryLoader(DATA_DIR, glob="*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()

    # 💡 [중요] 폴더에 PDF가 하나도 없을 때 FAISS가 뻗는 것을 방지하기 위한 더미 데이터 처리
    if not docs:
        print("⚠️ [RAG Info] 폴더에 PDF가 없습니다. 빈 벡터 DB를 대기 상태로 생성합니다.")
        dummy_doc = Document(page_content="초기화용 더미 데이터", metadata={"source": "init"})
        return FAISS.from_documents([dummy_doc], embeddings)

    print(f"✅ [RAG Info] {len(docs)}개의 PDF 페이지 로드됨. 벡터 인덱싱 중...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
    split_docs = text_splitter.split_documents(docs)
    
    return FAISS.from_documents(split_docs, embeddings)

# ==========================================
# 전역(Global) 객체 생성 
# (FastAPI 서버가 켜질 때 딱 한 번만 실행되어 메모리에 상주합니다)
# ==========================================
vectorstore = init_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

print("✅ [RAG Info] FAISS 벡터 DB 및 Retriever 준비 완료!")


# app/core/rag_engine.py (기존 코드 아래에 추가)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_llm

# 1. 챗봇용 LLM 객체 생성 (사내망 모델 사용)
chat_llm = get_llm(provider="ollama_qwen3", temperature=0.5)

# 2. RAG 프롬프트 세팅
prompt = ChatPromptTemplate.from_messages([
    ("system", "제공된 문서 내용을 바탕으로 질문에 답하세요. 문서에 없는 내용은 모른다고 답하세요.\n\n[문서]\n{context}"),
    ("human", "{question}")
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 3. 체인 조립
answer_chain = (
    RunnableLambda(lambda x: {"context": format_docs(x["docs"]), "question": x["question"]})
    | prompt
    | chat_llm
    | StrOutputParser()
)

rag_chain_with_sources = (
    RunnableParallel(docs=retriever, question=RunnablePassthrough())
    .assign(answer=answer_chain)
)

print("✅ [RAG Info] 챗봇 체인(answer_chain) 준비 완료!")
