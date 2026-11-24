
from urllib.parse import urlsplit


def validate_url(url):
    if not url or not url.strip():
        return False, "Please enter a URL."

    url = url.strip()

    if any(char.isspace() for char in url):
        return False, "URL must not contain spaces."

    try:
        parsed_url = urlsplit(url)

        if parsed_url.scheme not in ["http", "https"]:
            return False, "URL must start with http:// or https://"

        if not parsed_url.hostname:
            return False, "Please enter a valid URL."

        return True, "URL is valid."

    except ValueError:
        return False, "Invalid URL format."
