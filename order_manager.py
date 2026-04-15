import os
import json


class OrderManager:
    def __init__(self):
        self.history = []
        self.load_history()

    def load_history(self):
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = []

    def save_history(self):
        try:
            with open("history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Save history error:", e)

    # GIỮ LẠI ĐỂ KHÔNG LỖI CALL TỪ POS
    def save_to_excel(self, order):
        pass