使用ChatGPT完成

# StudyFlow 2.0｜智慧型學生學習與作業管理系統

## 一、專案動機與價值

學生在不同課程中常同時面對作業、報告、考試與專題，容易因截止日期分散而遺漏任務。StudyFlow 將學習待辦集中管理，並透過統計、課程進度和月曆協助安排時間。

本專案由第三週習題 3 的 StudyFlow 原始版本改進而來，保留 Flask + SQLite 技術與原本的任務管理功能，新增課程進度分析、截止日期月曆、多條件篩選及 CSV 匯出。

## 二、2.0 版本改進內容

| 功能 | 原始版本 | StudyFlow 2.0 |
|---|---|---|
| 任務 CRUD | 有 | 保留 |
| 優先級與狀態 | 有 | 保留並增加優先級篩選 |
| 關鍵字搜尋 | 有 | 保留 |
| 儀表板 | 基本統計 | 增加課程完成率與未來 7 天到期數 |
| 截止日期檢視 | 列表 | 新增月曆檢視，可切換月份 |
| 資料匯出 | 無 | 新增 UTF-8 BOM CSV 匯出，方便 Excel 開啟 |
| SQLite 效能 | 基本查詢 | 為截止日期及狀態欄位建立索引 |
| 手機版 | RWD | 保留並調整月曆與課程統計排版 |

## 三、系統功能

1. **儀表板**：顯示全部事項、未完成、逾期、完成率。
2. **課程進度分析**：統計各課程的任務數量、完成數與完成百分比。
3. **任務管理**：新增、編輯、刪除、標記完成。
4. **多條件篩選**：關鍵字、狀態及優先級。
5. **截止日期月曆**：依月份呈現截止日期，點選事項可進入編輯。
6. **CSV 匯出**：下載完整任務資料，可使用 Excel 開啟。
7. **響應式介面**：支援桌面與手機螢幕。

## 四、使用技術

- Python 3.9+
- Flask
- SQLite
- HTML / CSS / JavaScript（瀏覽器原生）
- Jinja2 Template

## 五、環境安裝

Windows PowerShell：

```powershell
py -3.12 -m pip install -r requirements.txt
```

## 六、啟動系統

在專案根目錄執行：

```powershell
py -3.12 app.py
```

瀏覽器開啟：

<http://127.0.0.1:5000>

第一次啟動會自動建立 `student_hub.db`、必要資料表與索引；若資料表為空，會加入範例任務。原本已存在的資料庫不會被刪除，新增欄位以外的功能不要求重建資料庫。

## 七、功能操作

- **總覽**：查看整體任務與各課程完成進度。
- **待辦事項**：搜尋名稱、課程或描述，並依狀態及優先級篩選。
- **月曆**：使用上個月／下個月切換月份；點選任務進入編輯。
- **匯出 CSV**：從導覽列選擇「匯出 CSV」，下載 `studyflow_tasks.csv`。

## 八、資料庫設計

主要資料表為 `tasks`：

| 欄位 | 說明 |
|---|---|
| id | 任務流水號，主鍵 |
| title | 任務名稱 |
| course | 課程名稱 |
| description | 詳細說明 |
| due_date | 截止日期 |
| priority | 高、中、低 |
| status | 待處理、進行中、已完成 |
| created_at | 建立時間 |

2.0 版本為 `due_date` 和 `status` 建立索引，改善常用排序與狀態篩選查詢。

## 九、專案結構

```text
hw3/
├── app.py
├── requirements.txt
├── README.md
├── student_hub.db       # 第一次執行時建立
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── tasks.html
│   ├── task_form.html
│   ├── calendar.html
│   └── error.html
└── tests/
    └── test_app.py
```

## 十、測試

執行原有及新增的 Flask 單元／路由測試：

```powershell
py -3.12 -m unittest discover -s tests -v
```

測試涵蓋：
- 儀表板載入與課程統計顯示。
- 新增任務。
- 缺少任務名稱時的表單驗證。
- 關鍵字搜尋。
- 任務完成狀態切換。
- 月曆頁面。
- CSV 匯出。
- 優先級篩選。

請以本機實際執行結果填寫測試通過數，不要在尚未執行前宣稱全部通過。

## 十一、改進成果與後續規劃

StudyFlow 2.0 不只是待辦事項清單，也提供課程進度總覽、截止日期視覺化與資料匯出，讓學生更容易掌握學習負擔與作業時程。

後續可擴充的方向包括使用者登入、多使用者資料隔離、行事曆提醒、雲端同步，以及匯入課程行事曆。

## 十二、參考資料

- Flask 文件：<https://flask.palletsprojects.com/>
- Python sqlite3 文件：<https://docs.python.org/3/library/sqlite3.html>
- Python csv 文件：<https://docs.python.org/3/library/csv.html>
