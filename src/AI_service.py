import json
import yaml
from openai import OpenAI
from config import API_KEY, NVIDIA_Model
from agent import Story_Agent, Answer_Agent, Safety_Agent

class AIService:
    """Dịch vụ điều phối (Orchestrator) 3 con Agent cho dự án Kể chuyện & Đố vui."""

    def __init__(self, prompt_yaml_path: str = "static/Prompt.yaml"):
        # Khởi tạo client kết nối NVIDIA API
        self.client = OpenAI(
            api_key=API_KEY.NVIDIA,
            base_url=NVIDIA_Model.URL,
        )

        # Đọc cấu hình Prompt từ YAML
        self.prompt_yaml_path = prompt_yaml_path
        self.prompt_config = self._load_prompt_yaml()

        # Khởi tạo 3 Agent
        self.story_agent = Story_Agent(
            client=self.client,
            model=NVIDIA_Model.LLM_MODEL,
            temperature=0.7
        )

        self.answer_agent = Answer_Agent(
            client=self.client,
            model=NVIDIA_Model.LLM_MODEL,
            temperature=0.3
        )

        self.safety_agent = Safety_Agent(
            client=self.client,
            model=NVIDIA_Model.SATEFY_MODEL,
            temperature=0.0
        )

    def _load_prompt_yaml(self) -> dict:
        with open(self.prompt_yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate_safe_story(self, age_group: str, topic: str, language: str = "Tiếng Việt", version: str = "v2") -> dict:
        """
        Quy trình tạo truyện:
        1. Lấy prompt v1 hoặc v2 từ YAML.
        2. Story_Agent sinh nội dung JSON.
        3. Safety_Agent kiểm duyệt nội dung vừa sinh.
        4. Nếu đạt chuẩn, thiết lập ngữ cảnh cho Answer_Agent để chuẩn bị đón nhận câu trả lời của bé.
        """
        prompt_data = self.prompt_config["prompts"].get(version, self.prompt_config["prompts"]["v2"])
        self.story_agent.system_prompt = prompt_data["system"]

        user_prompt = prompt_data["user_template"].format(
            age_group=age_group,
            topic=topic,
            language=language
        )

        # 1. Story Agent sinh nội dung
        raw_story_output = self.story_agent.generation(user_prompt)

        # 2. Safety Agent kiểm tra nội dung truyện
        safety_result = self.safety_agent.check(raw_story_output, context_type="story")
        if not safety_result.get("is_safe", False):
            return {
                "success": False,
                "error": "Nội dung vi phạm tiêu chuẩn an toàn thiếu nhi",
                "safety_detail": safety_result
            }

        # 3. Parse JSON truyện
        try:
            cleaned = raw_story_output.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
            story_dict = json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Lỗi parse JSON từ kết quả sinh truyện",
                "raw": raw_story_output
            }

        # 4. Tự động nạp bối cảnh vào Answer_Agent
        self.answer_agent.set_riddle_context(
            story=story_dict.get("story", ""),
            question=story_dict.get("riddle", ""),
            standard_answer=story_dict.get("answer", "")
        )

        return {
            "success": True,
            "data": story_dict,
            "safety_check": safety_result
        }

    def evaluate_child_answer(self, user_answer: str) -> dict:
        """
        Quy trình xử lý khi bé trả lời:
        1. Answer_Agent dùng bối cảnh câu đố & lịch sử để đưa ra nhận xét/gợi ý.
        2. Safety_Agent duyệt phản hồi của Answer_Agent để đảm bảo an toàn tuyệt đối.
        """
        # 1. Answer Agent đưa ra phản hồi
        feedback = self.answer_agent.evaluate_answer(user_answer)

        # 2. Safety Agent kiểm tra phản hồi
        safety_result = self.safety_agent.check(feedback, context_type="answer")
        if not safety_result.get("is_safe", False):
            return {
                "success": False,
                "error": "Phản hồi chưa đảm bảo an toàn cho trẻ",
                "feedback": "Bé ơi, câu trả lời của bé rất thú vị! Hãy thử suy nghĩ thêm một chút nhé!"
            }

        return {
            "success": True,
            "feedback": feedback,
            "safety_check": safety_result
        }
