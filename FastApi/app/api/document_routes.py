# app/api/document_routes.py (전체 덮어쓰기)

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, FileResponse # 💡 FileResponse 추가
from pydantic import BaseModel

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 💡 모듈 전체를 임포트하여 vectorstore를 동적으로 재할당할 수 있게 함
import app.core.rag_engine as rag_engine
from app.core.config import get_llm

router = APIRouter()

DATA_DIR = "./data/pdfs"
MAX_FILE_SIZE_MB = 10
MAX_FOLDER_CAPACITY_MB = 100

def get_folder_size_mb(folder_path: str) -> float:
    if not os.path.exists(folder_path): return 0.0
    total_size = sum(os.path.getsize(os.path.join(folder_path, f)) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)))
    return total_size / (1024 * 1024)

# ==========================================
# 1. 파일 목록 조회 API
# ==========================================
@router.get("/files")
def get_uploaded_files():
    if not os.path.exists(DATA_DIR):
        return {"files": [], "capacity_mb": 0.0, "max_capacity_mb": MAX_FOLDER_CAPACITY_MB}
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    return {
        "files": files,
        "capacity_mb": round(get_folder_size_mb(DATA_DIR), 2),
        "max_capacity_mb": MAX_FOLDER_CAPACITY_MB
    }

# ==========================================
# 2. 파일 다운로드 API (✨ 신규 추가)
# ==========================================
@router.get("/files/{filename}")
def download_file(filename: str):
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    return FileResponse(file_path, media_type='application/pdf', filename=filename)

# ==========================================
# 3. 파일 삭제 및 벡터 DB 갱신 API (✨ 신규 추가)
# ==========================================
@router.delete("/files/{filename}")
def delete_file(filename: str):
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    os.remove(file_path) # 1. 물리적 파일 삭제
    
    try:
        # 2. 파일이 지워진 상태로 FAISS 벡터 DB 새로고침
        rag_engine.vectorstore = rag_engine.init_vectorstore()
        rag_engine.retriever = rag_engine.vectorstore.as_retriever(search_kwargs={"k": 5})
        return {"message": f"'{filename}' 삭제 및 지식베이스 갱신 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 갱신 실패: {str(e)}")

# ==========================================
# 4. 파일 업로드 API
# ==========================================
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    file.file.seek(0, os.SEEK_END)
    file_size_mb = file.file.tell() / (1024 * 1024)
    file.file.seek(0)
    
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=413, detail="파일 용량 초과")

    if get_folder_size_mb(DATA_DIR) + file_size_mb > MAX_FOLDER_CAPACITY_MB:
        raise HTTPException(status_code=413, detail="서버 용량 초과")

    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
        split_docs = text_splitter.split_documents(docs)
        
        # 신규 문서를 기존 DB에 추가
        rag_engine.vectorstore.add_documents(split_docs)
        return {"message": f"'{file.filename}' 인덱싱 완료", "capacity": f"{get_folder_size_mb(DATA_DIR):.1f}MB / {MAX_FOLDER_CAPACITY_MB}MB"}
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 5. RAG 챗봇 API
# ==========================================
class ChatMessage(BaseModel):
    message: str
    provider: str = "ollama_qwen3"

rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "제공된 문서 내용을 바탕으로 질문에 답하세요. 문서에 없는 내용은 모른다고 답하세요.\n\n[문서]\n{context}"),
    ("human", "{question}")
])

def format_docs(docs): return "\n\n".join(doc.page_content for doc in docs)

@router.post("/chat")
async def chat_with_docs(req: ChatMessage):
    async def generate():
        try:
            current_llm = get_llm(provider=req.provider, temperature=0.5)
            
            answer_chain = (
                RunnableLambda(lambda x: {"context": format_docs(x["docs"]), "question": x["question"]})
                | rag_prompt
                | current_llm
                | StrOutputParser()
            )
            
            rag_chain_with_sources = (
                # 💡 항상 최신화된 동적 retriever 참조
                RunnableParallel(docs=rag_engine.retriever, question=RunnablePassthrough())
                .assign(answer=answer_chain)
            )

            retrieved_result = rag_chain_with_sources.invoke(req.message)
            async for chunk in answer_chain.astream({"docs": retrieved_result["docs"], "question": req.message}):
                yield chunk
        except Exception as e:
            yield f"\n\n⚠️ 답변 생성 오류: {str(e)}"
    return StreamingResponse(generate(), media_type="text/event-stream")
