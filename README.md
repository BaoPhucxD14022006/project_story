# Hệ Thống Kể Chuyện & Đố Vui Thiếu Nhi (Multi-Agent Storytelling System)

Hệ thống AI tương tác dành cho trẻ em, tích hợp mô hình điều phối đa Agent (Multi-Agent System) và cơ chế tự kiểm thử an toàn nghiêm ngặt (Zero-Tolerance Child Safety Guardrail).

---

## 1. Điểm nổi bật của dự án

* **Kiến trúc 3 Agent chuyên biệt**:
  * **StoryAgent**: Đóng vai trò là Tác giả truyện thiếu nhi và Chuyên gia sư phạm, sáng tác truyện ấm áp, giàu tính giáo dục và câu đố tư duy.
  * **AnswerAgent**: Đóng vai trò là Gia sư AI thân thiện, giải đáp chuẩn xác câu đố và đồng hành, khích lệ bé khi chơi.
  * **SafetyAgent**: Đóng vai trò là AI Guardrail kiểm duyệt an toàn nội dung với tiêu chuẩn không khoan nhượng (Zero-Tolerance).
* **Vòng lặp tự kiểm thử (Evaluator-Optimizer Loop)**:
  * Quy trình tuần hoàn: `Sinh truyện -> Kiểm thử truyện -> Sinh câu hỏi -> Kiểm thử câu hỏi -> Sinh đáp án -> Kiểm thử đáp án -> Trả kết quả`.
  * Khi phát hiện lỗi hoặc nội dung chưa phù hợp, hệ thống tự động phản hồi lý do để Agent sinh lại mà không làm gián đoạn ứng dụng.
* **Kiểm duyệt an toàn 2 chiều**:
  * Kiểm duyệt toàn bộ nội dung do AI sinh ra (Truyện, Câu đố, Đáp án, Phản hồi của Gia sư).
  * Kiểm duyệt câu trả lời của người dùng (User input moderation): Nếu phát hiện ngôn từ thô tục, bạo lực hay không phù hợp, hệ thống lập tức chặn và đưa ra lời nhắc nhở lễ phép, thân thiện cho bé.
* **Giao diện Web App hiện đại**:
  * Xây dựng bằng FastAPI, HTML, Vanilla CSS và JavaScript.
  * Thiết kế trang nhã, trực quan, hỗ trợ chọn độ tuổi, chủ đề và chat tương tác trực tiếp với Gia sư AI.

---

## 2. Cấu trúc thư mục

```text
Project_Story/
│
├── agent/                      # Các Agent độc lập
│   ├── StoryAgent.py           # Agent sáng tác truyện và câu đố
│   ├── AnswerAgent.py          # Agent gia sư và giải đáp
│   ├── SafetyAgent.py          # Agent kiểm duyệt an toàn thiếu nhi
│   └── __init__.py
│
├── workflow/                   # Điều phối quy trình vòng lặp
│   ├── AgentLoop.py            # Quản lý vòng lặp sinh và kiểm thử
│   └── __init__.py
│
├── src/
│   └── AI_service.py           # Dịch vụ tích hợp và ủy thác AgentLoop
│
├── config/
│   ├── config.py               # Cấu hình API Key và Model NVIDIA
│   └── __init__.py
│
├── static/
│   └── Prompt.yaml             # Hệ thống System Prompts & User Templates
│
├── web/                        # Giao diện Web App
│   ├── index.html              # Cấu trúc trang web
│   ├── style.css               # Giao diện hiện đại (Vanilla CSS)
│   └── app.js                  # Logic tương tác phía client (Vanilla JS)
│
├── app.py                      # Máy chủ Web App (FastAPI)
├── main.py                     # Ứng dụng chạy trên giao diện dòng lệnh (CLI)
├── requirements.txt            # Danh sách thư viện phụ thuộc
├── .env                        # Biến môi trường (chứa API Key)
└── README.md                   # Tài liệu hướng dẫn dự án
```

---

## 3. Bộ quy tắc an toàn Zero-Tolerance

Hệ thống tuân thủ 6 quy tắc an toàn nghiêm ngặt để bảo vệ trẻ nhỏ:

