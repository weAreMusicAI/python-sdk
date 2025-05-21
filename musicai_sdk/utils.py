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
    try:
        import importlib.metadata
        return importlib.metadata.version("musicai-sdk")
    except (ImportError, importlib.metadata.PackageNotFoundError):
        try:
            import os
            import musicai_sdk

            package_dir = os.path.dirname(os.path.abspath(musicai_sdk.__file__))

            pyproject_path = os.path.join(
                os.path.dirname(package_dir), "pyproject.toml"
            )

            if os.path.exists(pyproject_path):
                with open(pyproject_path, "r") as f:
                    for line in f:
                        if line.strip().startswith("version"):
                            version = line.split("=")[1].strip().strip("\"'")
                            return version
        except Exception:
            pass

        return "unknown"


def get_user_agent(environment="SDK-Python", version=None):
    if version is None:
        version = get_version()
    platform_name = platform.system() or "unknown"
    return f"Music.AI/{environment}/{version} ({platform_name})"
