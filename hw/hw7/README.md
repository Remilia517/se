使用ChatGPT完成

# 第六週 Docker 作業：StudyTask 微服務系統

## 1. 專案介紹

StudyTask 是課程作業管理網站，可新增作業、查看清單、標記完成及刪除。資料儲存在 PostgreSQL。

本專案使用：
- **Nginx**：Web Server，提供靜態網頁；同時作為 Reverse Proxy，將 `/api/` 請求轉送至 Flask API。
- **Python Flask**：提供 REST API，處理作業新增、查詢、更新與刪除。
- **PostgreSQL 16**：保存作業資料。
- **Dockerfile**：定義 API 與 Nginx 映像的建置方式。
- **docker-compose.yml**：管理多個容器、網路、資料卷、環境變數及健康檢查。

## 2. 系統架構

```text
瀏覽器 http://localhost:8080
              |
              v
       Nginx (port 80)
       Web Server / Reverse Proxy
              |
       /api/* | 靜態網頁
              v
       Flask API (port 5000)
              |
              v
       PostgreSQL (port 5432)
```

| 服務 | 容器連接埠 | 主機連接埠 | 功能 |
|---|---:|---:|---|
| nginx | 80 | 8080 | 網頁入口 |
| api | 5000 | 不直接公開 | Flask API |
| db | 5432 | 不直接公開 | PostgreSQL |

三個服務位於同一個 Docker bridge network。Nginx 透過 `api:5000` 連接後端，API 透過 `db:5432` 連接資料庫。

## 3. 專案結構

```text
studytask-docker/
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── nginx/
│   ├── Dockerfile
│   ├── default.conf
│   └── html/index.html
├── tests/
│   ├── unit/test_validation.py
│   └── api/test_tasks_api.py
├── e2e/
│   ├── package.json
│   ├── playwright.config.js
│   └── tests/studytask.spec.js
├── requirements-test.txt
├── pytest.ini
├── docker-compose.yml
├── .env.example
├── .dockerignore
├── .gitignore
└── README.md
```

## 4. 執行環境與安裝紀錄

本次使用 Windows、PowerShell、VS Code、Docker Desktop。

實際版本：

```text
Docker version 29.9.2, build a82e528
Docker Compose version v5.6.1
```

Docker Desktop 初次安裝時提示 Windows 尚未啟用 **Virtual Machine Platform**。依安裝程式提示，以系統管理員身分開啟 PowerShell，執行：

```powershell
wsl --install
```

完成後重新啟動 Windows，再開啟 Docker Desktop，等待 Docker Engine 啟動。

確認安裝及引擎狀態：

```powershell
docker --version
docker compose version
docker info
```

本專案不需要在 Windows 主機另外安裝 Python 或 PostgreSQL，相關執行環境由容器提供。

## 5. 建立環境設定檔

在專案根目錄執行：

```powershell
Copy-Item .env.example .env
```

`.env` 用來設定資料庫名稱、帳號、密碼及網站連接埠。正式環境應更換預設密碼，不要將含有機密資訊的 `.env` 上傳至公開 Repository。

## 6. Docker 指令與實際操作紀錄

### 6.1 查看 Docker 版本

```powershell
docker --version
docker compose version
```

實際輸出為 Docker 29.9.2、Docker Compose v5.6.1。

### 6.2 建置並啟動服務

```powershell
docker compose up -d --build
```

- `up`：建立並啟動 Compose 定義的服務。
- `-d`：背景執行。
- `--build`：啟動前先建置自訂映像。

第一次執行曾出現 Docker API 無法連線的錯誤：

```text
failed to connect to the docker API
The system cannot find the file specified.
```

原因是 Docker Desktop 的 Engine 尚未啟動。開啟 Docker Desktop 並等待 Engine 正常啟動後，再執行上述指令，即成功啟動服務。

### 6.3 查看容器狀態

```powershell
docker compose ps
```

本次實際結果：

| 容器 | 服務 | 狀態 |
|---|---|---|
| `hw6-api-1` | api | Up |
| `hw6-db-1` | db | Up (healthy) |
| `hw6-nginx-1` | nginx | Up |

Nginx 顯示 `0.0.0.0:8080 -> 80/tcp`，代表可透過本機 8080 埠開啟網站。

### 6.4 查看日誌

```powershell
docker compose logs
docker compose logs -f
docker compose logs api
docker compose logs db
```

`logs` 查看輸出；`-f` 持續追蹤日誌，按 `Ctrl+C` 停止追蹤（不會停止容器）；指定服務名稱可查看單一服務。

### 6.5 進入容器

```powershell
docker compose exec api sh
```

進入 API 容器後：

```sh
python --version
exit
```

進入 PostgreSQL：

```powershell
docker compose exec db psql -U studytask -d studytask
```

在 psql 內執行：

```sql
\dt
SELECT * FROM tasks;
\q
```

### 6.6 查看映像、容器、資料卷及網路

```powershell
docker images
docker ps
docker ps -a
docker volume ls
docker network ls
```

### 6.7 停止及移除服務

