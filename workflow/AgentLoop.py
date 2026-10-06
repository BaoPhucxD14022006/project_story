import json

class AgentLoop:
    """
    Quy trình vòng lặp 3 Agent:
    Sinh truyện -> Kiểm thử -> Sinh câu hỏi -> Kiểm thử -> Sinh đáp án -> Kiểm thử -> Trả kết quả cuối cùng
    """

    def __init__(self, story_agent, answer_agent, safety_agent, prompt_config: dict, max_retries: int = 3, verbose: bool = False):
        self.story_agent = story_agent
        self.answer_agent = answer_agent
        self.safety_agent = safety_agent
        self.prompt_config = prompt_config
        self.max_retries = max_retries
        self.verbose = verbose

    def _log(self, message: str):
        """In log chỉ khi verbose được bật."""
        if self.verbose:
            print(message)

    def _clean_and_parse_json(self, raw_text: str) -> dict:
        """Làm sạch chuỗi JSON, loại bỏ markdown fence nếu có và parse sang dict."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()
        # Tìm vị trí bắt đầu và kết thúc của JSON object
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]
        return json.loads(cleaned)

    def _loop_story(self, age_group: str, topic: str, language: str) -> dict:
        """Vòng lặp sinh truyện và kiểm thử truyện."""
        template = self.prompt_config.get("story_agent", {}).get("story_template")
        if not template:
            template = self.prompt_config.get("story_agent", {}).get("user_template", "")

        feedback = None
        for attempt in range(1, self.max_retries + 1):
            self._log(f"[BƯỚC 1/3] Sinh truyện (Lần thử {attempt}/{self.max_retries})...")
            prompt = template.format(age_group=age_group, topic=topic, language=language)
            if feedback:
                prompt += f"\n\nLưu ý từ lần kiểm thử trước: Nội dung trước bị từ chối vì '{feedback}'. Hãy khắc phục lỗi này."

            raw_story = self.story_agent.generation(prompt)
            safety_res = self.safety_agent.check(raw_story, context_type="story")

            if safety_res.get("is_safe", False):
                try:
                    story_dict = self._clean_and_parse_json(raw_story)
                    self._log("[KIỂM THỬ 1] Truyện đạt chuẩn an toàn.")
                    return story_dict
                except Exception:
                    feedback = "Định dạng đầu ra không phải JSON hợp lệ"
            else:
                feedback = safety_res.get("reason", "Nội dung vi phạm tiêu chuẩn an toàn")
                self._log(f"[CẢNH BÁO] Truyện chưa đạt: {feedback}. Tiến hành sinh lại...")

        return None

    def _loop_question(self, story: str, language: str) -> dict:
        """Vòng lặp sinh câu hỏi và kiểm thử câu hỏi."""
        template = self.prompt_config.get("story_agent", {}).get("question_template")
        feedback = None

        for attempt in range(1, self.max_retries + 1):
            self._log(f"[BƯỚC 2/3] Sinh câu hỏi từ truyện (Lần thử {attempt}/{self.max_retries})...")
            prompt = template.format(story=story, language=language)
            if feedback:
                prompt += f"\n\nLưu ý từ lần kiểm thử trước: Câu hỏi trước bị từ chối vì '{feedback}'. Hãy khắc phục lỗi này."

            raw_question = self.story_agent.generation(prompt)
            safety_res = self.safety_agent.check(raw_question, context_type="question")

            if safety_res.get("is_safe", False):
                try:
                    question_dict = self._clean_and_parse_json(raw_question)
                    self._log("[KIỂM THỬ 2] Câu hỏi đạt chuẩn an toàn.")
                    return question_dict
                except Exception:
                    feedback = "Định dạng đầu ra không phải JSON hợp lệ"
            else:
                feedback = safety_res.get("reason", "Câu hỏi chưa đạt chuẩn an toàn")
                self._log(f"[CẢNH BÁO] Câu hỏi chưa đạt: {feedback}. Tiến hành sinh lại...")

        return None

    def _loop_answer(self, story: str, question: str, language: str) -> dict:
        """Vòng lặp sinh đáp án và kiểm thử đáp án."""
        template = self.prompt_config.get("answer_agent", {}).get("answer_template")
        feedback = None

        for attempt in range(1, self.max_retries + 1):
            self._log(f"[BƯỚC 3/3] Sinh đáp án chuẩn (Lần thử {attempt}/{self.max_retries})...")
            prompt = template.format(story=story, question=question, language=language)
            if feedback:
                prompt += f"\n\nLưu ý từ lần kiểm thử trước: Đáp án trước bị từ chối vì '{feedback}'. Hãy khắc phục lỗi này."

            raw_answer = self.answer_agent.generate_standard_answer(prompt)
            safety_res = self.safety_agent.check(raw_answer, context_type="answer")

            if safety_res.get("is_safe", False):
                try:
                    answer_dict = self._clean_and_parse_json(raw_answer)
                    self._log("[KIỂM THỬ 3] Đáp án đạt chuẩn an toàn.")
                    return answer_dict
                except Exception:
                    feedback = "Định dạng đầu ra không phải JSON hợp lệ"
            else:
                feedback = safety_res.get("reason", "Đáp án chưa đạt chuẩn an toàn")
                self._log(f"[CẢNH BÁO] Đáp án chưa đạt: {feedback}. Tiến hành sinh lại...")

        return None

    def run(self, age_group: str, topic: str, language: str = "Tiếng Việt") -> dict:
        """Thực thi toàn bộ quy trình vòng lặp 3 Agent."""
        # 1. Sinh truyện -> Kiểm thử truyện
        story_data = self._loop_story(age_group=age_group, topic=topic, language=language)
        if not story_data:
            return {
                "success": False,
                "error": "Không thể tạo câu chuyện an toàn sau số lần thử tối đa."
            }

        # 2. Sinh câu hỏi -> Kiểm thử câu hỏi
        question_data = self._loop_question(story=story_data["story"], language=language)
        if not question_data:
            return {
                "success": False,
                "error": "Không thể tạo câu hỏi an toàn sau số lần thử tối đa."
            }

        # 3. Sinh đáp án -> Kiểm thử đáp án
        answer_data = self._loop_answer(
            story=story_data["story"],
            question=question_data["riddle"],
            language=language
        )
        if not answer_data:
            return {
                "success": False,
                "error": "Không thể tạo đáp án an toàn sau số lần thử tối đa."
            }

        # 4. Đóng gói kết quả cuối cùng
        final_result = {
            "title": story_data.get("title", "Câu chuyện dành cho bé"),
            "age_group": age_group,
            "topic": topic,
            "language": language,
            "characters": story_data.get("characters", []),
            "story": story_data.get("story", ""),
            "lesson": story_data.get("lesson", ""),
            "riddle": question_data.get("riddle", ""),
            "hint": question_data.get("hint") or answer_data.get("hint", ""),
            "answer": answer_data.get("answer", ""),
            "explanation": answer_data.get("explanation", "")
        }

        # Nạp bối cảnh cho AnswerAgent để sẵn sàng trò chuyện với bé
        self.answer_agent.set_riddle_context(
            story=final_result["story"],
            question=final_result["riddle"],
            standard_answer=final_result["answer"]
        )

        return {
            "success": True,
            "data": final_result
        }

    def evaluate_user_answer(self, user_answer: str) -> dict:
        """
        Quy trình đánh giá câu trả lời của người dùng:
        1. Kiểm thử an toàn câu trả lời của bé (User input moderation).
        2. Nếu an toàn -> AnswerAgent phân tích và đưa ra phản hồi.
        3. Kiểm thử an toàn phản hồi của AnswerAgent (Tutor output moderation).
        4. Trả kết quả hiển thị cho bé.
        """
        # 1. Kiểm tra an toàn câu trả lời của người dùng
        user_safety = self.safety_agent.check(user_answer, context_type="user_input")
        if not user_safety.get("is_safe", False):
            reason = user_safety.get("reason", "Nội dung không phù hợp với chuẩn mực thiếu nhi")
            self._log(f"[CẢNH BÁO AN TOÀN] Câu trả lời của người dùng vi phạm: {reason}")
            return {
                "success": False,
                "is_safe": False,
                "error": "Câu trả lời của người dùng vi phạm tiêu chuẩn an toàn",
                "violation": user_safety.get("violation_category"),
                "feedback": "Bé ơi, lời nói này chưa ngoan đâu nhé! Chúng mình hãy dùng những từ ngữ lễ phép, đáng yêu để cùng giải câu đố nào!",
                "safety_check": user_safety
            }

        # 2. Answer Agent đưa ra phản hồi
        raw_feedback = self.answer_agent.evaluate_answer(user_answer)

        # 3. Safety Agent kiểm tra mức độ an toàn của phản hồi
        agent_safety = self.safety_agent.check(raw_feedback, context_type="answer")
        if not agent_safety.get("is_safe", False):
            return {
                "success": False,
                "is_safe": False,
                "error": "Phản hồi chưa đảm bảo an toàn cho trẻ",
                "feedback": "Bé ơi, câu trả lời của bé rất thú vị! Hãy thử suy nghĩ thêm một chút nhé!",
                "safety_check": agent_safety
            }

        # 4. Trích xuất nội dung hiển thị
        display_feedback = raw_feedback
        answer_data = None
        try:
            cleaned = raw_feedback.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
            if cleaned.startswith("{") and cleaned.endswith("}"):
                answer_data = json.loads(cleaned)
                display_feedback = (
                    answer_data.get("feedback")
                    or answer_data.get("praise_or_encouragement")
                    or raw_feedback
                )
        except Exception:
            display_feedback = raw_feedback

        return {
            "success": True,
            "is_safe": True,
            "feedback": display_feedback,
            "data": answer_data,
            "safety_check": agent_safety
        }
