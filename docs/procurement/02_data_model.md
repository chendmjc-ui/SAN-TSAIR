# 贈禮品尋單採購流程 — 資料模型與狀態機（Phase 2）

> 隸屬 `docs/GOAL_procurement_architecture.md` Phase 2 產出。欄位設計參考業界常見採購/CRM
> 追蹤系統慣例，未引用 `gift-suppliers/` 內任何實際欄位或數值。

## 三個核心實體

### 1. Supplier（供應商）

| 欄位 | 型別 | 說明 |
|---|---|---|
| `supplier_id` | string | 唯一識別碼（如 `SUP-001`） |
| `name` | string | 廠商名稱 |
| `category` | enum | 業務線分類，比照型錄系統：`uniform`（制服）/ `gift`（禮贈品）/ `other` |
| `contact_name` | string | 聯絡窗口姓名 |
| `contact_channel` | string | 聯絡方式（email/電話/LINE，僅存管道類型不存實際帳密） |
| `agreement_status` | enum | `unknown` / `pending`（同意但要先看網站）/ `agreed` / `declined` |
| `tier` | int | 開發優先順序梯隊（1=第一梯隊） |
| `notes` | string | 備註 |
| `created_at` / `updated_at` | datetime | 建立/更新時間 |

### 2. Quote（報價單，一個 Supplier 可對多個 Quote）

| 欄位 | 型別 | 說明 |
|---|---|---|
| `quote_id` | string | 唯一識別碼 |
| `supplier_id` | string | 外鍵 |
| `product_name` | string | 品項名稱 |
| `moq` | int | 最小訂購量 |
| `unit_price_ex_tax` | number | 未稅單價（**內部使用，不得出現在公開網站**，呼應 `feedback_no_pricing_public` 規則） |
| `sample_fee` | number | 樣品費 |
| `lead_time_days` | int | 交期（天） |
| `status` | enum | 見下方狀態機 |
| `reply_deadline` | date | 回覆期限 |
| `quoted_at` | date | 報價日期 |

### 3. PurchaseOrder（採購單，決策通過後才產生）

| 欄位 | 型別 | 說明 |
|---|---|---|
| `po_id` | string | 唯一識別碼 |
| `quote_id` | string | 外鍵，來源報價 |
| `quantity` | int | 實際下單數量 |
| `total_amount` | number | 總金額（內部使用） |
| `payment_terms` | string | 付款條件 |
| `expected_delivery` | date | 預計交期 |
| `status` | enum | `draft` / `confirmed` / `shipped` / `received` / `cancelled` |

## 狀態機（Quote.status）

```
待聯繫 (contacted=false)
   │  發送詢價
   ▼
已詢價 (inquired) ──超過 reply_deadline 未回應──> 逾期提醒 (overdue)
   │  收到廠商回覆
   ▼
已報價 (quoted)
   │  評估後決定要樣品
   ▼
樣品中 (sampling) ──樣品不通過──> 已淘汰 (rejected)
   │  樣品通過
   ▼
決策中 (deciding)
   │            └──不採用──> 已淘汰 (rejected)
   ▼ 採用
已下單 (ordered) → 轉入 PurchaseOrder 追蹤
```

**設計原則**：每個中間狀態都有明確的下一步（不會卡在「不知道要幹嘛」的狀態），且都有一條
通往 `rejected`（已淘汰）的出口，避免流程卡死。`overdue`（逾期提醒）是唯一的「時間觸發」
狀態轉換，用來驅動 Phase 3 的自動提醒邏輯。

## 與 gift-suppliers/ Excel 主檔的對照（僅欄位名稱層級，未讀取實際內容）

`gift-suppliers/CLAUDE.md` 記載主檔欄位包含：聯繫日、回覆期限、MOQ、稅別、未稅單價、
樣品費、Logo/包裝費、現貨、交期、付款條件、安規／檢驗、保固／換貨、決策——本設計的
`Quote`/`PurchaseOrder` 欄位刻意保持相容（`moq`/`unit_price_ex_tax`/`sample_fee`/
`lead_time_days`/`payment_terms` 對應），如果未來要真正整合，主檔欄位可以直接映射過來，
不需要重新設計一次。

## 通知觸發規則（供 Phase 3 使用）

| 觸發事件 | 通知對象 | 通知內容 |
|---|---|---|
| Quote 新建（狀態=已詢價） | 負責人 | 「已發送詢價給 {supplier.name}，期限 {reply_deadline}」 |
| Quote 超過 reply_deadline 仍為已詢價 | 負責人 | 「⚠️ {supplier.name} 報價已逾期，請跟進」 |
| Quote 狀態變更為已報價 | 負責人 | 「{supplier.name} 已回報價，請前往比較」 |
| Quote 狀態變更為已下單 | 負責人 | 「{supplier.name} 已確認下單，轉入交期追蹤」 |
