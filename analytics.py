from typing import Any


def analyze_dataset(
    dataset: dict[str, Any],
) -> dict[str, Any]:
    try:
        from savva_analytics import analyze_dataset as calculate
    except ModuleNotFoundError as exc:
        if exc.name == "savva_analytics":
            raise NotImplementedError(
                "Analytics module is not integrated"
            ) from exc
        raise

    return calculate(dataset)
