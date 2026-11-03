"""GET 전용 Graph 클라이언트. 외부 오류와 URL을 그대로 노출하지 않는다."""
import json
import math
import os
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from runtime import CollectDeadline, GRAPH_VERSION, GraphError, GraphRateLimited


def retry_minutes(headers) -> int | float | None:
    values = []
    for name, raw in (headers or {}).items():
        if name.lower() not in ("x-business-use-case-usage", "x-ad-account-usage"):
            continue
        try:
            pending = [json.loads(raw)]
        except (ValueError, TypeError):
            continue
        while pending:
            item = pending.pop()
            if isinstance(item, dict):
                value = item.get("estimated_time_to_regain_access")
                if type(value) in (int, float) and math.isfinite(value) and value >= 0:
                    values.append(value)
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)
    return max(values) if values else None


def response_error(data, status: int, headers) -> GraphError:
    error = data.get("error") if isinstance(data, dict) else None
    code = error.get("code") if isinstance(error, dict) else None
    code = code if type(code) is int else None
    if status == 429 or code in (4, 17, 32, 613) or (code is not None and 80000 <= code <= 80014):
        return GraphRateLimited(retry_minutes(headers), code)
    return GraphError(code=code)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def mask_url(url: str) -> str:
    return re.sub(r"(?i)(access_token=)[^&#\s]*", r"\1[REDACTED]", url)


class Graph:
    def __init__(self, token: str | None = None, opener=None, sleeper=time.sleep):
        self._token = os.environ.get("ACCESS_TOKEN", "") if token is None else token
        if not self._token:
            raise ValueError("token_missing")
        self._open = opener or build_opener(NoRedirect()).open
        self._sleep = sleeper
        self.deadline = None

    def remaining(self) -> float:
        remaining = 20 if self.deadline is None else self.deadline - time.monotonic()
        if remaining <= 0:
            raise CollectDeadline()
        return min(20, remaining)

    def get(self, path: str, params: dict | None = None) -> dict:
        if not re.fullmatch(r"/[A-Za-z0-9_/-]+", path):
            raise ValueError("invalid_graph_path")
        params = dict(params or {})
        if "access_token" in params:
            raise ValueError("token_parameter_forbidden")
        url = f"https://graph.facebook.com/{GRAPH_VERSION}{path}?{urlencode(params)}"
        request = Request(url, headers={"Authorization": "Bearer " + self._token})
        for attempt in range(3):
            retry = False
            failure = GraphError()
            try:
                with self._open(request, timeout=self.remaining()) as response:
                    data = json.load(response)
                    if isinstance(data, dict) and "error" in data:
                        raise response_error(data, 200, getattr(response, "headers", {}))
                self.remaining()
                if not isinstance(data, dict):
                    raise GraphError("graph_response_error")
                return data
            except CollectDeadline:
                raise
            except HTTPError as error:
                try:
                    try:
                        data = json.load(error)
                    except (ValueError, OSError):
                        data = None
                    failure = response_error(data, error.code, error.headers)
                finally:
                    error.close()
                if isinstance(failure, GraphRateLimited):
                    raise failure from None
                retry = 500 <= error.code < 600
            except (URLError, OSError, TimeoutError):
                retry = True
            except GraphError:
                raise
            except ValueError:
                raise GraphError("graph_response_error") from None
            except Exception:
                raise failure from None
            if not retry or attempt == 2:
                raise failure from None
            self._sleep(min(attempt + 1, self.remaining()))
        raise GraphError("graph_request_failed")

    def pages(self, path: str, params: dict | None = None) -> list:
        query, rows, seen = {**(params or {}), "limit": 500}, [], set()
        while True:
            page = self.get(path, query)
            if not isinstance(page.get("data"), list):
                raise GraphError("graph_data_missing")
            rows.extend(page["data"])
            paging = page.get("paging", {})
            if not paging.get("next"):
                return rows
            # next URL 자체를 호출하지 않아 인증 헤더의 외부 호스트 유출을 막는다.
            parsed = urlsplit(paging["next"])
            if parsed.scheme != "https" or parsed.hostname != "graph.facebook.com":
                raise GraphError("unsafe_pagination")
            cursor = parse_qs(parsed.query).get("after", [None])[0]
            if not cursor or cursor in seen:
                raise GraphError("invalid_pagination")
            seen.add(cursor)
            query["after"] = cursor
