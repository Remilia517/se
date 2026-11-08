使用ChatGPT完成

# StudyFlow 學生學習與作業管理中心

## 專案價值
學生常在不同課程、群組與平台收到作業通知，容易忘記截止日期。本系統將課程作業、報告、考試與個人待辦集中管理，並提供優先級、狀態、截止日與完成率總覽。

## 功能
- 儀表板：總事項、未完成、逾期、完成率
- 新增、編輯、刪除待辦事項
- 記錄課程、說明、截止日期、優先級
- 待處理／進行中／已完成狀態管理
- 搜尋與狀態篩選
- 自動計算逾期與完成率
- SQLite 持久化儲存
- 手機與桌面 RWD 介面

## 環境需求
Python 3.9 以上。

## Windows 安裝
```powershell
py -3.12 -m pip install -r requirements.txt
```

## 啟動
```powershell
py -3.12 app.py
```
瀏覽器開啟 http://127.0.0.1:5000

第一次啟動會自動建立 `student_hub.db` 並放入幾筆範例事項。

## 專案結構
```text
student_life_hub/
├── app.py
├── requirements.txt
├── README.md
├── student_hub.db       # 執行後自動建立
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── tasks.html
│   ├── task_form.html
│   └── error.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## 測試
```powershell
py -3.12 -m unittest discover -s tests -v
```
