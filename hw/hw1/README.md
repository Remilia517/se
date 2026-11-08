使用ChatGPT完成

# MiniCurl — Python 簡易版 cURL 專案

MiniCurl 是一個以 Python 撰寫的命令列 HTTP Client，參考 cURL 的操作方式，練習 HTTP Request / Response、HTTP Method、Headers、JSON、Cookie、認證與檔案傳輸。

> 本專案是教學用途的簡化實作，並非完整 cURL 替代品。

## 一、功能列表

| 功能 | 指令 | 說明 |
|---|---|---|
| GET | 預設方法 | 取得伺服器資料 |
| POST / PUT / PATCH / DELETE | `-X` | 指定 HTTP 方法 |
| HEAD | `-I` | 只取得回應標頭 |
| Request Headers | `-H` | 自訂請求標頭 |
| Request Body | `-d` | 傳送文字或表單資料 |
| JSON | `--json` | 傳送 JSON 格式 |
| Basic Auth | `-u` | HTTP 基本認證 |
| Cookie | `-b` | 傳送 Cookie |
| Cookie 儲存 | `-c` | 儲存伺服器回傳 Cookie |
| 檔案下載 | `-o` | 將回應寫入檔案 |
| 檔案上傳 | `-T` | 將本機檔案作為請求本文 |
| Multipart 表單 | `-F` | 傳送 multipart 表單欄位 |
| Redirect | `-L` / `--no-redirect` | 控制重新導向 |
| Timeout | `--timeout` | 設定逾時秒數 |
| Verbose | `-v` | 顯示請求與回應摘要 |
| Status | `--show-status` | 顯示 HTTP 狀態資訊 |

## 二、環境需求

- Windows 10 / 11、macOS 或 Linux
- Python 3.9 以上
- pip
- 可連線至測試 API 的網路

## 三、安裝與執行

### 1. 解壓縮並開啟資料夾

使用 VS Code 開啟 `minicurl_full` 資料夾。

### 2. 建立虛擬環境（建議）

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

如果 PowerShell 不允許執行啟用指令，也可以直接使用 `.venv\Scripts\python.exe` 執行程式。

### 3. 安裝套件

```bash
python -m pip install -r requirements.txt
```

### 4. 執行程式

```bash
python -m minicurl https://httpbin.org/get
```

也可以：

```bash
python -m minicurl --help
```

## 四、操作範例

### 1. GET：取得資料

```bash
python -m minicurl https://httpbin.org/get
```

### 2. POST：傳送文字資料

```bash
python -m minicurl -X POST https://httpbin.org/post -d "name=Alice&age=20"
```

### 3. POST：傳送 JSON

```bash
python -m minicurl -X POST https://httpbin.org/post --json "{\"name\":\"Alice\",\"age\":20}"
```

### 4. 自訂 Header

```bash
python -m minicurl -H "Accept: application/json" -H "User-Agent: MiniCurl/1.0" https://httpbin.org/headers
```

### 5. HEAD：取得回應標頭

```bash
python -m minicurl -I https://httpbin.org/get
```

### 6. 顯示標頭與本文

```bash
python -m minicurl -i https://httpbin.org/get
```

### 7. Basic Authentication

```bash
python -m minicurl -u "username:password" https://httpbin.org/basic-auth/username/password
```

### 8. 傳送 Cookie

```bash
python -m minicurl -b "session=abc123" https://httpbin.org/cookies
```

### 9. 下載檔案

```bash
python -m minicurl -o example.html https://example.com
```

### 10. 上傳檔案

```bash
python -m minicurl -X POST -T example.txt https://httpbin.org/post
```

### 11. 逾時與詳細資訊

```bash
python -m minicurl -v --timeout 5 https://httpbin.org/delay/2
```

### 12. DELETE

```bash
python -m minicurl -X DELETE https://httpbin.org/delete
```

## 五、HTTP 基本概念

一次 HTTP 通訊主要由 Request 與 Response 組成。

### Request（請求）

- Method：請求方法，例如 GET、POST、PUT、DELETE。
- URL：指定伺服器資源位置。
- Headers：傳遞內容格式、認證等資訊。
- Body：傳送資料，例如表單或 JSON。

### Response（回應）

- Status Code：伺服器處理結果。
- Headers：回應內容類型、長度、Cookie 等資訊。
- Body：伺服器實際回傳的資料。

### 常見 HTTP 狀態碼

| 狀態碼 | 意義 |
|---|---|
| 200 OK | 請求成功 |
| 201 Created | 資源建立成功 |
| 301 / 302 | 重新導向 |
| 400 Bad Request | 請求格式錯誤 |
| 401 Unauthorized | 尚未通過認證 |
| 403 Forbidden | 沒有存取權限 |
| 404 Not Found | 找不到資源 |
| 500 Internal Server Error | 伺服器內部錯誤 |

## 六、程式架構

```text
minicurl_full/
├── minicurl/
│   ├── __init__.py       # 套件版本
│   ├── __main__.py       # python -m minicurl 入口
│   └── cli.py            # 參數解析、HTTP 請求與輸出
├── examples/
│   └── README.md         # 範例說明
├── tests/
│   └── test_cli.py       # 單元測試
├── requirements.txt      # 相依套件
├── pyproject.toml        # 專案安裝設定
└── README.md             # 專案說明文件
```

## 七、錯誤處理與退出碼

| 退出碼 | 說明 |
|---|---|
| 0 | HTTP 請求成功（2xx） |
| 1 | 其他請求錯誤 |
| 2 | 參數、檔案或輸入格式錯誤 |
| 7 | 無法建立連線 |
| 22 | HTTP 回應為 4xx 或 5xx |
| 28 | 連線逾時 |

MiniCurl 會顯示伺服器回應內容，即使狀態碼為 4xx 或 5xx，也會以退出碼 22 表示 HTTP 錯誤。

## 八、測試

安裝需求套件後，在專案根目錄執行：

```bash
python -m unittest discover -s tests -v
```
