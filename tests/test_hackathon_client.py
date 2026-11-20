import io
import json
import os
import unittest
from unittest.mock import patch

from hackathon_client import (
    HackathonAPIError,
    get_case3_dataset,
)


class HackathonClientTests(unittest.TestCase):

    @patch.dict(
        os.environ,
        {
            "HACK_API_URL":
                "https://hack-api.be-healthy.tech"
        },
    )
    @patch("urllib.request.urlopen")
    def test_get_dataset(self, mocked_urlopen):
        payload = {
            "dataset": {
                "meta": {"dataset_id": "case3-dev-v1"},
                "weeks": [],
            },
            "reference": {
                "answers": [],
            },
        }

        mocked_urlopen.return_value = io.BytesIO(
            json.dumps(payload).encode("utf-8")
        )

        result = get_case3_dataset(
            dataset_code="case3-dev-v1",
            authorization="Bearer test-token",
        )

        self.assertEqual(result, payload["dataset"])
        self.assertNotIn("reference", result)

        request = mocked_urlopen.call_args.args[0]

        self.assertEqual(
            request.get_header("Authorization"),
            "Bearer test-token",
        )

        self.assertIn(
            "dataset_code=case3-dev-v1",
            request.full_url,
        )

    @patch.dict(
        os.environ,
        {"HACK_API_URL": "https://example.test"},
    )
    @patch("urllib.request.urlopen")
    def test_invalid_json(self, mocked_urlopen):
        mocked_urlopen.return_value = io.BytesIO(
            b"invalid-json"
        )

        with self.assertRaises(HackathonAPIError):
            get_case3_dataset(
                dataset_code="case3-dev-v1",
                authorization="Bearer test-token",
            )

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_url(self):
        with self.assertRaises(HackathonAPIError):
            get_case3_dataset(
                dataset_code="case3-dev-v1",
                authorization="Bearer test-token",
            )


if __name__ == "__main__":
    unittest.main()
