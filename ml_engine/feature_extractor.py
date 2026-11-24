
import ipaddress
import re
from collections import Counter
from math import log2
from urllib.parse import parse_qsl, urlsplit

import pandas as pd


FEATURE_COLUMNS = [
    "URL_Length",
    "Dot_Count",
    "Hyphen_Count",
    "Digit_Count",
    "Special_Char_Count",
    "Has_HTTPS",
    "Domain_Length",
    "Subdomain_Count",
    "Has_IP_Address",
    "URL_Depth",
    "Query_Parameter_Count",
    "At_Symbol_Count",
    "URL_Entropy",
    "Digit_Ratio",
    "Suspicious_Word_Count",
    "Domain_Hyphen_Count",
    "Has_Port",
    "Double_Slash_Count",
    "Has_Punycode",
    "Has_Encoded_Characters",
    "Longest_Host_Label_Length"
]


SUSPICIOUS_WORDS = {
    "login", "verify", "update", "secure", "account",
    "banking", "password", "signin", "confirm",
    "webscr", "paypal"
}


def calculate_entropy(url):
    """Calculate Shannon entropy of the complete URL."""

    if not url:
        return 0.0

    char_counts = Counter(url)
    total_chars = len(url)

    entropy = 0.0

    for count in char_counts.values():
        probability = count / total_chars
        entropy -= probability * log2(probability)

    return entropy


def parse_url(url):
    """Parse URLs with or without an HTTP/HTTPS scheme."""

    try:
        if url.lower().startswith(("http://", "https://")):
            return urlsplit(url)

        return urlsplit("//" + url)

    except ValueError:
        return urlsplit("")


def extract_url_features(url):

    if not isinstance(url, str) or not url.strip():
        raise ValueError("Please provide a valid URL.")

    url = url.strip()

    parsed = parse_url(url)
    hostname = parsed.hostname or ""

    # IP address detection
    try:
        ipaddress.ip_address(hostname)
        has_ip_address = 1
    except ValueError:
        has_ip_address = 0

    # Domain and subdomain features
    domain_parts = [
        part for part in hostname.lower().rstrip(".").split(".")
        if part
    ]

    if has_ip_address:
        subdomain_count = 0
    else:
        if domain_parts and domain_parts[0] == "www":
            domain_parts = domain_parts[1:]

        subdomain_count = max(0, len(domain_parts) - 2)

    # URL structure
    url_depth = len([
        part for part in parsed.path.split("/") if part
    ])

    query_parameter_count = len(
        parse_qsl(parsed.query, keep_blank_values=True)
    )

    # Character-based features
    digit_count = sum(char.isdigit() for char in url)
    url_length = len(url)

    digit_ratio = (
        digit_count / url_length if url_length else 0
    )

    suspicious_tokens = re.findall(r"[a-z0-9]+", url.lower())

    suspicious_word_count = sum(
        token in SUSPICIOUS_WORDS
        for token in suspicious_tokens
    )

    # Port detection
    try:
        has_port = int(parsed.port is not None)
    except ValueError:
        has_port = 0

    # Double slash count, excluding the initial scheme
    double_slash_count = url.count("//")

    if url.lower().startswith(("http://", "https://")):
        double_slash_count -= 1

    # V3 additional features
    has_punycode = int("xn--" in hostname.lower())

    has_encoded_characters = int(
        bool(re.search(r"%[0-9a-fA-F]{2}", url))
    )

    hostname_labels = hostname.rstrip(".").split(".") if hostname else []

    longest_host_label_length = max(
        (len(label) for label in hostname_labels),
        default=0
    )

    features = {
        "URL_Length": url_length,
        "Dot_Count": url.count("."),
        "Hyphen_Count": url.count("-"),
        "Digit_Count": digit_count,
        "Special_Char_Count": sum(
            not char.isalnum() for char in url
        ),
        "Has_HTTPS": int(url.lower().startswith("https://")),
        "Domain_Length": len(hostname),
        "Subdomain_Count": subdomain_count,
        "Has_IP_Address": has_ip_address,
        "URL_Depth": url_depth,
        "Query_Parameter_Count": query_parameter_count,
        "At_Symbol_Count": url.count("@"),
        "URL_Entropy": calculate_entropy(url),
        "Digit_Ratio": digit_ratio,
        "Suspicious_Word_Count": suspicious_word_count,
        "Domain_Hyphen_Count": hostname.count("-"),
        "Has_Port": has_port,
        "Double_Slash_Count": double_slash_count,
        "Has_Punycode": has_punycode,
        "Has_Encoded_Characters": has_encoded_characters,
        "Longest_Host_Label_Length": longest_host_label_length
    }

    return pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS
    )
