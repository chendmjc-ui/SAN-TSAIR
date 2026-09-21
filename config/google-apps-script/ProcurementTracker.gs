/**
 * 三才實業 贈禮品採購流程追蹤器
 *
 * 設計原則（對應 docs/procurement/03_handoff_decisions_analysis.md 決定1方案A）：
 * 本表只存「追蹤狀態」，不存任何金額／MOQ／付款條件等商務欄位——逾期提醒的判斷式
 * 只需要「供應商名稱＋回覆期限」，完全用不到金額，所以這份 Sheet 的資安暴露面
 * 遠低於機密主檔。正式報價內容永遠只留在 gift-suppliers/ 的 Excel 主檔裡，
 * 這裡只是「談到哪一步了」的狀態快照，單向同步：先寫 Excel，再改本表狀態。
 *
 * 部署方式（獨立專案，不跟現有詢價表單那份 Sheet 共用——那份是 Anyone 可存取的
 * 公開 doPost 端點，機密相關資料不該跟公開入口同住）：
 * 1. 開一份新的 Google Sheet。
 * 2. 選單「擴充功能 Extensions」→「Apps Script」，把本檔內容整個貼進編輯器。
 * 3. 左側齒輪圖示「專案設定」→ Script Properties，新增兩筆
 *    （直接複用現有詢價表單那組 LINE Channel，不用重新申請）：
 *      LINE_CHANNEL_ACCESS_TOKEN = <複用詢價表單那組 Channel Access Token>
 *      LINE_USER_ID              = <複用詢價表單那組 User ID>
 * 4. 編輯器工具列函式下拉選 runSelfTest，執行一次，Log（檢視 → 記錄）要全部顯示
 *    PASS 才能繼續；任何 FAIL 都代表狀態機邏輯有誤，不可略過。
 * 5. 編輯器工具列函式下拉選 setupDailyTrigger，執行一次（會跳授權畫面，允許）。
 *    這會建立每個工作日早上 9 點自動執行 checkOverdue 的排程，不需要再手動跑。
 * 6. 回到 Sheet 分頁重新整理，選單列會多一個「採購追蹤」自訂選單。
 * 7. 把 gift-suppliers/output/tracker_seed.csv 的內容整份貼進「Import」分頁
 *    （從 A1 開始貼，含標題列），選單「採購追蹤」→「匯入參照資料」。
 */

const QUOTES_SHEET = 'quotes';
const IMPORT_SHEET = 'Import';
const QUOTES_HEADER = ['supplier_id', 'name', 'tier', 'contact_channel', 'product_name',
  'quote_id', 'status', 'contacted_at', 'reply_deadline', 'quoted_at',
  'next_action', 'last_synced'];

// 對應 docs/procurement/02_data_model.md 的狀態機
const VALID_TRANSITIONS = {
  '已詢價': ['已報價', '逾期'],
  '逾期': ['已報價'],
  '已報價': ['樣品中', '已淘汰'],
  '樣品中': ['決策中', '已淘汰'],
  '決策中': ['已下單', '已淘汰'],
  '已下單': [],
  '已淘汰': [],
};

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('採購追蹤')
    .addItem('匯入參照資料', 'importSeedData')
    .addItem('手動檢查逾期（平常會自動跑，不需手動點）', 'checkOverdue')
    .addToUi();
}

function getOrCreateQuotesSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(QUOTES_SHEET);
  if (!sheet) {
    sheet = ss.insertSheet(QUOTES_SHEET);
    sheet.appendRow(QUOTES_HEADER);
  }
  return sheet;
}

/**
 * 把「Import」分頁（gift-suppliers/scripts/export_tracker_seed.py 產出的 CSV
 * 貼上去的內容）的參照資料，upsert 進 quotes 分頁。已存在的 supplier_id 只更新
 * 參照欄位（name/tier/contact_channel/product_name），不動 status/quote_id，
 * 避免覆蓋掉已經在追蹤中的狀態。
 */
