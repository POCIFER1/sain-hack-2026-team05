import unittest

from case3_contract import (
    PROFILE_FIELDS,
    make_week_answer,
    unknown_profile,
    validate_case3_answers,
)


def sample_hypotheses():
    return [
        {"text": "Возможно, ты иногда ложишься поздно.", "confidence": 0.4},
        {"text": "Похоже, уровень активности меняется по дням.", "confidence": 0.3},
        {"text": "Возможно, в будни режим отличается от выходных.", "confidence": 0.2},
    ]


class Case3ContractTests(unittest.TestCase):
    def test_missing_record_id_rejected(self):
        week = make_week_answer(
            "week_01",
            {},
            sample_hypotheses(),
        )

        answers = {"weeks": [week]}

        with self.assertRaises(ValueError):
            validate_case3_answers(
                answers,
                expected_record_ids=[
                    "week_01",
                    "week_02",
                ],
            )

    def test_unexpected_record_id_rejected(self):
        week = make_week_answer(
            "week_99",
            {},
            sample_hypotheses(),
        )

        answers = {"weeks": [week]}

        with self.assertRaises(ValueError):
            validate_case3_answers(
                answers,
                expected_record_ids=["week_01"],
            )

    def test_unknown_profile_has_exactly_11_fields(self):
        self.assertEqual(set(unknown_profile()), set(PROFILE_FIELDS))

    def test_valid_full_answer(self):
        week = make_week_answer(
            "week-001",
            {"chronotype": {"value": "intermediate", "confidence": 0.72}},
            sample_hypotheses(),
        )
        validate_case3_answers({"weeks": [week]}, expected_record_ids=["week-001"])

    def test_invalid_enum_rejected(self):
        week = make_week_answer(
            "week-001",
            {"movement_index": {"value": "between_50_and_70", "confidence": 0.8}},
            sample_hypotheses(),
        )
        with self.assertRaises(ValueError):
            validate_case3_answers({"weeks": [week]})

    def test_exactly_three_hypotheses(self):
        week = make_week_answer("week-001", {}, sample_hypotheses()[:2])
        with self.assertRaises(ValueError):
            validate_case3_answers({"weeks": [week]})

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValueError):
            make_week_answer("week-001", {"sleep_hours": {"value": 8, "confidence": 0.5}}, sample_hypotheses())

    def test_duplicate_record_id_rejected(self):
        week = make_week_answer("week-001", {}, sample_hypotheses())
        with self.assertRaises(ValueError):
            validate_case3_answers({"weeks": [week, week]})


if __name__ == "__main__":
    unittest.main()
