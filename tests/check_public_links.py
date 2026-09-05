"""Read-only audit of the homepage's external links. Reports access failures too."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_portfolio_content import Document, ROOT


def check(url):
    result = request_url(url, "HEAD")
    if result.get("status") in (400, 405):
        return request_url(url, "GET")
    return result


def request_url(url, method):
    try:
        request = Request(url, method=method, headers={"User-Agent": "Portfolio-link-check/1.0"})
        with urlopen(request, timeout=20) as response:
            return {"url": url, "status": response.status, "destination": response.url}
    except HTTPError as error:
        return {"url": url, "status": error.code}
    except (URLError, TimeoutError) as error:
        return {"url": url, "error": str(error)}


if __name__ == "__main__":
    document = Document((ROOT / "index.html").read_text(encoding="utf-8"))
    urls = sorted({attrs["href"] for tag, attrs in document.elements
                   if tag == "a" and attrs.get("href", "").startswith("https://")})
    with ThreadPoolExecutor(max_workers=4) as pool:
        print(json.dumps(list(pool.map(check, urls)), indent=2))
