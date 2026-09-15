import os

from dotenv import load_dotenv


load_dotenv()


def get_gemini_api_key() -> str:
    """Return the Gemini API key from the environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Set it in the environment before running the app."
        )
    return api_key