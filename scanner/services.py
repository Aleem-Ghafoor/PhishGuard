
from ml_engine.predictor import predict_url


def scan_url(url):
    result = predict_url(url)
    return result
