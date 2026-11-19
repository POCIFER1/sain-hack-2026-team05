
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


REQUEST_TIMEOUT_SECONDS = 180


class HackathonAPIError(Exception):
    """Raised when the hackathon API request or response is invalid."""


def get_case3_dataset(
    dataset_code: str,
    authorization: str,
) -> dict[str, Any]:
    """Fetch a Case 3 dataset using the incoming evaluation token."""

    api_url = os.getenv("HACK_API_URL")

    if not api_url:
        raise HackathonAPIError(
            "HACK_API_URL is not configured"
        )

    if not authorization.strip():
        raise HackathonAPIError(
            "Authorization header is required"
        )

    query = urllib.parse.urlencode(
        {"dataset_code": dataset_code}
    )

    url = (
        f"{api_url.rstrip('/')}"
        f"/case/3/getData?{query}"
    )

    request = urllib.request.Request(
        url=url,
        headers={
            "Authorization": authorization,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ) as response:
            payload = json.load(response)

    except urllib.error.HTTPError as exc:
        raise HackathonAPIError(
            f"Hackathon API returned HTTP {exc.code}"
        ) from None

    except (urllib.error.URLError, TimeoutError, OSError):
        raise HackathonAPIError(
            "Hackathon API is unavailable"
        ) from None

    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HackathonAPIError(
            "Hackathon API returned invalid JSON"
        ) from None

    if not isinstance(payload, dict):
        raise HackathonAPIError(
            "Hackathon API response must be a JSON object"
        )

    dataset = payload.get("dataset")

    if not isinstance(dataset, dict):
        raise HackathonAPIError(
            "Hackathon API response contains no valid dataset"
        )

    return dataset
