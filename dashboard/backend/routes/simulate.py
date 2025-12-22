"""Simulation routes - send test logs through the pipeline."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
import httpx

router = APIRouter(prefix="/api", tags=["simulate"])


# Scenario definitions matching generator/generate_logs.py
SCENARIOS = {
    "shadow_ai": {
        "name": "Shadow AI Upload",
        "description": "User uploads sensitive data to unapproved AI service",
        "expected_risk": "HIGH",
        "logs": [
            {
                "user_id": "demo_user@company.com",
                "domain": "claude.ai",
                "url": "/api/v1/messages",
                "method": "POST",
                "upload_size_bytes": 15_000_000,
            }
        ]
    },
    "data_leak": {
        "name": "Data Exfiltration (Blacklisted)",
        "description": "User uploads data to blacklisted file-sharing service",
        "expected_risk": "CRITICAL",
        "logs": [
            {
                "user_id": "demo_user@company.com",
                "domain": "wetransfer.com",
                "url": "/api/v1/transfer",
                "method": "POST",
                "upload_size_bytes": 50_000_000,
            }
        ]
    },
    "false_positive": {
        "name": "Safe Traffic (Whitelisted)",
        "description": "User accesses approved company domain",
        "expected_risk": "SAFE",
        "logs": [
            {
                "user_id": "demo_user@company.com",
                "domain": "drive.company.com",
                "url": "/api/v1/upload",
                "method": "POST",
                "upload_size_bytes": 5_000_000,
            }
        ]
    },
    # Alias mappings for different frontend naming
    "blacklist": None,  # Will map to data_leak
    "whitelist": None,  # Will map to false_positive
}

# Alias mappings
SCENARIOS["blacklist"] = SCENARIOS["data_leak"]
SCENARIOS["whitelist"] = SCENARIOS["false_positive"]


class SimulateRequest(BaseModel):
    type: str = "shadow_ai"


# Collector URL - the collector runs on port 8000 in Docker network
COLLECTOR_URL = "http://collector:8000/logs"
# Fallback for local development
COLLECTOR_URL_LOCAL = "http://localhost:8000/logs"


@router.post("/simulate")
async def simulate_attack(request: SimulateRequest):
    """
    Send a simulated log to the collector.
    The worker will process it and create alerts.
    """
    scenario_type = request.type.lower()
    
    if scenario_type not in SCENARIOS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid scenario type. Valid types: shadow_ai, data_leak, false_positive"
        )
    
    scenario = SCENARIOS[scenario_type]
    
    # Build log with current timestamp
    log_entry = scenario["logs"][0].copy()
    log_entry["ts"] = datetime.now(timezone.utc).isoformat()
    
    # Send to collector
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Try Docker network first, then localhost
        for url in [COLLECTOR_URL, COLLECTOR_URL_LOCAL]:
            try:
                response = await client.post(url, json=log_entry)
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "message": f"Simulation '{scenario['name']}' sent successfully",
                        "scenario": scenario_type,
                        "expected_risk": scenario["expected_risk"],
                        "log_sent": log_entry
                    }
            except httpx.RequestError:
                continue
    
    # If we get here, neither URL worked
    raise HTTPException(
        status_code=503, 
        detail="Could not reach collector service. Make sure the backend is running."
    )
