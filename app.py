import sys
import os

# Đảm bảo console Windows in được tiếng Việt UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.AI_service import AIService

app = FastAPI(title="Hệ Thống Kể Chuyện & Đố Vui Thiếu Nhi")

# Khởi tạo AI Service điều phối
service = AIService(prompt_yaml_path="static/Prompt.yaml")

# Mount thư mục tĩnh web
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
def serve_index():
    """Phục vụ giao diện người dùng chính."""
    return FileResponse("web/index.html")

class StoryRequest(BaseModel):
    age_group: str = "3-5"
    topic: str
    language: str = "Tiếng Việt"

class AnswerRequest(BaseModel):
    user_answer: str

@app.post("/api/generate")
def generate_story_endpoint(req: StoryRequest):
    """API sinh truyện và câu đố theo vòng lặp đa Agent."""
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Chủ đề không được để trống")

    result = service.generate_safe_story(
        age_group=req.age_group,
        topic=req.topic.strip(),
        language=req.language
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Lỗi tạo câu chuyện"))

    return result

@app.post("/api/answer")
def evaluate_answer_endpoint(req: AnswerRequest):
    """API đánh giá câu trả lời của bé với kiểm duyệt an toàn 2 chiều."""
    answer_text = req.user_answer.strip()
    if not answer_text:
        raise HTTPException(status_code=400, detail="Câu trả lời không được để trống")

    result = service.evaluate_child_answer(answer_text)
    return result

if __name__ == "__main__":
    import uvicorn
    print("\n[MÁY CHỦ] Khởi động Web App tại địa chỉ: http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
