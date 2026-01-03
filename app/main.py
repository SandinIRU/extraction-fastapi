from __future__ import annotations

from functools import lru_cache
from fastapi import FastAPI, HTTPException, Response

from app.schemas import ItineraryExtractRequest, Itinerary
from app.extractor import ItineraryExtractor, ExtractionError

app = FastAPI(
    title="Structured Extraction API (Itinerary)",
    version="1.0.0",
)


@lru_cache
def get_extractor() -> ItineraryExtractor:
    # Lazy init so DEMO_MODE=true works even without OpenAI quota
    return ItineraryExtractor()


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True}


@app.get("/favicon.ico")
def favicon() -> Response:
    # Browsers request favicon automatically; returning 204 avoids noisy 404 logs
    return Response(status_code=204)


def _run_extraction(req: ItineraryExtractRequest) -> Itinerary:
    extractor = get_extractor()
    it, _repairs = extractor.extract(
        user_text=req.text,
        max_days=req.max_days,
        currency=req.currency,
        max_repairs=2,
    )
    return it


# Correct endpoint
@app.post("/extract-itinerary", response_model=Itinerary)
def extract_itinerary(req: ItineraryExtractRequest) -> Itinerary:
    try:
        return _run_extraction(req)
    except ExtractionError as e:
        # clean 502 with the real OpenAI/quota message
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


#  old typo endpoint working (tested it before)
@app.post("/extract-itineary", response_model=Itinerary)
def extract_itineary(req: ItineraryExtractRequest) -> Itinerary:
    try:
        return _run_extraction(req)
    except ExtractionError as e:
        # 502 handling
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