```powershell
docker compose stop
docker compose start
docker compose down
```

- `stop`：停止容器但保留容器。
- `start`：重新啟動已停止的容器。
- `down`：移除容器與網路，預設保留 named volume。

若要連同 PostgreSQL 資料一起刪除：

```powershell
docker compose down -v
```

**注意：** `-v` 會刪除 PostgreSQL 資料卷，資料庫資料會消失。需要保留資料時不要使用。

## 7. 網頁與 API 實際測試

啟動服務：

```powershell
docker compose up -d
```

瀏覽器開啟：<http://localhost:8080>

本次實際測試：
1. 網頁顯示「系統正常｜API 已連線｜資料庫已連線」。
2. 新增作業「Docker 第六週作業」，課程填入「軟體工程」，並設定截止日期。
3. 新增後，作業出現在清單中。
4. 勾選作業後，作業顯示完成狀態。
5. 重新整理網頁，資料仍能顯示。

API 健康檢查網址：<http://localhost:8080/api/health>

預期回傳：

```json
{
  "status": "ok",
  "service": "studytask-api",
  "database": "connected"
}
```

這段 JSON 是瀏覽器/API 的回應，不是 PowerShell 指令。若直接貼到 PowerShell，會因為語法不符而出現錯誤。

## 8. Docker Volume 資料持久化測試

本專案使用 named volume `postgres_data` 保存 PostgreSQL 資料。

實際測試步驟：

1. 在網頁新增「Docker 第六週作業」。
2. 執行 `docker compose down`，停止並移除容器。
3. 執行 `docker compose up -d`，重新建立並啟動容器。
4. 重新開啟 <http://localhost:8080>。
5. 確認原本新增的作業仍然存在。

**實際測試結果：成功。** 容器移除並重新建立後，原本的作業資料仍然存在，證明 PostgreSQL 資料保存在 Docker named volume，而不是只存在於容器本身。

`docker compose down` 預設保留 named volume；若使用 `docker compose down -v`，資料卷會被刪除。

## 9. Nginx Reverse Proxy 說明

使用者只需要連線至 Nginx 的 `http://localhost:8080`：
- 一般網頁由 Nginx 提供。
- `/api/` 開頭的請求由 Nginx 反向代理至 `api:5000`。
- Flask API 再透過 Docker 內部網路連接 `db:5432`。

因此瀏覽器不需要直接連接資料庫，也不必公開 API 與 PostgreSQL 的連接埠。

## 10. 常見問題

**Docker Engine 無法連線：** 確認 Docker Desktop 已啟動，等待 Engine 正常運作，再執行 `docker info`。

**8080 埠已被使用：** 修改 `.env` 的 `WEB_PORT=8081`，重新啟動後使用 `http://localhost:8081`。

**API 無法連接資料庫：** 執行 `docker compose ps`、`docker compose logs db`、`docker compose logs api`，確認 DB healthy，且連線主機名稱為 `db` 而非 `localhost`。

**修改程式碼後畫面未更新：** 執行 `docker compose up -d --build` 重新建置。

## 11. 學習心得

透過本專案，我實際練習了 Docker image、container、Dockerfile、Docker Compose、port mapping、volume、network、environment variables、health check 與 logs 等概念。

我了解如何將網站入口、後端 API 與資料庫拆成獨立服務：Nginx 負責接收瀏覽器請求，Flask 負責資料邏輯，PostgreSQL 負責保存資料。使用 Docker Compose 可以透過一份 YAML 設定檔統一啟動及管理多個服務，讓開發環境更容易重現。

本次也實際解決 Docker Engine 尚未啟動造成無法連線的問題，最後完成三個容器啟動、網站操作、API 與資料庫連線，以及 PostgreSQL Volume 資料持久化測試。

## 12. 參考資料

1. 老師教材：<https://github.com/ccc115a/se/tree/main/03-tool/03-docker>
2. Docker Docs - Compose Quickstart：<https://docs.docker.com/compose/gettingstarted/>
3. Docker Docs - Multi-container applications：<https://docs.docker.com/get-started/docker-concepts/running-containers/multi-container-applications/>
4. Docker Compose：<https://github.com/docker/compose>


# 第七週：網站應用的三種測試

本週以 StudyTask 作業管理系統為測試對象，實作三個層級的測試：

1. **單元測試（Unit Test）**：測試 Python Flask Server 中獨立的資料驗證函式。
2. **系統測試／Web API 測試（API Test）**：透過 HTTP 請求測試 API 與 PostgreSQL 的整合。
3. **端對端測試（E2E Test）**：使用 Playwright 無頭瀏覽器，模擬使用者在網頁上的操作。

## 13. 測試環境準備

測試需要先安裝 Python 套件：

```powershell
py -3.12 -m pip install -r app/requirements.txt -r requirements-test.txt
```

確認 Docker 服務已啟動：

```powershell
docker compose up -d --build
docker compose ps
```

確認網站可以開啟：<http://localhost:8080>

### 三種測試的差異

