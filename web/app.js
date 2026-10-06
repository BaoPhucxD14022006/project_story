document.addEventListener("DOMContentLoaded", () => {
    // State
    let selectedAge = "3-5";
    let selectedTopic = "Khám phá vũ trụ cùng bạn Gấu Nâu";

    // Elements
    const ageButtons = document.querySelectorAll(".age-btn");
    const topicTags = document.querySelectorAll(".topic-tag");
    const customTopicInput = document.getElementById("custom-topic");
    const btnGenerate = document.getElementById("btn-generate");
    const pipelineStatus = document.getElementById("pipeline-status");

    const storySection = document.getElementById("story-section");
    const storyTitle = document.getElementById("story-title");
    const characterTags = document.getElementById("character-tags");
    const storyBody = document.getElementById("story-body");
    const storyLesson = document.getElementById("story-lesson");
    const storyRiddle = document.getElementById("story-riddle");
    const storyHint = document.getElementById("story-hint");

    const chatSection = document.getElementById("chat-section");
    const chatMessages = document.getElementById("chat-messages");
    const chatForm = document.getElementById("chat-form");
    const userAnswerInput = document.getElementById("user-answer-input");
    const btnSubmitAnswer = document.getElementById("btn-submit-answer");

    // Lựa chọn lứa tuổi
    ageButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            ageButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedAge = btn.dataset.age;
        });
    });

    // Lựa chọn chủ đề gợi ý
    topicTags.forEach(tag => {
        tag.addEventListener("click", () => {
            topicTags.forEach(t => t.classList.remove("active"));
            tag.classList.add("active");
            selectedTopic = tag.dataset.topic;
            customTopicInput.value = "";
        });
    });

    // Nhập chủ đề tùy chỉnh
    customTopicInput.addEventListener("input", (e) => {
        if (e.target.value.trim()) {
            topicTags.forEach(t => t.classList.remove("active"));
            selectedTopic = e.target.value.trim();
        }
    });

    // Gửi yêu cầu sinh truyện
    btnGenerate.addEventListener("click", async () => {
        const topic = customTopicInput.value.trim() || selectedTopic;
        if (!topic) {
            alert("Vui lòng chọn hoặc nhập chủ đề câu chuyện.");
            return;
        }

        btnGenerate.disabled = true;
        pipelineStatus.classList.remove("hidden");

        try {
            const response = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    age_group: selectedAge,
                    topic: topic,
                    language: "Tiếng Việt"
                })
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                alert("[LỖI]: " + (result.detail || result.error || "Không thể tạo truyện."));
                return;
            }

            const data = result.data;
            renderStory(data);

            // Mở khu vực chat và cuộn tới truyện
            chatSection.classList.remove("hidden");
            chatMessages.innerHTML = `
                <div class="message message-bot">
                    <div class="message-meta">Gia sư AI</div>
                    <div class="message-content">Chào bé yêu! Bé đã đọc xong câu chuyện '${data.title}' chưa? Hãy thử đoán câu trả lời cho câu đố xem nào!</div>
                </div>
            `;

            storySection.scrollIntoView({ behavior: "smooth" });

        } catch (error) {
            alert("[LỖI KẾT NỐI]: Không thể kết nối tới máy chủ AI.");
            console.error(error);
        } finally {
            btnGenerate.disabled = false;
            pipelineStatus.classList.add("hidden");
        }
    });

    // Render thông tin truyện
    function renderStory(data) {
        storyTitle.textContent = data.title || "Câu chuyện thiếu nhi";
        storyBody.textContent = data.story || "";
        storyLesson.textContent = data.lesson || "Mỗi câu chuyện đều đem lại một bài học ý nghĩa.";
        storyRiddle.textContent = data.riddle || "";

        if (data.hint) {
            storyHint.textContent = "Gợi ý cho bé: " + data.hint;
            storyHint.classList.remove("hidden");
        } else {
            storyHint.classList.add("hidden");
        }

        // Render nhân vật
        characterTags.innerHTML = "";
        if (data.characters && Array.isArray(data.characters)) {
            data.characters.forEach(char => {
                const tag = document.createElement("span");
                tag.className = "character-tag";
                tag.textContent = char;
                characterTags.appendChild(tag);
            });
        }

        storySection.classList.remove("hidden");
    }

    // Xử lý gửi câu trả lời của bé
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const answerText = userAnswerInput.value.trim();
        if (!answerText) return;

        // Thêm tin nhắn của bé vào khung chat
        appendMessage("user", "Bé trả lời", answerText);
        userAnswerInput.value = "";
        btnSubmitAnswer.disabled = true;

        try {
            const response = await fetch("/api/answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_answer: answerText })
            });

            const result = await response.json();

            if (!response.ok) {
                appendMessage("warning", "Thông báo", result.detail || "Đã xảy ra lỗi khi kiểm tra câu trả lời.");
                return;
            }

            // Nếu câu trả lời bị vi phạm an toàn
            if (result.is_safe === false) {
                appendMessage("warning", "Nhắc nhở an toàn", result.feedback);
            } else {
                // Phản hồi bình thường của Gia sư AI
                appendMessage("bot", "Gia sư AI", result.feedback);
            }

        } catch (error) {
            appendMessage("warning", "Lỗi kết nối", "Không thể gửi phản hồi tới Gia sư AI.");
            console.error(error);
        } finally {
            btnSubmitAnswer.disabled = false;
            userAnswerInput.focus();
        }
    });

    // Thêm tin nhắn vào hộp chat
    function appendMessage(senderType, metaText, contentText) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message message-${senderType}`;

        const metaDiv = document.createElement("div");
        metaDiv.className = "message-meta";
        metaDiv.textContent = metaText;

        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        contentDiv.textContent = contentText;

        msgDiv.appendChild(metaDiv);
        msgDiv.appendChild(contentDiv);

        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
