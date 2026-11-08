使用ChatGPT完成全部程式碼

# HW9：Cloudflare 網站部署實作

## 一、作業介紹

本次作業使用 Cloudflare 平台部署網站，將原本的學生任務管理系統 StudyFlow 改良並部署至 Cloudflare Workers，並使用 Cloudflare D1 作為資料庫，實現線上任務管理功能。

本專案名稱為 **StudyFlow 2.0**，提供學生管理課程、安排作業及追蹤任務進度的功能。

## 二、專案資訊

| 項目 | 內容 |
|---|---|
| 作業名稱 | HW9：Cloudflare 網站部署 |
| 專案名稱 | StudyFlow 2.0 |
| 網站架構 | Cloudflare Workers |
| 資料庫 | Cloudflare D1 |
| 前端技術 | HTML、CSS、JavaScript |
| 後端技術 | JavaScript、Cloudflare Workers API |
| 開發工具 | Visual Studio Code |
| 部署工具 | Wrangler CLI |
| 套件管理 | npm |

### 正式網站

https://studyflow-cloudflare.wer77788901.workers.dev

## 三、系統功能

### 1. 任務管理
- 新增學生任務。
- 編輯既有任務。
- 刪除任務。
- 更新任務完成狀態。

### 2. 任務分類與搜尋
- 依課程名稱管理任務。
- 依待處理、進行中及已完成篩選。
- 依高、中、低優先程度篩選。
- 搜尋任務名稱、課程及任務說明。

### 3. 任務統計
- 顯示全部任務數量。
- 顯示待處理任務數量。
- 顯示進行中任務數量。
- 顯示已完成任務數量。

### 4. 日曆與資料匯出
- 以月曆方式顯示任務截止日期。
- 支援 CSV 格式匯出任務資料。

### 5. 資料庫管理
使用 Cloudflare D1 儲存任務資料，讓使用者重新開啟網站後仍能讀取已儲存的資料。

## 四、專案資料夾結構

```text
studyflow-cloudflare/
│
├── public/
│
├── src/
│   └── index.js
│
├── test/
│
├── .wrangler/
│
├── node_modules/
│
├── package.json
├── package-lock.json
├── wrangler.jsonc
├── schema.sql
└── README.md
```

### 主要檔案說明

| 檔案 | 用途 |
|---|---|
| src/index.js | Worker 後端、API 及網站前端內容 |
| wrangler.jsonc | Cloudflare Workers 與 D1 設定 |
| schema.sql | 建立 D1 資料表及索引 |
| package.json | 專案套件及執行指令 |
| public/ | 靜態資源資料夾 |
| test/ | 測試相關檔案 |

## 五、開發環境設定

### 1. 安裝必要工具

本專案使用以下工具：

- Node.js
- npm
- Wrangler CLI
- Visual Studio Code

安裝 Wrangler：

```powershell
npm.cmd install -D wrangler
```

確認 Wrangler 版本：

```powershell
npx.cmd wrangler --version
```

### 2. 登入 Cloudflare

```powershell
npx.cmd wrangler login
```

確認登入狀態：

```powershell
npx.cmd wrangler whoami
```

## 六、Cloudflare D1 資料庫設定

### 1. 建立 D1 資料庫

```powershell
npx.cmd wrangler d1 create studyflow-db
```

建立完成後，將資料庫名稱及 ID 設定至 `wrangler.jsonc`。

### 2. wrangler.jsonc 設定

```json
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "studyflow-cloudflare",
  "main": "src/index.js",
  "compatibility_date": "2026-11-08",
  "account_id": "YOUR_CLOUDFLARE_ACCOUNT_ID",
  "d1_databases": [
    {
      "binding": "studyflow_db",
      "database_name": "studyflow-db",
      "database_id": "YOUR_D1_DATABASE_ID"
    }
  ]
}
```

請將範例中的帳號 ID 與資料庫 ID 替換成自己的設定。

### 3. 建立資料表

在專案根目錄建立 `schema.sql`：

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    course TEXT DEFAULT '',
    description TEXT DEFAULT '',
    due_date TEXT DEFAULT '',
    priority TEXT DEFAULT '中',
    status TEXT DEFAULT '待處理',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_due_date
ON tasks(due_date);

CREATE INDEX IF NOT EXISTS idx_tasks_status
ON tasks(status);

CREATE INDEX IF NOT EXISTS idx_tasks_priority
ON tasks(priority);
```

### 4. 建立遠端資料表

```powershell
npx.cmd wrangler d1 execute studyflow-db --remote --file=./schema.sql
```

### 5. 確認資料表

```powershell
npx.cmd wrangler d1 execute studyflow-db --remote --command="SELECT name FROM sqlite_master WHERE type='table';"
```

確認結果包含：

```text
tasks
```

## 七、本機測試與執行

### 1. 安裝專案套件

```powershell
npm.cmd install
```

### 2. 建立本機 D1 資料表

```powershell
npx.cmd wrangler d1 execute studyflow-db --local --file=./schema.sql
```

注意：本機 D1 與 Cloudflare 遠端 D1 是不同的資料庫，需要分別建立資料表。

### 3. 啟動本機伺服器

```powershell
npm.cmd run dev
```

開啟瀏覽器：

http://127.0.0.1:8787/

### 4. 健康檢查

開啟：

http://127.0.0.1:8787/api/health

確認 Worker 與 D1 資料庫連線狀態。

## 八、正式部署至 Cloudflare

### 1. 執行部署

```powershell
npx.cmd wrangler deploy
```

### 2. 確認部署結果

部署成功後，Wrangler 會顯示正式網站網址。

本專案正式網址：

https://studyflow-cloudflare.wer77788901.workers.dev

### 3. 線上健康檢查

開啟：

https://studyflow-cloudflare.wer77788901.workers.dev/api/health

正常結果：

```json
{
  "status": "ok",
  "database": "connected",
  "task_count": 0
}
```

## 九、API 功能說明

| HTTP 方法 | API 路徑 | 功能 |
|---|---|---|
| GET | /api/health | 檢查系統與資料庫連線 |
| GET | /api/tasks | 取得所有任務 |
| POST | /api/tasks | 新增任務 |
| PUT | /api/tasks/:id | 編輯任務 |
| PATCH | /api/tasks/:id | 更新任務狀態或優先程度 |
| DELETE | /api/tasks/:id | 刪除任務 |
| GET | /api/export.csv | 匯出任務 CSV |