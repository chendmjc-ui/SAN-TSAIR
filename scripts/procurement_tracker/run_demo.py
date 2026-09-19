"""
Phase 4 Demo 驗證：用完全虛構的供應商/報價資料跑一次完整流程，
驗證狀態機轉換與通知邏輯是否符合 docs/procurement/02_data_model.md 設計。

跑法：py -3 scripts/procurement_tracker/run_demo.py
"""
import sys
from datetime import date, timedelta

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from tracker import Store, TransitionError

PASS = []
FAIL = []


def check(label: str, condition: bool):
    (PASS if condition else FAIL).append(label)
    print(f"{'✅' if condition else '❌'} {label}")


def main():
    store = Store()  # 不 load 舊檔，每次 demo 從空白狀態開始

    print("=== 建立虛構供應商 ===")
    store.add_supplier("SUP-DEMO-1", "示範廠商A", category="gift", tier=1)
    store.add_supplier("SUP-DEMO-2", "示範廠商B", category="uniform", tier=2)

    print("\n=== 情境1：正常走完全流程直到下單 ===")
    store.add_quote("Q-DEMO-1", "SUP-DEMO-1", "虛構禮品X", reply_deadline="2099-01-01")
    store.transition("Q-DEMO-1", "quoted")
    store.transition("Q-DEMO-1", "sampling")
    store.transition("Q-DEMO-1", "deciding")
    store.transition("Q-DEMO-1", "ordered")
    check("情境1：Q-DEMO-1 最終狀態為 ordered", store.quotes["Q-DEMO-1"]["status"] == "ordered")
    check("情境1：history 完整記錄 5 個狀態", store.quotes["Q-DEMO-1"]["history"] == ["inquired", "quoted", "sampling", "deciding", "ordered"])

    print("\n=== 情境2：中途淘汰路徑 ===")
    store.add_quote("Q-DEMO-2", "SUP-DEMO-2", "虛構制服Y", reply_deadline="2099-01-01")
    store.transition("Q-DEMO-2", "quoted")
    store.transition("Q-DEMO-2", "rejected")
    check("情境2：Q-DEMO-2 最終狀態為 rejected", store.quotes["Q-DEMO-2"]["status"] == "rejected")

    print("\n=== 情境3：非法狀態轉換必須被擋下 ===")
    store.add_quote("Q-DEMO-3", "SUP-DEMO-1", "虛構禮品Z", reply_deadline="2099-01-01")
    illegal_blocked = False
    try:
        store.transition("Q-DEMO-3", "ordered")  # inquired 不能直接跳 ordered
    except TransitionError as e:
        illegal_blocked = True
        print(f"（預期中的錯誤）{e}")
    check("情境3：inquired 直接跳 ordered 被擋下", illegal_blocked)

    print("\n=== 情境4：逾期自動偵測與通知 ===")
    overdue_deadline = (date.today() - timedelta(days=3)).isoformat()
    store.add_quote("Q-DEMO-4", "SUP-DEMO-2", "虛構禮品逾期案例", reply_deadline=overdue_deadline)
    overdue_ids = store.check_overdue()
    check("情境4：Q-DEMO-4 被偵測為逾期", "Q-DEMO-4" in overdue_ids)
    check("情境4：Q-DEMO-4 狀態變成 overdue", store.quotes["Q-DEMO-4"]["status"] == "overdue")

    print("\n=== 存檔（demo_data.json，僅虛構資料）===")
    store.save()
    check("demo_data.json 已寫入", (store.__class__.load().quotes.get("Q-DEMO-1") is not None))

    print(f"\n=== 結果：{len(PASS)} 通過 / {len(FAIL)} 失敗 ===")
    if FAIL:
        print("失敗項目：", FAIL)
        raise SystemExit(1)
    print("全部情境通過，追蹤系統雛形驗證成功。")


if __name__ == "__main__":
    main()
