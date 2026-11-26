from urllib.parse import urlsplit


def validate_url(url):
    """Validate the URL syntax before it reaches the ML prediction pipeline."""
    if not isinstance(url, str) or not url.strip():
        return False, "Please enter a URL."

    url = url.strip()

    if any(char.isspace() for char in url):
        return False, "URL must not contain spaces."

    try:
        parsed_url = urlsplit(url)

        if parsed_url.scheme.lower() not in ("http", "https"):
            return False, "URL must start with http:// or https://"

        if not parsed_url.hostname:
            return False, "Please enter a valid URL."

        # Accessing .port makes urllib validate the port's numeric value and range.
        # It raises ValueError for non-numeric ports and ports outside 0-65535.
        parsed_url.port

        if parsed_url.netloc.endswith(":"):
            return False, "Please enter a valid port number."

        return True, "URL is valid."

    except ValueError:
        return False, "Invalid URL format or port number."
