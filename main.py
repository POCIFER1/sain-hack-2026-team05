import logging
from typing import Any, Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from analytics import analyze_dataset
from case3_contract import validate_case3_answers
from hackathon_client import HackathonAPIError, get_case3_dataset


logger = logging.getLogger(__name__)

app = FastAPI(
    title="SAIN Case 3 Backend",
    version="0.1.0",
)


class RunRequest(BaseModel):
    case: Literal[3]
    dataset_code: str = Field(min_length=1, max_length=256)


def require_bearer_authorization(
    authorization: str | None,
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Bearer token required",
        )

    scheme, separator, token = authorization.partition(" ")

    if (
        not separator
        or scheme.lower() != "bearer"
        or not token.strip()
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header",
        )

    return authorization


def extract_record_ids(
    dataset: dict[str, Any],
) -> list[str]:
    weeks = dataset.get("weeks")

    if not isinstance(weeks, list) or not weeks:
        raise ValueError("Dataset must contain a non-empty weeks array")

    record_ids = []

    for week in weeks:
        if not isinstance(week, dict):
            raise ValueError("Invalid dataset week")

        record_id = week.get("record_id")

        if not isinstance(record_id, str) or not record_id:
            raise ValueError("Missing or invalid record_id")

        record_ids.append(record_id)

    if len(record_ids) != len(set(record_ids)):
        raise ValueError("Duplicate record_id in dataset")

    return record_ids


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "service": "sain-case3",
        "status": "ok",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run")
def run(
    body: RunRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    """Process all dataset weeks and return validated Case 3 answers."""

    auth_header = require_bearer_authorization(authorization)

    try:
        # Hidden evaluation datasets require the incoming Bearer token.
        dataset = get_case3_dataset(
            dataset_code=body.dataset_code,
            authorization=auth_header,
        )

    except HackathonAPIError as exc:
        logger.error("Case 3 dataset retrieval failed")

        raise HTTPException(
            status_code=502,
            detail="Failed to retrieve dataset",
        ) from exc

    try:
        expected_record_ids = extract_record_ids(dataset)

    except ValueError as exc:
        logger.error("Invalid Case 3 dataset structure")

        raise HTTPException(
            status_code=502,
            detail="Invalid Case 3 dataset structure",
        ) from exc

    try:
        answers = analyze_dataset(dataset)

    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail="Analytics is not implemented",
        ) from exc

    finally:
        del dataset

    if not isinstance(answers, dict):
        raise HTTPException(
            status_code=500,
            detail="Analytics must return a JSON object",
        )

    try:
        validate_case3_answers(
            answers,
            expected_record_ids=expected_record_ids,
        )

    except ValueError as exc:
        logger.error("Case 3 output validation failed")

        raise HTTPException(
            status_code=500,
            detail="Analytics output violates Case3Answers contract",
        ) from exc

    logger.info(
        "Case 3 run completed: %d weeks",
        len(expected_record_ids),
    )

    return answers
