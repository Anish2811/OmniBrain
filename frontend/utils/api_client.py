import requests


BASE_URL = "http://127.0.0.1:8000"


def check_backend_health():
    """
    Check whether the OmniBrain FastAPI backend is running.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/health",
            timeout=5
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return {
            "status": "unavailable"
        }