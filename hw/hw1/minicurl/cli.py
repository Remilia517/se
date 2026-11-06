"""Command-line interface for MiniCurl."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

from . import __version__


def parse_header(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in values:
        if ":" not in raw:
            raise ValueError(f"標頭格式錯誤：{raw!r}，請使用 '名稱: 值'")
        key, value = raw.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError("HTTP 標頭名稱不可為空")
        result[key] = value.strip()
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="minicurl",
        description="MiniCurl - 使用 Python 實作的簡易命令列 HTTP 用戶端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""使用範例：
  minicurl https://httpbin.org/get
  minicurl -X POST https://httpbin.org/post --json '{"name":"Amy"}'
  minicurl -H "Accept: application/json" https://httpbin.org/headers
  minicurl -o page.html https://example.com
  minicurl -u username:password https://httpbin.org/basic-auth/username/password
""",
    )
    parser.add_argument("url", help="要連線的完整網址")
    parser.add_argument("-X", "--request", dest="method", default="GET", help="HTTP 方法")
    parser.add_argument("-H", "--header", action="append", default=[], help="自訂 HTTP 標頭，可重複")
    parser.add_argument("-d", "--data", help="傳送文字或表單資料")
    parser.add_argument("--json", dest="json_text", help="傳送 JSON 格式資料")
    parser.add_argument("-F", "--form", action="append", default=[], help="multipart 表單欄位，格式 key=value")
    parser.add_argument("-T", "--upload-file", help="上傳檔案（以檔案內容作為 request body）")
    parser.add_argument("-u", "--user", help="Basic Auth，格式 username:password")
    parser.add_argument("-b", "--cookie", action="append", default=[], help="Cookie，格式 name=value")
    parser.add_argument("-c", "--cookie-jar", help="將伺服器回傳 Cookie 儲存至檔案")
    parser.add_argument("-o", "--output", help="將回應內容儲存至指定檔案")
    parser.add_argument("-i", "--include", action="store_true", help="同時顯示回應標頭")
    parser.add_argument("-I", "--head", action="store_true", help="使用 HEAD 方法")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示請求與回應資訊")
    parser.add_argument("-L", "--location", action="store_true", help="跟隨重新導向（預設開啟）")
    parser.add_argument("--no-redirect", action="store_true", help="不跟隨重新導向")
    parser.add_argument("--timeout", type=float, default=15, help="逾時秒數，預設 15")
    parser.add_argument("--max-size", type=int, default=0, help="回應最大下載大小（bytes），0 表示不限")
    parser.add_argument("--show-status", action="store_true", help="顯示 HTTP 狀態碼")
    parser.add_argument("--version", action="version", version=f"MiniCurl {__version__}")
    return parser


def _parse_cookies(values: list[str]) -> dict[str, str]:
    cookies = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"Cookie 格式錯誤：{item!r}，請使用 name=value")
        key, value = item.split("=", 1)
        cookies[key.strip()] = value.strip()
    return cookies


def _parse_forms(values: list[str]) -> dict[str, str]:
    data = {}
    for item in values:
        if "=" not in item:
            raise ValueError(f"表單格式錯誤：{item!r}，請使用 key=value")
        key, value = item.split("=", 1)
        data[key] = value
    return data


def _print_headers(response: requests.Response) -> None:
    print(f"HTTP {response.status_code} {response.reason}")
    for key, value in response.headers.items():
        print(f"{key}: {value}")
    print()


