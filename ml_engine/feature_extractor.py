
import pandas as pd


FEATURE_COLUMNS = [
    "URL_Length",
    "Dot_Count",
    "Hyphen_Count",
    "Digit_Count",
    "Special_Char_Count",
    "Has_HTTPS"
]


def extract_url_features(url):

    if not isinstance(url, str) or not url:
        raise ValueError("Please provide a valid URL.")

    url = url.strip()

    features = {
        "URL_Length": len(url),
        "Dot_Count": url.count("."),
        "Hyphen_Count": url.count("-"),
        "Digit_Count": sum(char.isdigit() for char in url),
        "Special_Char_Count": sum(
            not char.isalnum() for char in url
        ),
        "Has_HTTPS": int(url.lower().startswith("https://"))
    }

    return pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS
    )
