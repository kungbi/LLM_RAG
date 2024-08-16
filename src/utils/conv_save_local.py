import os
import json
from typing import List, Dict


class MessageManager:
    def __init__(self, base_path: str = "./conv"):
        self.base_path = base_path

    def save_message(self, tab: str, message: Dict):
        path = os.path.join(self.base_path, f"Chat_{tab}", "messages")
        os.makedirs(path, exist_ok=True)

        # 메시지 파일 경로
        message_file = os.path.join(path, "messages.json")

        # 기존 메시지를 불러오기
        if os.path.exists(message_file):
            with open(message_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
        else:
            messages = []  # 메시지 파일이 없으면 빈 리스트 생성

        # 새 메시지 추가
        messages.append(message)

        # 전체 메시지 목록 저장
        with open(message_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    def load_messages(self, tab: str) -> List[Dict]:
        path = os.path.join(self.base_path, f"Chat_{tab}", "messages", "messages.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def clear_messages(self, tab: str):
        path = os.path.join(self.base_path, tab, "messages", "messages.json")
        if os.path.exists(path):
            os.remove(path)