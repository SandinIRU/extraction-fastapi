from __future__ import annotations

import json
import os
from typing import Tuple

from dotenv import load_dotenv
from pydantic import ValidationError

from app.schemas import Itinerary, DayPlan, ActivityBlock
from app.rules import validate_business_rules


SYSTEM_PROMPT = """You are a strict information extraction engine.
Return ONLY a JSON object matching the provided schema.
Do not include any extra keys.
If the user text is missing details, make minimal reasonable assumptions and list them in assumptions.
Keep activities realistic and safe."""


class ExtractionError(RuntimeError):
    pass


class ItineraryExtractor:
    def __init__(self) -> None:
        load_dotenv()
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Only require OpenAI key if demo mode is OFF
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None

        if not self.demo_mode:
            if not self.api_key:
                raise ExtractionError("Missing OPENAI_API_KEY and DEMO_MODE is false. Set DEMO_MODE=true for GitHub/demo.")
            # Import OpenAI only when needed (keeps demo mode lighter)
            from openai import OpenAI  # local import
            self.client = OpenAI(api_key=self.api_key)

    def _demo_itinerary(self, user_text: str, max_days: int, currency: str) -> Itinerary:
        """
        Deterministic fallback: produces valid schema output without calling OpenAI.
        This is perfect for GitHub reviewers.
        """
        # quick heuristic: try to infer travelers/days (optional)
        duration = min(4, max_days)

        days = [
            DayPlan(
                day_number=1,
                base_city="Colombo",
                morning=[ActivityBlock(title="Arrive & city walk", place="Colombo")],
                afternoon=[ActivityBlock(title="Museum / Galle Face", place="Colombo")],
                evening=[ActivityBlock(title="Dinner by the sea", place="Colombo")],
                notes=["DEMO_MODE: Replace with real LLM output by setting DEMO_MODE=false and adding billing/quota."],
            ),
            DayPlan(
                day_number=2,
                base_city="Kandy",
                morning=[ActivityBlock(title="Travel to Kandy", place="Kandy")],
                afternoon=[ActivityBlock(title="Temple of the Tooth visit", place="Kandy")],
                evening=[ActivityBlock(title="Cultural show", place="Kandy")],
            ),
            DayPlan(
                day_number=3,
                base_city="Nuwara Eliya / Ella",
                morning=[ActivityBlock(title="Scenic train ride", place="Kandy → Ella")],
                afternoon=[ActivityBlock(title="Tea plantation tour", place="Nuwara Eliya / Ella")],
                evening=[ActivityBlock(title="Relax & viewpoints", place="Ella")],
            ),
            DayPlan(
                day_number=4,
                base_city="Colombo",
                morning=[ActivityBlock(title="Return to Colombo", place="Colombo")],
                afternoon=[ActivityBlock(title="Shopping / souvenirs", place="Colombo")],
                evening=[ActivityBlock(title="Departure prep", place="Colombo")],
            ),
        ][:duration]

        return Itinerary(
            trip_title="Demo Sri Lanka Itinerary",
            traveler_count=2,
            duration_days=duration,
            currency=currency,
            assumptions=[
                "DEMO_MODE output (no OpenAI call).",
                "Activities are generic placeholders for demonstration.",
            ],
            days=days,
        )

    def _call_model(self, user_text: str, max_days: int, currency: str) -> Itinerary:
        if not self.client:
            raise ExtractionError("OpenAI client not initialized. Set DEMO_MODE=false and provide OPENAI_API_KEY.")

        user_prompt = f"""
Extract a travel itinerary from this text.

Hard requirements:
- duration_days must be <= {max_days}
- currency must be "{currency}"
- day_number must start at 1 and increase by 1
- days length must equal duration_days

Text:
{user_text}
""".strip()

        resp = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            text_format=Itinerary,
            temperature=0,
        )
        return resp.output_parsed  # type: ignore[return-value]

    def extract(self, user_text: str, max_days: int, currency: str, max_repairs: int = 2) -> Tuple[Itinerary, int]:
        # Demo path (no OpenAI needed)
        if self.demo_mode:
            it = self._demo_itinerary(user_text, max_days, currency)
            errors = validate_business_rules(it)
            if errors:
                raise ExtractionError(f"Demo itinerary failed rules: {errors}")
            return it, 0

        # Real OpenAI path
        itinerary = self._call_model(user_text, max_days=max_days, currency=currency)
        errors = validate_business_rules(itinerary)

        repairs_used = 0
        while errors and repairs_used < max_repairs:
            repairs_used += 1
            repair_prompt = f"""
The JSON you produced did not satisfy our business rules.

Business rule violations:
{json.dumps(errors, indent=2)}

Here is your previous JSON:
{itinerary.model_dump_json(indent=2)}

Fix the JSON so it satisfies the rules and still matches the schema exactly.
Return ONLY corrected JSON.
""".strip()

            try:
                resp = self.client.responses.parse(
                    model=self.model,
                    input=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": repair_prompt},
                    ],
                    text_format=Itinerary,
                    temperature=0,
                )
                itinerary = resp.output_parsed  # type: ignore[assignment]
            except ValidationError as ve:
                errors = [f"Schema validation error: {str(ve)}"]
                continue

            errors = validate_business_rules(itinerary)

        if errors:
            raise ExtractionError(f"Could not satisfy business rules after {max_repairs} repairs: {errors}")

        return itinerary, repairs_used
