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