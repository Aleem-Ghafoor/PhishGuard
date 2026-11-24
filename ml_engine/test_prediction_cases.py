
from ml_engine.predictor import predict_url


test_urls = [
    "https://www.example.com",
    "http://example.com",
    "https://login.example.com/account",
    "https://example.com/login?id=123&user=test",
    "http://192.0.2.10:8080/login",
    "https://example.com/%2Flogin",
    "https://xn--e1afmkfd.xn--p1ai/login",
    "https://example.com:8443/account/login"
]


print("=" * 60)
print("PHISHGUARD - MULTIPLE URL PREDICTION TESTING")
print("=" * 60)

passed = 0
failed = 0

for index, url in enumerate(test_urls, start=1):

    try:
        result = predict_url(url)

        required_keys = {
            "url",
            "prediction",
            "phishing_probability",
            "threshold"
        }

        assert required_keys.issubset(result.keys())
        assert result["prediction"] in ["Phishing", "Legitimate"]
        assert 0 <= result["phishing_probability"] <= 1

        print(f"\nTest {index}: PASSED")
        print("URL:", url)
        print("Prediction:", result["prediction"])
        print("Phishing Probability:", result["phishing_probability"])

        passed += 1

    except Exception as error:
        print(f"\nTest {index}: FAILED")
        print("URL:", url)
        print("Error:", error)

        failed += 1


print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("Total Tests:", len(test_urls))
print("Passed:", passed)
print("Failed:", failed)


print("\nINVALID INPUT TESTING")

invalid_inputs = ["", None, 123]

for value in invalid_inputs:
    try:
        predict_url(value)
        print(repr(value), "FAILED: Invalid input accepted")
    except ValueError:
        print(repr(value), "PASSED: ValueError raised")
    except Exception as error:
        print(repr(value), "FAILED:", type(error).__name__)