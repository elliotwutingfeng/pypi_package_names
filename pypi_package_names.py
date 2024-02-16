import json
import logging
from contextlib import closing

try:
    import urllib.request as request
except ImportError:
    import urllib2 as request

try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

CONTENT_TYPES = (
    "application/vnd.pypi.simple.v1+json",
    "application/vnd.pypi.simple.v1+html",
    "text/html",  # For legacy compatibility
)  # PEP 691


class ExtractAHref(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []  # type: list[str]

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, val in attrs:
                if key == "href":
                    self.data.append(val)


def get_body(url, accept):  # type: (str, str) -> tuple[str, str | None]
    try:
        r = request.Request(url)
        r.add_header("Accept", accept)
        with closing(request.urlopen(r, timeout=60)) as f:
            status_code = f.status if hasattr(f, "status") else f.getcode()
            if status_code == 200:
                data = f.read().decode("utf-8")
                return data, f.headers.get("content-type", None)
            logger.error(status_code)
            return "", None
    except Exception as e:
        logger.error(e)
        return "", None


def get_unique_package_names(html_only=False):  # type: (bool | None) -> str
    accept_header = CONTENT_TYPES[2] if html_only else ", ".join(CONTENT_TYPES)
    source, content_type = get_body("https://pypi.python.org/simple", accept_header)
    if not any(content_type.startswith(c) for c in CONTENT_TYPES):
        raise ValueError("Invalid content-type", content_type)
    if content_type.startswith(CONTENT_TYPES[0]):
        body_json = json.loads(source)
        package_names = sorted(
            set(
                entry["name"]
                for entry in body_json.get("projects", [])
                if entry.get("name", "")
            )
        )  # type: list[str]
    else:
        parser = (
            ExtractAHref()
        )  # Parse legacy HTML page as fallback if JSON response is unavailable.
        parser.feed(source)
        paths = parser.data
        package_names = sorted(
            set(
                path.rsplit("/", 2)[-2]
                for path in paths
                if path.startswith("/simple/")
                and path.endswith("/")
                and path.count("/") == 3
            )
        )  # type: list[str]
    logger.info("%d unique package names found", len(package_names))
    return json.dumps(package_names)


if __name__ == "__main__":
    package_names = get_unique_package_names()
    print(package_names, end="")
