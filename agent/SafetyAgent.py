import json
import time

class Safety_Agent:
    """Agent chịu trách nhiệm kiểm duyệt an toàn nội dung cho cả câu chuyện (Story) và phản hồi (Answer)."""
    def __init__(self, client, model, system_prompt=None, temperature=0.0, max_tokens=512):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Bộ nhớ lưu vết kiểm duyệt (Audit Log Memory)
        self.audit_log = []

    def _default_system_prompt(self) -> str:
        return """
Bạn là Chuyên gia Kiểm duyệt An toàn Nội dung Thiếu nhi (Child Safety Content Moderator).
NHIỆM VỤ: Phân tích nội dung được cung cấp và xác định xem có an toàn tuyệt đối cho trẻ em hay không.

QUY TẮC CẤM (ZERO-TOLERANCE):
1. Bạo lực, vũ khí, máu me, tự hại, đánh đấm.
2. Nội dung người lớn, gợi dục, 18+, tình cảm không phù hợp lứa tuổi.
3. Tên người thật (chính khách, người nổi tiếng, PII).
4. Kinh dị, hù dọa, ma quỷ, gây ám ảnh sợ hãi.
5. Ngôn từ thô tục, phân biệt đối xử, thù ghét, nhạy cảm chính trị.

YÊU CẦU ĐẦU RA:
BẮT BUỘC trả về duy nhất một chuỗi JSON chuẩn (không dùng markdown fence ```json), dạng:
{
  "is_safe": true/false,
  "risk_level": "NONE" | "LOW" | "HIGH",
  "violation_category": null hoặc "violence" | "adult" | "real_name" | "horror" | "hate",
  "reason": "Giải thích ngắn gọn lý do vì sao an toàn hoặc vì sao vi phạm"
}
"""

    def check(self, content_to_check: str, context_type: str) -> dict:
        """
        Kiểm tra mức độ an toàn của nội dung.
        :param content_to_check: Chuỗi câu chuyện từ Story_Agent hoặc lời giải từ Answer_Agent.
        :param context_type: "story" hoặc "answer" (hoặc "user_input").
        :return: Dict kết quả {"is_safe": bool, "risk_level": str, "violation_category": str, "reason": str}
        """
        user_prompt = f"LOẠI NỘI DUNG CẦN DUYỆT: [{context_type.upper()}]\nNỘI DUNG:\n{content_to_check}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Đã sửa lỗi: .message.content thay vì .messages.content
        raw_output = response.choices[0].message.content.strip()

        # Parse kết quả JSON an toàn
        try:
            # Loại bỏ markdown code fence nếu model vô tình sinh ra
            cleaned_output = raw_output
            if cleaned_output.startswith("```"):
                cleaned_output = cleaned_output.strip("`")
                if cleaned_output.startswith("json"):
                    cleaned_output = cleaned_output[4:].strip()
            result = json.loads(cleaned_output)
        except Exception:
            # Fallback an toàn nếu parse JSON thất bại
            is_safe = "is_safe\": true" in raw_output.lower() or "an toàn" in raw_output.lower()
            result = {
                "is_safe": is_safe,
                "risk_level": "NONE" if is_safe else "HIGH",
                "violation_category": None if is_safe else "unspecified",
                "reason": raw_output
            }

        # Lưu vào bộ nhớ Audit Log
        audit_record = {
            "timestamp": time.time(),
            "context_type": context_type,
            "content_preview": content_to_check[:120] + "...",
            "result": result
        }
        self.audit_log.append(audit_record)

        return result

    def get_violations(self):
        """Lấy danh sách các nội dung bị vi phạm trong phiên làm việc."""
        return [record for record in self.audit_log if not record["result"].get("is_safe", True)]

    def clear_audit_log(self):
        """Xóa trắng lịch sử kiểm duyệt."""
        self.audit_log = []