def run(args: argparse.Namespace) -> int:
    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        print("錯誤：URL 必須是完整的 http:// 或 https:// 網址", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("錯誤：--timeout 必須大於 0", file=sys.stderr)
        return 2
    if args.max_size < 0:
        print("錯誤：--max-size 不可小於 0", file=sys.stderr)
        return 2

    method = "HEAD" if args.head else args.method.upper()
    try:
        headers = parse_header(args.header)
        cookies = _parse_cookies(args.cookie)
        form_data = _parse_forms(args.form)

        if sum(bool(x) for x in (args.data is not None, args.json_text is not None, bool(args.form), args.upload_file)) > 1:
            print("錯誤：--data、--json、--form、--upload-file 請擇一使用", file=sys.stderr)
            return 2

        body = args.data
        json_body = None
        if args.json_text is not None:
            try:
                json_body = json.loads(args.json_text)
            except json.JSONDecodeError as exc:
                print(f"JSON 格式錯誤：{exc}", file=sys.stderr)
                return 2
            if not any(k.lower() == "content-type" for k in headers):
                headers["Content-Type"] = "application/json"

        files = None
        opened_file = None
        if args.form:
            form_data = _parse_forms(args.form)
        if args.upload_file:
            file_path = Path(args.upload_file)
            if not file_path.is_file():
                print(f"找不到上傳檔案：{file_path}", file=sys.stderr)
                return 2
            opened_file = file_path.open("rb")
            body = opened_file

        if args.verbose:
            print(f"> {method} {args.url}", file=sys.stderr)
            for key, value in headers.items():
                print(f"> {key}: {value}", file=sys.stderr)
            for key in cookies:
                print(f"> Cookie: {key}=***", file=sys.stderr)

        auth = None
        if args.user:
            if ":" not in args.user:
                print("錯誤：-u 格式應為 username:password", file=sys.stderr)
                if opened_file:
                    opened_file.close()
                return 2
            auth = tuple(args.user.split(":", 1))

        session = requests.Session()
        if args.cookie_jar and Path(args.cookie_jar).exists():
            session.cookies.update(requests.utils.cookiejar_from_dict({}))
            session.cookies.update(requests.cookies.RequestsCookieJar())
            # Netscape cookie jars are not required; this option writes received cookies below.
        response = session.request(
            method=method,
            url=args.url,
            headers=headers,
            data=body if json_body is None and not args.form else (form_data if args.form else None),
            json=json_body,
            files=files,
            cookies=cookies,
            auth=auth,
            timeout=args.timeout,
            allow_redirects=not args.no_redirect,
            stream=bool(args.output),
        )
        if opened_file:
            opened_file.close()

        if args.verbose:
            print(f"< HTTP {response.status_code} {response.reason}", file=sys.stderr)

        if args.cookie_jar:
            cookie_dict = requests.utils.dict_from_cookiejar(session.cookies)
            Path(args.cookie_jar).write_text(
                "\\n".join(f"{k}={v}" for k, v in cookie_dict.items()), encoding="utf-8"
            )

        if args.include or args.head or args.show_status:
            _print_headers(response)

        if args.head:
            return 0 if response.ok else 22

        if args.output:
            total = 0
            with Path(args.output).open("wb") as output:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if args.max_size and total > args.max_size:
                        raise ValueError(f"下載內容超過限制 {args.max_size} bytes")
                    output.write(chunk)
            print(f"已儲存 {total} bytes 至 {args.output}", file=sys.stderr)
        else:
            content = response.content
            if args.max_size and len(content) > args.max_size:
                raise ValueError(f"回應內容超過限制 {args.max_size} bytes")
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    print(json.dumps(response.json(), ensure_ascii=False, indent=2))
                except requests.exceptions.JSONDecodeError:
                    sys.stdout.write(response.text)
            else:
                sys.stdout.write(response.text)
                if response.text and not response.text.endswith("\\n"):
                    print()

        return 0 if response.ok else 22

    except requests.exceptions.Timeout:
        print(f"連線逾時：超過 {args.timeout} 秒", file=sys.stderr)
        return 28
    except requests.exceptions.ConnectionError as exc:
        print(f"連線失敗：{exc}", file=sys.stderr)
        return 7
    except requests.exceptions.RequestException as exc:
        print(f"HTTP 請求錯誤：{exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 2


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(run(args))


if __name__ == "__main__":
    main()
