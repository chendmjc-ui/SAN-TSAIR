/**
 * 三才實業 詢價表單 → Google Sheet 留底 + LINE Messaging API 通知
 *
 * 部署方式：
 * 1. 開一份新的 Google Sheet，選單 Extensions（擴充功能）→ Apps Script。
 * 2. 把這個檔案的內容整個貼進編輯器（取代預設的 Code.gs 內容）。
 * 3. 左側「專案設定」（齒輪圖示）→ Script Properties → 新增兩筆：
 *      LINE_CHANNEL_ACCESS_TOKEN = <LINE Developers Console 取得的 Channel Access Token>
 *      LINE_USER_ID              = <要接收通知的 LINE 個人 User ID（U 開頭）>
 * 4. 右上角 Deploy → New deployment → 類型選 Web app：
 *      Execute as: Me
 *      Who has access: Anyone
 *    部署後複製產生的網址（結尾是 /exec），貼回給 Claude 更新 main.js。
 */

const SHEET_NAME = '詢價紀錄';

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const name = data.name || '';
    const phone = data.phone || '';
    const service = data.service || '';
    const qty = data.qty || '';
    const msg = data.msg || '';
    const time = data.time || new Date().toISOString();

    appendToSheet_(time, name, phone, service, qty, msg);
    notifyLine_(name, phone, service, qty, msg, time);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function appendToSheet_(time, name, phone, service, qty, msg) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(['時間', '姓名', '電話', '服務項目', '數量', '需求說明']);
  }
  sheet.appendRow([time, name, phone, service, qty, msg]);
}

function notifyLine_(name, phone, service, qty, msg, time) {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('LINE_CHANNEL_ACCESS_TOKEN');
  const userId = props.getProperty('LINE_USER_ID');
  if (!token || !userId) return;

  const text = '🏆 三才實業 新詢價單\n'
    + '姓名：' + name + '\n'
    + '電話：' + phone + '\n'
    + '項目：' + service + '\n'
    + '數量：' + qty + '\n'
    + '說明：' + msg + '\n'
    + '時間：' + time;

  UrlFetchApp.fetch('https://api.line.me/v2/bot/message/push', {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: 'Bearer ' + token },
    payload: JSON.stringify({ to: userId, messages: [{ type: 'text', text: text }] }),
    muteHttpExceptions: true
  });
}
