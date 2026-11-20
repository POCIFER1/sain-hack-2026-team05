import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from case3_contract import make_week_answer
from hackathon_client import HackathonAPIError
from main import app


def sample_answers():
    week = make_week_answer(
        record_id="week-001",
        profile={
            "chronotype": {
                "value": "intermediate",
                "confidence": 0.82,
            },
        },
        hypotheses=[
            {
                "text": "Возможно, ты поздно ложишься.",
                "confidence": 0.8,
            },
            {
                "text": "Похоже, активность зависит от дня.",
                "confidence": 0.7,
            },
            {
                "text": "Возможно, режим меняется в выходные.",
                "confidence": 0.6,
            },
        ],
    )

    return {"weeks": [week]}


class RunEndpointTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok"},
        )

    def test_missing_token(self):
        response = self.client.post(
            "/run",
            json={
                "case": 3,
                "dataset_code": "case3-dev-v1",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_invalid_case(self):
        response = self.client.post(
            "/run",
            headers={
                "Authorization": "Bearer test-token",
            },
            json={
                "case": 2,
                "dataset_code": "case3-dev-v1",
            },
        )

        self.assertEqual(response.status_code, 422)

    @patch("main.analyze_dataset")
    @patch("main.get_case3_dataset")
    def test_successful_run(
        self,
        mock_get_dataset,
        mock_analyze,
    ):
        dataset = {
            "weeks": [
                {"record_id": "week-001"},
            ],
        }

        mock_get_dataset.return_value = dataset
        mock_analyze.return_value = sample_answers()

        response = self.client.post(
            "/run",
            headers={
                "Authorization": "Bearer test-token",
            },
            json={
                "case": 3,
                "dataset_code": "case3-dev-v1",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json(),
            sample_answers(),
        )

        mock_get_dataset.assert_called_once_with(
            dataset_code="case3-dev-v1",
            authorization="Bearer test-token",
        )

        mock_analyze.assert_called_once_with(dataset)

    @patch("main.get_case3_dataset")
    def test_api_failure(self, mock_get_dataset):
        mock_get_dataset.side_effect = HackathonAPIError(
            "API unavailable"
        )

        response = self.client.post(
            "/run",
            headers={
                "Authorization": "Bearer test-token",
            },
            json={
                "case": 3,
                "dataset_code": "case3-dev-v1",
            },
        )

        self.assertEqual(response.status_code, 502)

    @patch("main.analyze_dataset")
    @patch("main.get_case3_dataset")
    def test_analytics_not_implemented(
        self,
        mock_get_dataset,
        mock_analyze,
    ):
        mock_get_dataset.return_value = {
          "weeks": [
          {"record_id": "week-001"},
          ],
        }

        mock_analyze.side_effect = NotImplementedError()

        response = self.client.post(
            "/run",
            headers={
                "Authorization": "Bearer test-token",
            },
            json={
                "case": 3,
                "dataset_code": "case3-dev-v1",
            },
        )

        self.assertEqual(response.status_code, 501)

    @patch("main.analyze_dataset")
    @patch("main.get_case3_dataset")
    def test_invalid_analytics_output(
        self,
        mock_get_dataset,
        mock_analyze,
    ):
        mock_get_dataset.return_value = {
          "weeks": [
          {"record_id": "week-001"},
          ],
        }

        mock_analyze.return_value = {
            "weeks": [
                {
                    "record_id": "week-001",
                    "profile": {},
                    "hypotheses": [],
                },
            ],
        }

        response = self.client.post(
            "/run",
            headers={
                "Authorization": "Bearer test-token",
            },
            json={
                "case": 3,
                "dataset_code": "case3-dev-v1",
            },
        )

        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()
