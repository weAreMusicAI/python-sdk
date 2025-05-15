from urllib.parse import urlparse, unquote
import platform
from pathlib import Path


def extract_name_from_url(file_url):
    url = urlparse(file_url)
    filename = url.path.split("/")[-1]
    return unquote(filename)


def extract_file_extension_from_url(url):
    name_from_url = extract_name_from_url(url)
    return name_from_url.split(".")[-1]


def get_version():
    package_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(package_path, "r") as f:
        content = f.read()

        for line in content.splitlines():
            if line.startswith("version = "):
                return line.split("=")[1].strip().strip("\"'")
    return "unknown"


def get_user_agent(environment="SDK-Python", version=None):
    if version is None:
        version = get_version()
    platform_name = platform.system() or "unknown"
    return f"Music.AI/{environment}/{version} ({platform_name})"
