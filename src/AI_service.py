import json
import yaml
from openai import OpenAI
from config import API_KEY, NVIDIA_Model
from agent import Story_Agent, Answer_Agent, Safety_Agent
from workflow.AgentLoop import AgentLoop

class AIService:
    """Dịch vụ khởi tạo và điều phối các Agent thiếu nhi."""

    def __init__(self, prompt_yaml_path: str = "static/Prompt.yaml"):
        # Khởi tạo client kết nối NVIDIA API
        self.client = OpenAI(
            api_key=API_KEY.NVIDIA,
            base_url=NVIDIA_Model.URL,
        )

        # Đọc cấu hình Prompt từ YAML
        self.prompt_yaml_path = prompt_yaml_path
        self.prompt_config = self._load_prompt_yaml()

        # Nạp System Prompt cho từng Agent từ YAML
        story_system = self.prompt_config.get("story_agent", {}).get("system_prompt")
        answer_system = self.prompt_config.get("answer_agent", {}).get("system_prompt")
        safety_system = self.prompt_config.get("safety_agent", {}).get("system_prompt")

        # Khởi tạo 3 Agent
        self.story_agent = Story_Agent(
            client=self.client,
            model=NVIDIA_Model.LLM_MODEL,
            system_prompt=story_system,
            temperature=0.7
        )

        self.answer_agent = Answer_Agent(
            client=self.client,
            model=NVIDIA_Model.LLM_MODEL,
            system_prompt=answer_system,
            temperature=0.3
        )

        self.safety_agent = Safety_Agent(
            client=self.client,
            model=NVIDIA_Model.SATEFY_MODEL,
            system_prompt=safety_system,
            temperature=0.0
        )

        # Khởi tạo AgentLoop để xử lý quy trình vòng lặp sinh truyện và kiểm thử
        self.agent_loop = AgentLoop(
            story_agent=self.story_agent,
            answer_agent=self.answer_agent,
            safety_agent=self.safety_agent,
            prompt_config=self.prompt_config
        )

    def _load_prompt_yaml(self) -> dict:
        with open(self.prompt_yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate_safe_story(self, age_group: str, topic: str, language: str = "Tiếng Việt") -> dict:
        """Ủy thác cho AgentLoop xử lý toàn bộ vòng lặp sinh và kiểm thử."""
        return self.agent_loop.run(
            age_group=age_group,
            topic=topic,
            language=language
        )

    def evaluate_child_answer(self, user_answer: str) -> dict:
        """Ủy thác cho AgentLoop đánh giá câu trả lời của bé kèm kiểm duyệt 2 chiều."""
        return self.agent_loop.evaluate_user_answer(user_answer)

