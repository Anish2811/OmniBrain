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


def upload_document(uploaded_file):
    """Send a document from Streamlit to the backend."""

    try:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        response = requests.post(
            f"{BASE_URL}/upload",
            files=files,
            timeout=60
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return {
        "success": False,
        "message": "Could not connect to the backend. Please try again."
    }