1. **Bạo lực (Violence)**: Nghiêm cấm vũ khí, đấm đá, máu me, tự hại, tử vong, đánh đập hoặc ngược đãi động vật.
2. **Đồi trụy & Người lớn (Adult & Obscene)**: Nghiêm cấm ngôn từ thô tục, gợi dục, 18+, tình dục, khỏa thân, quấy rối.
3. **Nguy hiểm & Bắt chước có hại (Dangerous Acts)**: Cấm các hành vi trẻ có thể bắt chước gây nguy hiểm (chơi lửa, diêm, điện, leo trèo ban công/cửa sổ cao, dao kéo, uống hóa chất tẩy rửa, nuốt dị vật, đi theo người lạ, bỏ nhà đi...).
4. **Kinh dị & Hù dọa (Horror & Trauma)**: Cấm ma quỷ, bóng tối rùng rợn, hù dọa bắt cóc, nhốt phòng tối, đòn roi trừng phạt gây ác mộng.
5. **Thù ghét & Tiêu cực (Hate & Discrimination)**: Cấm miệt thị ngoại hình (body shaming), chê bai giàu nghèo, phân biệt đối xử.
6. **Tên người thật (No Real Names / PII)**: Không sử dụng tên người nổi tiếng, chính khách ngoài đời thực; chỉ dùng tên nhân vật hư cấu ngộ nghĩnh (Thỏ Trắng, Nhím Nâu, Bé Bo...).

---

## 4. Hướng dẫn cài đặt

### Yêu cầu hệ thống:
* Python 3.10 trở lên.
* Kết nối Internet để gọi API mô hình.

### Bước 1: Cài đặt thư viện phụ thuộc
Mở terminal tại thư mục dự án và chạy lệnh:
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình API Key
Tạo hoặc kiểm tra file `.env` tại thư mục gốc của dự án với nội dung:
```env
NVIDIA_API_KEY=your_nvidia_api_key_here
```

---

## 5. Hướng dẫn sử dụng

### Cách 1: Khởi chạy giao diện Web App (Khuyên dùng)
Chạy lệnh sau trong terminal:
```bash
python app.py
```
Sau đó mở trình duyệt web và truy cập địa chỉ:
```
http://127.0.0.1:8000
```

* **Chọn nhóm tuổi**: 3-5 tuổi (Mầm non), 6-8 tuổi (Tiểu học), 9-12 tuổi (Khám phá).
* **Chọn chủ đề**: Nhấp vào các thẻ chủ đề gợi ý hoặc tự nhập chủ đề theo ý muốn.
* **Tạo truyện**: Nhấn nút `Tạo Câu Chuyện Mới` để hệ thống chạy quy trình vòng lặp đa Agent.
* **Giải đố cùng Gia sư AI**: Nhập câu trả lời của bé vào khung chat bên dưới để tương tác trực tiếp.

### Cách 2: Khởi chạy giao diện dòng lệnh (CLI)
Nếu muốn chạy trực tiếp trên console/terminal:
```bash
python main.py
```

* Hệ thống sẽ tự động khởi tạo câu chuyện và đưa ra câu đố.
* Nhập câu trả lời tại dòng `[Lượt X] Bé trả lời: ` để tương tác với Gia sư AI.
* Gõ `q`, `exit` hoặc `thoat` để kết thúc phiên chơi.

---

## 6. Luồng hoạt động chi tiết của AgentLoop

1. **Bước 1 (Sinh truyện)**: `StoryAgent` nhận thông tin lứa tuổi và chủ đề để sáng tác cốt truyện, nhân vật và bài học nhân văn.
2. **Bước 2 (Kiểm thử 1)**: `SafetyAgent` kiểm định truyện. Nếu vi phạm, trả về lý do và yêu cầu `StoryAgent` viết lại (tối đa 3 lần).
3. **Bước 3 (Sinh câu hỏi)**: Sau khi truyện đạt chuẩn, `StoryAgent` tạo câu đố tư duy bám sát chi tiết then chốt trong truyện.
4. **Bước 4 (Kiểm thử 2)**: `SafetyAgent` kiểm định câu đố. Nếu vi phạm hoặc không liên quan đến truyện, yêu cầu tạo lại.
5. **Bước 5 (Sinh đáp án)**: `AnswerAgent` suy luận và đúc kết đáp án chuẩn xác cùng lời giải thích và gợi ý.
6. **Bước 6 (Kiểm thử 3)**: `SafetyAgent` kiểm định đáp án chuẩn.
7. **Bước 7 (Trả kết quả)**: Đóng gói dữ liệu hoàn chỉnh, nạp bối cảnh vào `AnswerAgent` để sẵn sàng đối thoại cùng trẻ.
8. **Bước 8 (Đối thoại & Kiểm duyệt 2 chiều)**: Khi trẻ gửi câu trả lời, `SafetyAgent` kiểm tra câu trả lời của trẻ trước. Nếu an toàn mới chuyển tiếp cho `AnswerAgent` phản hồi và kiểm duyệt lại câu trả lời của AI trước khi hiển thị.
