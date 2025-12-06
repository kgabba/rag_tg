from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from models.model import TextIn
from db.utils import conn_to_db
from llm.deps import chunk_and_embed_to_db, llm, get_top_k_chunks, chunk_and_embed_file
import os

ADMIN_TG_ID = os.getenv("ADMIN_TG_ID")
router_llm = APIRouter(prefix='/llm')

MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 МБ


@router_llm.post("/embed")
def create_embeddings(payload: TextIn, conn = Depends(conn_to_db), tg_id: str = Header(None)):
    if tg_id != ADMIN_TG_ID:
        raise HTTPException(403, "Нет доступа")
    inserted = chunk_and_embed_to_db(payload.text, conn)
    return {"status": "ok", "chunks_added_counts": inserted}


@router_llm.post("/embed_file")
async def create_embeddings_from_file(
    file: UploadFile = File(...),
    conn = Depends(conn_to_db),
):
    try:
        content = await file.read()

        # лимит 4 МБ
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Файл больше 4 МБ")

        inserted = chunk_and_embed_file(content, file.filename, conn)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки файла: {e}")

    return {
        "status": "ok",
        "filename": file.filename,
        "chunks_added_counts": inserted,
    }


@router_llm.post("/ask")
def ask_llm(payload: TextIn, conn = Depends(conn_to_db)):
    question = payload.text

    chunks = get_top_k_chunks(question, conn, k=5)

    if not chunks:
        return {
            "answer": "В базе пока нет данных для ответа.",
            "context_used": [],
        }

    context = "\n\n---\n\n".join(chunks)

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

    response = llm.invoke(prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    return {
        "answer": answer,
        "context_used": chunks,
    }
