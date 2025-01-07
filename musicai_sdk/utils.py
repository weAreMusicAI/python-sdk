from urllib.parse import urlparse, unquote


def extract_name_from_url(file_url):
    url = urlparse(file_url)
    filename = url.path.split("/")[-1]
    return unquote(filename)


def extract_file_extension_from_url(url):
    name_from_url = extract_name_from_url(url)
    return name_from_url.split(".")[-1]
