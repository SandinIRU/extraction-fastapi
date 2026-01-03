from app.schemas import Itinerary, DayPlan
from app.rules import validate_business_rules


def test_business_rules_day_numbers_must_be_sequential():
    it = Itinerary(
        trip_title="Test Trip",
        traveler_count=2,
        duration_days=2,
        currency="LKR",
        assumptions=[],
        days=[
            DayPlan(day_number=1, base_city="Colombo"),
            DayPlan(day_number=3, base_city="Kandy"),
        ],
    )
    errs = validate_business_rules(it)
    assert any("day_number must be exactly" in e for e in errs)


def test_business_rules_days_length_equals_duration():
    it = Itinerary(
        trip_title="Test Trip",
        traveler_count=1,
        duration_days=3,
        currency="LKR",
        assumptions=[],
        days=[
            DayPlan(day_number=1, base_city="Colombo"),
            DayPlan(day_number=2, base_city="Kandy"),
        ],
    )
    errs = validate_business_rules(it)
    assert any("days length" in e for e in errs)