function importSeedData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const importSheet = ss.getSheetByName(IMPORT_SHEET);
  if (!importSheet) {
    SpreadsheetApp.getUi().alert('找不到「Import」分頁，請先建立並貼上 tracker_seed.csv 的內容（含標題列）。');
    return;
  }
  const importRows = importSheet.getDataRange().getValues();
  if (importRows.length < 2) {
    SpreadsheetApp.getUi().alert('Import 分頁沒有資料列，請確認已貼上 tracker_seed.csv 的內容。');
    return;
  }
  const importHeader = importRows[0];
  const col = {};
  importHeader.forEach((h, i) => { col[h] = i; });
  const required = ['supplier_id', 'name', 'tier', 'contact_channel', 'product_name', 'contacted_at', 'reply_deadline'];
  for (const key of required) {
    if (!(key in col)) {
      SpreadsheetApp.getUi().alert('Import 分頁缺少欄位：' + key + '，請確認貼上的是完整的 tracker_seed.csv。');
      return;
    }
  }

  const quotesSheet = getOrCreateQuotesSheet_();
  const existing = quotesSheet.getDataRange().getValues();
  const existingIndex = {}; // supplier_id -> row number (1-based,含標題)
  for (let r = 1; r < existing.length; r++) {
    existingIndex[existing[r][0]] = r + 1;
  }

  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
  let inserted = 0, updated = 0;

  for (let r = 1; r < importRows.length; r++) {
    const row = importRows[r];
    const supplierId = row[col['supplier_id']];
    if (!supplierId) continue;
    const name = row[col['name']];
    const tier = row[col['tier']];
    const contactChannel = row[col['contact_channel']];
    const productName = row[col['product_name']];
    const contactedAt = row[col['contacted_at']];
    const replyDeadline = row[col['reply_deadline']];

    if (existingIndex[supplierId]) {
      const rowNum = existingIndex[supplierId];
      quotesSheet.getRange(rowNum, 2, 1, 4).setValues([[name, tier, contactChannel, productName]]);
      quotesSheet.getRange(rowNum, 12).setValue(today); // last_synced
      updated++;
    } else {
      const status = (contactedAt && replyDeadline) ? '已詢價' : '';
      const quoteId = 'Q-' + supplierId;
      quotesSheet.appendRow([
        supplierId, name, tier, contactChannel, productName,
        quoteId, status, contactedAt || '', replyDeadline || '', '',
        '', today,
      ]);
      inserted++;
    }
  }

  SpreadsheetApp.getUi().alert('匯入完成：新增 ' + inserted + ' 筆、更新 ' + updated + ' 筆參照資料。');
}

function validateTransition_(current, next) {
  const allowed = VALID_TRANSITIONS[current] || [];
  return allowed.indexOf(next) !== -1;
}

/**
 * 手動變更某筆 quote 的狀態（在編輯器直接呼叫，或日後改成綁選單/按鈕）。
 * 不合法的轉換會拋錯，不會默默略過。
 */
