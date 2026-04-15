import csv
import json
import os


class OrderManager:
    def __init__(self):
        self.history = []
        self.history_file = "history.json"
        self.export_file = "orders_export.csv"
        self.load_history()

    def _normalize_int(self, value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _normalize_items(self, items):
        normalized = []

        if not isinstance(items, list):
            return normalized

        for item in items:
            if isinstance(item, dict):
                name = str(item.get("name", "")).strip()
                qty = self._normalize_int(item.get("qty", 1), 1)
                price = self._normalize_int(item.get("price", 0), 0)

                if name:
                    normalized.append({
                        "name": name,
                        "qty": qty,
                        "price": price
                    })

            elif isinstance(item, str):
                text = item.strip()
                if text:
                    normalized.append({
                        "name": text,
                        "qty": 1,
                        "price": 0
                    })

        return normalized

    def _normalize_order(self, order):
        if not isinstance(order, dict):
            return None

        time_value = str(order.get("time", "")).strip()
        payment = str(order.get("payment", "Không rõ")).strip() or "Không rõ"
        items = self._normalize_items(order.get("items", []))

        total = order.get("total")
        if total is None:
            total = sum(item["qty"] * item["price"] for item in items)

        total = self._normalize_int(total, 0)

        return {
            "time": time_value,
            "items": items,
            "total": total,
            "payment": payment
        }

    def load_history(self):
        self.history = []

        if not os.path.exists(self.history_file):
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                return

            normalized_history = []
            for order in data:
                normalized_order = self._normalize_order(order)
                if normalized_order:
                    normalized_history.append(normalized_order)

            self.history = normalized_history

        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            self.history = []

    def save_history(self):
        try:
            normalized_history = []
            for order in self.history:
                normalized_order = self._normalize_order(order)
                if normalized_order:
                    normalized_history.append(normalized_order)

            self.history = normalized_history

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print("Save history error:", e)

    def _build_items_summary(self, items):
        parts = []

        for item in self._normalize_items(items):
            line_total = item["qty"] * item["price"]
            if item["price"] > 0:
                parts.append(f"{item['name']} x{item['qty']} = {line_total}")
            else:
                parts.append(f"{item['name']} x{item['qty']}")

        return "; ".join(parts)

    # GIỮ LẠI ĐỂ KHÔNG LỖI CALL TỪ POS
    def save_to_excel(self, order):
        normalized_order = self._normalize_order(order)

        if not normalized_order:
            return

        file_exists = os.path.exists(self.export_file)
        needs_header = True

        if file_exists:
            try:
                needs_header = os.path.getsize(self.export_file) == 0
            except OSError:
                needs_header = True

        try:
            with open(self.export_file, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)

                if needs_header:
                    writer.writerow([
                        "time",
                        "payment",
                        "total",
                        "item_count",
                        "items_json",
                        "items_summary"
                    ])

                writer.writerow([
                    normalized_order["time"],
                    normalized_order["payment"],
                    normalized_order["total"],
                    len(normalized_order["items"]),
                    json.dumps(normalized_order["items"], ensure_ascii=False),
                    self._build_items_summary(normalized_order["items"])
                ])

        except Exception as e:
            print("Save export error:", e)