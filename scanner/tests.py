from unittest.mock import patch

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase

from scanner.validation import validate_url


class URLValidationTests(SimpleTestCase):
    def test_accepts_http_and_https_urls(self):
        self.assertEqual(validate_url("https://example.com")[0], True)
        self.assertEqual(validate_url("http://example.com/path")[0], True)

    def test_rejects_missing_scheme(self):
        self.assertFalse(validate_url("example.com")[0])

    def test_rejects_non_http_scheme(self):
        self.assertFalse(validate_url("ftp://example.com")[0])

    def test_rejects_non_numeric_port(self):
        self.assertFalse(validate_url("https://example.com:abc")[0])

    def test_rejects_port_out_of_range(self):
        self.assertFalse(validate_url("https://example.com:99999")[0])

    def test_rejects_empty_port(self):
        self.assertFalse(validate_url("https://example.com:")[0])

    def test_rejects_whitespace(self):
        self.assertFalse(validate_url("https://example.com/a b")[0])


class ScanAPITests(TestCase):
    def setUp(self):
        cache.clear()

    @patch("scanner.views.scan_url")
    def test_scan_api_returns_model_result(self, mock_scan_url):
        mock_scan_url.return_value = {
            "url": "https://example.com",
            "prediction": "Legitimate",
            "phishing_probability": 0.12,
            "threshold": 0.5,
        }

        response = self.client.post(
            "/scanner/scan_api/",
            {"url": "https://example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["result"]["prediction"], "Legitimate")
        mock_scan_url.assert_called_once_with("https://example.com")

    @patch("scanner.views.scan_url")
    def test_scan_api_limits_requests_per_client(self, mock_scan_url):
        mock_scan_url.return_value = {
            "url": "https://example.com",
            "prediction": "Legitimate",
            "phishing_probability": 0.12,
            "threshold": 0.5,
        }

        for _ in range(10):
            response = self.client.post(
                "/scanner/scan_api/",
                {"url": "https://example.com"},
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/scanner/scan_api/",
            {"url": "https://example.com"},
        )

        self.assertEqual(response.status_code, 429)
        self.assertFalse(response.json()["success"])
        self.assertEqual(mock_scan_url.call_count, 10)

    @patch("scanner.views.scan_url", side_effect=RuntimeError("model unavailable"))
    def test_scan_api_logs_internal_errors_and_returns_generic_message(self, mock_scan_url):
        with self.assertLogs("scanner.views", level="ERROR"):
            response = self.client.post(
                "/scanner/scan_api/",
                {"url": "https://example.com"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json()["message"],
            "Something went wrong while scanning. Please try again.",
        )
