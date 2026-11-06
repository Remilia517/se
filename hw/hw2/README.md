使用ChatGPT完成

# 金門大學校務入口模擬系統（課堂專題）

使用 Python Flask + SQLite 製作的校務系統風格網站。介面與功能參考一般大學學生入口網站的常見模組，並非金門大學官方系統，也不連接校方正式資料。

## 功能
- 學生登入與登出
- 首頁儀表板：學生資料、修課摘要、校務公告
- 課程查詢：依課程代碼、名稱、教師搜尋
- 模擬選課／退選：檢查重複選課、時間衝堂與名額
- 個人課表：依星期與節次呈現
- 學期成績：展示用範例資料
- 個人資料頁
- SQLite 資料庫自動初始化
- RWD 版面，支援桌面與手機瀏覽

## 環境需求
- Python 3.9 以上
- pip

## 安裝（Windows PowerShell）
```powershell
py -3.12 -m pip install -r requirements.txt
```

## 啟動
```powershell
py -3.12 app.py
```
瀏覽器開啟：
`http://127.0.0.1:5000`

## 展示帳號
- 學號：`412630001`
- 密碼：`123456`

## 專案結構
```text
knu_portal_project/
├── app.py
├── requirements.txt
├── README.md
├── knu_portal.db          # 第一次執行後自動產生
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── courses.html
│   ├── timetable.html
│   ├── grades.html
│   ├── profile.html
│   └── error.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## 資料與安全注意事項
- 所有學生、課程、公告及成績均為虛構展示資料。
- 密碼為教學簡化而以明文儲存；正式系統必須使用密碼雜湊、CSRF 防護、權限控管與 HTTPS。
- Flask 開發伺服器僅供本機測試，不應直接部署至公開網路。
- 若要使用真實校務資料，必須取得學校授權，且不得繞過登入或存取控制。

## 測試
```powershell
py -3.12 -m unittest discover -s tests -v
```

## 可搭配 OpenCode + Big Pickle 的擴充方向
可要求 AI 逐步新增：課程管理後台、成績 CRUD、學生註冊、密碼雜湊、CSRF 保護、匯出課表 PDF、單元測試與操作紀錄。請先閱讀現有架構再修改，保留 SQLite 資料與既有路由。
