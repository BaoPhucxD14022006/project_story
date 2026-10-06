import sys
import os

# Đảm bảo console Windows in được tiếng Việt UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.AI_service import AIService

def main():
    service = AIService(prompt_yaml_path="static/Prompt.yaml")
    service.agent_loop.verbose = True

    print("\n" + "=" * 65)
    print("[KHỞI TẠO] ĐANG TẠO CÂU CHUYỆN VÀ CÂU ĐỐ CHO BÉ...")
    print("=" * 65)

    # 1. Sinh truyện và câu đố theo quy trình vòng lặp 3 agent
    result = service.generate_safe_story(
        age_group="6-8",
        topic="Khám phá vũ trụ cùng bạn Gấu",
        language="Tiếng Việt"
    )

    if not result["success"]:
        print("[LỖI]:", result.get("error"))
        return

    story_data = result["data"]
    print(f"\n[TIÊU ĐỀ]: {story_data.get('title', 'Chuyến phiêu lưu của Gấu')}")
    print(f"\n{story_data['story']}")
    print("\n" + "-" * 65)
    print(f"[CÂU ĐỐ]: {story_data['riddle']}")
    print("-" * 65)

    # 2. Vòng lặp tương tác: Cho phép bé nhập câu trả lời thực tế
    print("[HƯỚNG DẪN] Hãy nhập câu trả lời của bé để trò chuyện với Gia sư AI (gõ 'q' để thoát):\n")
    turn = 1
    while True:
        try:
            user_input = input(f"[Lượt {turn}] Bé trả lời: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nTạm biệt bé!")
            break

        if not user_input:
            continue
        if user_input.lower() in ["q", "exit", "quit", "thoat"]:
            print("\nTạm biệt bé, hẹn gặp lại ở câu chuyện tiếp theo!")
            break

        # Đánh giá câu trả lời
        eval_result = service.evaluate_child_answer(user_input)
        print(f"\n[Gia sư AI]:\n{eval_result['feedback']}")
        print("\n" + "-" * 65)
        turn += 1

if __name__ == "__main__":
    main()
