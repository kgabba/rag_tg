from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from models.model import TextIn
from db.utils import conn_to_db
from llm.deps import chunk_and_embed_to_db, llm, get_top_k_chunks, chunk_and_embed_file
from auth.deps import require_roles

router_llm = APIRouter(prefix='/llm')

@router_llm.post("/embed", dependencies=[Depends(require_roles(["admin"]))])
def create_embeddings(payload: TextIn, conn = Depends(conn_to_db)):
    inserted = chunk_and_embed_to_db(payload.text, conn)
    return {"status": "ok", "chunks_added_counts": inserted}

@router_llm.post(
    "/embed_file",
    dependencies=[Depends(require_roles(["admin"]))],
)
async def create_embeddings_from_file(
    file: UploadFile = File(...),
    conn = Depends(conn_to_db),
):
    try:
        content = await file.read()
        inserted = chunk_and_embed_file(content, file.filename, conn)
    except ValueError as e:
        # например, неподдерживаемый формат
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {e}")

    return {
        "status": "ok",
        "filename": file.filename,
        "chunks_added_counts": inserted,
    }



@router_llm.post("/ask", dependencies=[Depends(require_roles(["user"]))])
def ask_llm(payload: TextIn, conn = Depends(conn_to_db)):
    question = payload.text

    # 1. достаём top-2 чанка из БД
    chunks = get_top_k_chunks(question, conn, k=2)

    if not chunks:
        return {
            "answer": "В базе пока нет данных для ответа.",
            "context_used": [],
        }

    context = "\n\n---\n\n".join(chunks)

    # 2. собираем промпт с жёстким правилом "не придумывай"
    prompt = f"""
Ты — помощник, который отвечает ТОЛЬКО на основе приведённого контекста.

Контекст:
{context}

Вопрос пользователя: {question}

Правила:
- Используй только факты из контекста.
- Если в контексте нет нужной информации, ответь дословно: "Нет такой информации в базе".
- Не выдумывай и не добавляй внешние знания.
- Отвечай кратко, по-русски.
"""

    # 3. зовём LLM
    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    return {
        "answer": answer,
        "context_used": chunks,
    }