| 測試種類 | 測試對象 | 本專案使用工具 | 目的 |
|---|---|---|---|
| 單元測試 | Server 的函式 | Python `unittest` | 確認單一函式輸入與輸出正確 |
| 系統/API 測試 | HTTP API 與資料庫整合 | `pytest`、`requests` | 確認 API 狀態碼、回傳資料及 CRUD 流程 |
| E2E 測試 | 完整網站操作流程 | Playwright | 模擬使用者透過瀏覽器操作網站 |

## 14. 單元測試（Unit Test）

### 測試內容

單元測試放在 `tests/unit/test_validation.py`，測試 Flask Server 的兩個資料驗證函式：

- `validate_title()`：檢查作業名稱是否為空白，並去除前後空格。
- `validate_status()`：只允許 `pending` 與 `done` 兩種狀態。

### 執行指令

在專案根目錄執行：

```powershell
py -3.12 -m unittest discover -s tests/unit -v
```

預期結果為 4 個測試案例通過，包括：
1. 作業名稱可以正確去除前後空白。
2. 空白或空值的作業名稱會被拒絕。
3. `pending` 和 `done` 是有效狀態。
4. 其他狀態值會被拒絕。

單元測試不需要啟動 PostgreSQL，因為這些測試只針對獨立的 Server 函式。

## 15. 系統測試／Web API 測試

### 測試內容

API 測試放在 `tests/api/test_tasks_api.py`，使用 `requests` 對正在執行的網站送出 HTTP 請求，並由 `pytest` 驗證回應。

測試項目：
1. `GET /api/health`：確認 API 與 PostgreSQL 連線正常。
2. `POST /api/tasks`：新增作業，確認回傳 HTTP 201。
3. `GET /api/tasks`：確認新增的作業出現在清單。
4. `PATCH /api/tasks/<id>`：將作業狀態改為 `done`。
5. `DELETE /api/tasks/<id>`：測試結束後刪除測試資料。
6. 空白作業名稱：確認 API 回傳 HTTP 400。

### 執行指令

先確定 Docker 容器正在執行，再於專案根目錄執行：

```powershell
py -3.12 -m pytest tests/api -v
```

預設測試網址是 `http://localhost:8080`。若要測試其他網址，可設定環境變數：

```powershell
$env:STUDYTASK_BASE_URL = "http://localhost:8080"
py -3.12 -m pytest tests/api -v
```

API 測試會建立一筆帶有隨機識別碼的測試作業，並在測試結束時嘗試刪除，不會依賴固定的作業 ID。

## 16. E2E 端對端測試（Playwright）

### Playwright 介紹

Playwright 是瀏覽器自動化測試工具，可以啟動 Chromium、Firefox 或 WebKit，模擬使用者開啟網站、輸入文字、點擊按鈕及檢查畫面。

本專案使用 Playwright 的 Chromium 無頭模式（Headless），不需要顯示瀏覽器視窗。

### 安裝 Node.js 套件

先確認電腦已安裝 Node.js 和 npm：

```powershell
node --version
npm --version
```

進入 `e2e` 資料夾：

```powershell
cd e2e
npm install
npx playwright install chromium
```

### 執行 E2E 測試

確認 Docker 網站仍在執行，並且目前位於 `e2e` 資料夾：

```powershell
npm run test:e2e
```

若想看到瀏覽器實際操作過程：

```powershell
npm run test:e2e:headed
```

### 測試項目

`e2e/tests/studytask.spec.js` 包含兩個端對端測試：

1. 開啟首頁，確認頁面顯示系統、API 與資料庫連線正常。
2. 模擬使用者新增作業、勾選完成，再刪除該作業，確認整個操作流程成功。

測試報告可使用：

```powershell
npm run report
```

Playwright 會產生 HTML 報告；失敗時也會保留截圖及 trace，方便除錯。

## 17. 建議的完整測試順序

每次測試建議依照以下順序執行：

**第一步：啟動 Docker 服務（在專案根目錄）**

```powershell
docker compose up -d --build
docker compose ps
```

**第二步：執行 Server 單元測試（在專案根目錄）**

```powershell
py -3.12 -m unittest discover -s tests/unit -v
```

**第三步：執行 Web API 系統測試（在專案根目錄）**

```powershell
py -3.12 -m pytest tests/api -v
```

**第四步：執行 Playwright E2E 測試（切換至 e2e 資料夾）**

```powershell
cd e2e
npm run test:e2e
```

**第五步：回到專案根目錄，查看服務狀態**

```powershell
cd ..
docker compose ps
```

## 18. 測試結果紀錄

執行測試後，請將自己的實際結果填入下表，並保留終端機截圖：

| 測試種類 | 測試指令 | 實際結果 |
|---|---|---|
| 單元測試 | `py -3.12 -m unittest discover -s tests/unit -v` | 執行後填寫 |
| API 系統測試 | `py -3.12 -m pytest tests/api -v` | 執行後填寫 |
| Playwright E2E | `npm run test:e2e`（於 `e2e` 資料夾） | 執行後填寫 |

> 注意：以上是測試程式與執行方式，表格中的通過數量必須以實際執行結果為準，不要在尚未執行前填寫測試成功。