function changeStatus(quoteId, newStatus) {
  const sheet = getOrCreateQuotesSheet_();
  const data = sheet.getDataRange().getValues();
  for (let r = 1; r < data.length; r++) {
    if (data[r][5] === quoteId) { // quote_id 欄
      const current = data[r][6]; // status 欄
      if (!validateTransition_(current, newStatus)) {
        throw new Error('不允許從「' + current + '」轉到「' + newStatus + '」（合法選項：' + (VALID_TRANSITIONS[current] || []).join('、') + '）');
      }
      sheet.getRange(r + 1, 7).setValue(newStatus); // status
      if (newStatus === '已報價') {
        sheet.getRange(r + 1, 10).setValue(Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd')); // quoted_at
      }
      return;
    }
  }
  throw new Error('找不到 quote_id：' + quoteId);
}

function isOverdue_(replyDeadline, today) {
  if (!replyDeadline) return false;
  const deadline = (replyDeadline instanceof Date) ? replyDeadline : new Date(replyDeadline);
  return today > deadline;
}

/**
 * 每個工作日早上 9 點由 setupDailyTrigger() 建立的排程自動呼叫。
 * 找出所有「已詢價」且超過 reply_deadline 的 quote，轉成「逾期」狀態並彙總成
 * 一則 LINE 訊息。狀態轉換本身就是去重機制：轉成「逾期」後就不再符合
 * 「已詢價」的篩選條件，不會被下一輪重複通知。
 */
function checkOverdue() {
  const today = new Date();
  const day = today.getDay();
  if (day === 0 || day === 6) return; // 只在工作日跑，週末略過

  const sheet = getOrCreateQuotesSheet_();
  const data = sheet.getDataRange().getValues();
  const overdueNames = [];

  for (let r = 1; r < data.length; r++) {
    const status = data[r][6];
    const replyDeadline = data[r][8];
    if (status === '已詢價' && isOverdue_(replyDeadline, today)) {
      sheet.getRange(r + 1, 7).setValue('逾期');
      overdueNames.push(data[r][1]); // name 欄
    }
  }

  if (overdueNames.length > 0) {
    const text = '⚠️ 採購追蹤逾期提醒\n以下廠商報價已逾期，請跟進：\n' + overdueNames.map(n => '・' + n).join('\n');
    notifyLine_(text);
  }
}

function notifyLine_(text) {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('LINE_CHANNEL_ACCESS_TOKEN');
  const userId = props.getProperty('LINE_USER_ID');
  if (!token || !userId) return;

  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token },
    payload: JSON.stringify({ to: userId, messages: [{ type: 'text', text: text }] }),
    muteHttpExceptions: true,
  });
}

/**
 * 建立每個工作日早上 9 點自動執行 checkOverdue 的排程。先檢查是否已存在同名
 * 觸發器，避免重複建立（重跑本函式是安全的）。只需要在部署時手動執行一次。
 */
function setupDailyTrigger() {
  const existing = ScriptApp.getProjectTriggers();
  for (const t of existing) {
    if (t.getHandlerFunction() === 'checkOverdue') {
      Logger.log('已存在 checkOverdue 的排程，不重複建立。');
      return;
    }
  }
  ScriptApp.newTrigger('checkOverdue')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
  Logger.log('已建立每日 09:00 執行 checkOverdue 的排程。');
}

/**
 * 自我測試：純邏輯驗證（狀態機轉換規則、逾期判斷），不寫入/不讀取真實的
 * quotes 分頁，避免污染正式資料。部署後、啟用排程前必須先跑過這支確認全過。
 */
function runSelfTest() {
  const results = [];
  const assert_ = (label, cond) => results.push({ label, pass: !!cond });

  // 情境1：正常流程 已詢價 -> 已報價 合法
  assert_('已詢價 -> 已報價 應合法', validateTransition_('已詢價', '已報價'));

  // 情境2：非法跳轉 已詢價 -> 已下單 應被擋下
  assert_('已詢價 -> 已下單 應不合法', !validateTransition_('已詢價', '已下單'));

  // 情境3：終態不可再轉換
  assert_('已下單 -> 已報價 應不合法（終態）', !validateTransition_('已下單', '已報價'));
  assert_('已淘汰 -> 已報價 應不合法（終態）', !validateTransition_('已淘汰', '已報價'));

  // 情境4：逾期判斷
  const today = new Date('2026-09-21');
  assert_('過期日期應判定逾期', isOverdue_('2026-09-01', today));
  assert_('未來日期不應判定逾期', !isOverdue_('2026-12-01', today));
  assert_('空白期限不應判定逾期', !isOverdue_('', today));

  // 情境5：淘汰出口存在（每個中間狀態都能淘汰，不會卡死）
  ['已報價', '樣品中', '決策中'].forEach(s => {
    assert_(s + ' 應有通往已淘汰的出口', validateTransition_(s, '已淘汰'));
  });

  let passCount = 0;
  results.forEach(r => {
    Logger.log((r.pass ? 'PASS' : 'FAIL') + ' - ' + r.label);
    if (r.pass) passCount++;
  });
  Logger.log('---');
  Logger.log(passCount + ' / ' + results.length + ' 通過');
  if (passCount !== results.length) {
    throw new Error('自我測試有未通過項目，請檢視上方 Log，不要繼續部署排程。');
  }
}
