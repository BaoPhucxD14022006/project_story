class Story_Agent:
    """Agent chịu trách nhiệm sáng tác câu chuyện, câu đố và đáp án."""
    def __init__(self, client, model, system_prompt=None, temperature=0.7, max_tokens=1024, max_memory_turns=5):
        self.client = client
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_memory_turns = max_memory_turns
        # Bộ nhớ lưu lại các lượt sáng tác trước đó
        self.history = []

    def generation(self, prompt_user: str) -> str:
        """Sinh câu chuyện mới dựa trên yêu cầu và lịch sử các truyện trước đó."""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # Nạp bộ nhớ các lượt sáng tác gần nhất
        messages.extend(self.history[- (self.max_memory_turns * 2):])
        
        # Thêm prompt hiện tại
        messages.append({"role": "user", "content": prompt_user})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Đã sửa lỗi: .message.content thay vì .messages.content
        content = response.choices[0].message.content

        # Lưu vào bộ nhớ
        self.history.append({"role": "user", "content": prompt_user})
        self.history.append({"role": "assistant", "content": content})
        return content

    def clear_memory(self):
        """Xóa bộ nhớ khi bắt đầu phiên mới hoàn toàn."""
        self.history = []