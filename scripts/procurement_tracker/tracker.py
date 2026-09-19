"""
贈禮品尋單採購流程 — 追蹤系統雛形（Phase 3）

比照三才網站既有 Google Apps Script 詢價表單架構
（config/google-apps-script/Code.gs：表單 -> Sheet 留底 -> LINE 推播）的
「事件觸發 -> 資料落地 -> 即時通知」三段式設計，本地 Python 版本用 JSON
檔案模擬 Sheet，notify_stub() 模擬 LINE 推播（正式上線時把這個函式換成
真正呼叫 LINE Messaging API 或改寫成 Apps Script 版本即可，資料結構不用動）。

僅供架構驗證用，資料一律是虛構 demo 資料，不得填入任何真實供應商資訊。
"""
import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "demo_data.json"

# 對應 docs/procurement/02_data_model.md 的狀態機
VALID_TRANSITIONS = {
    "inquired": {"quoted", "overdue"},
    "overdue": {"quoted"},
    "quoted": {"sampling", "rejected"},
    "sampling": {"deciding", "rejected"},
    "deciding": {"ordered", "rejected"},
    "ordered": set(),
    "rejected": set(),
}

NOTIFY_TEMPLATES = {
    "inquired": "已發送詢價給 {supplier}，期限 {deadline}",
    "overdue": "⚠️ {supplier} 報價已逾期，請跟進",
    "quoted": "{supplier} 已回報價，請前往比較",
    "sampling": "{supplier} 進入樣品評估階段",
    "deciding": "{supplier} 樣品通過，進入決策階段",
    "ordered": "{supplier} 已確認下單，轉入交期追蹤",
    "rejected": "{supplier} 已淘汰",
}


class TransitionError(Exception):
    pass


def notify_stub(event: str, supplier_name: str, **kwargs) -> str:
    """demo 模式：印出通知內容。正式上線時換成 LINE Messaging API push。"""
    msg = NOTIFY_TEMPLATES.get(event, event).format(supplier=supplier_name, **kwargs)
    print(f"[通知] {msg}")
    return msg


@dataclass
class Store:
    suppliers: dict = field(default_factory=dict)
    quotes: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path = DB_PATH) -> "Store":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(suppliers=data.get("suppliers", {}), quotes=data.get("quotes", {}))

    def save(self, path: Path = DB_PATH):
        path.write_text(
            json.dumps({"suppliers": self.suppliers, "quotes": self.quotes}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_supplier(self, supplier_id: str, name: str, category: str, tier: int = 2):
        self.suppliers[supplier_id] = {
            "supplier_id": supplier_id,
            "name": name,
            "category": category,
            "agreement_status": "unknown",
            "tier": tier,
            "created_at": datetime.now().isoformat(),
        }

    def add_quote(self, quote_id: str, supplier_id: str, product_name: str, reply_deadline: str):
        if supplier_id not in self.suppliers:
            raise ValueError(f"未知供應商 {supplier_id}")
        self.quotes[quote_id] = {
            "quote_id": quote_id,
            "supplier_id": supplier_id,
            "product_name": product_name,
            "status": "inquired",
            "reply_deadline": reply_deadline,
            "history": ["inquired"],
        }
        notify_stub("inquired", self.suppliers[supplier_id]["name"], deadline=reply_deadline)

    def transition(self, quote_id: str, new_status: str):
        quote = self.quotes[quote_id]
        current = quote["status"]
        allowed = VALID_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise TransitionError(f"不允許從「{current}」轉到「{new_status}」（合法選項：{sorted(allowed)}）")
        quote["status"] = new_status
        quote["history"].append(new_status)
        supplier_name = self.suppliers[quote["supplier_id"]]["name"]
        notify_stub(new_status, supplier_name)

    def check_overdue(self, today: date = None):
        today = today or date.today()
        overdue_ids = []
        for quote_id, quote in self.quotes.items():
            if quote["status"] == "inquired":
                deadline = date.fromisoformat(quote["reply_deadline"])
                if today > deadline:
                    self.transition(quote_id, "overdue")
                    overdue_ids.append(quote_id)
        return overdue_ids
