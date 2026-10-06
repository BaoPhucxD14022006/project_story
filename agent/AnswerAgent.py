class Answer_Agent:
    """Agent chịu trách nhiệm đánh giá câu trả lời của trẻ, đưa ra nhận xét hoặc gợi ý bổ sung."""
    def __init__(self, client, model, system_prompt=None, temperature=0.3, max_tokens=1024, max_memory_turns=6):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_memory_turns = max_memory_turns
        
        # Bối cảnh câu đố hiện tại
        self.current_context = None
        # Bộ nhớ các lượt đoán và gợi ý của phiên đố vui hiện tại
        self.chat_history = []

    def set_riddle_context(self, story: str, question: str, standard_answer: str):
        """Thiết lập câu chuyện và câu đố mới, đồng thời làm mới bộ nhớ đối thoại."""
        self.current_context = {
            "story": story,
            "question": question,
            "standard_answer": standard_answer
        }
        self.chat_history = []

    def generate_standard_answer(self, prompt_user: str) -> str:
        """Sinh đáp án chuẩn dựa trên truyện và câu đố."""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt_user})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content

    def evaluate_answer(self, user_answer: str) -> str:
        """Đánh giá câu trả lời của bé dựa trên bối cảnh và các lần đoán trước đó."""
        if not self.current_context:
            raise ValueError("Chưa thiết lập bối cảnh câu đố. Hãy gọi set_riddle_context() trước.")

        # Lắp ghép prompt hệ thống có bối cảnh
        context_prompt = (
            f"BỐI CẢNH CÂU CHUYỆN:\n{self.current_context['story']}\n\n"
            f"CÂU ĐỐ ĐẶT RA:\n{self.current_context['question']}\n\n"
            f"ĐÁP ÁN CHUẨN:\n{self.current_context['standard_answer']}\n\n"
            "NHIỆM VỤ: Xem xét câu trả lời của bé. Nếu đúng, hãy khen ngợi nhiệt tình. "
            "Nếu chưa đúng, hãy khích lệ nhẹ nhàng và đưa ra 1 gợi ý nhỏ dựa trên câu chuyện để bé đoán tiếp."
        )

        messages = [
            {"role": "system", "content": f"{self.system_prompt}\n\n{context_prompt}"}
        ]

        # Nạp lịch sử các lượt đoán trước của bé trong phiên này
        messages.extend(self.chat_history[- (self.max_memory_turns * 2):])

        # Thêm câu trả lời mới nhất của bé
        messages.append({"role": "user", "content": f"Bé trả lời: {user_answer}"})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Đã sửa lỗi: .message.content
        feedback = response.choices[0].message.content

        # Lưu lại lượt đối thoại vào bộ nhớ
        self.chat_history.append({"role": "user", "content": f"Bé trả lời: {user_answer}"})
        self.chat_history.append({"role": "assistant", "content": feedback})
        return feedback

    def clear_memory(self):
        """Xóa trắng bộ nhớ của lượt chơi này."""
        self.current_context = None
        self.chat_history = []
