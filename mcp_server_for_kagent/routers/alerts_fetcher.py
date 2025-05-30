import logging
import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import re
from fastapi import Query




log = logging.getLogger(__name__)


router = APIRouter()

ALERTMANAGER_URL = "http://alertmanager-main.monitoring.svc.cluster.local:9093/api/v2/alerts" 
@router.get("/fetch/firing/alerts")
async def fetch_firing_alerts():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(ALERTMANAGER_URL)
            response.raise_for_status()
            alerts = response.json()
            firing_alerts = [alert for alert in alerts if alert.get("status", {}).get("state") == "active"]
            return JSONResponse(content=firing_alerts)
    except Exception as e:
        log.error(f"Error fetching alerts: {e}")
        return JSONResponse(content={"error": "Failed to fetch alerts"}, status_code=500)


@router.get("/fetch/all/alerts")
async def fetch_all_alerts():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(ALERTMANAGER_URL)
            response.raise_for_status()
            alerts = response.json()
            return JSONResponse(content=alerts)
    except Exception as e:
        log.error(f"Error fetching alerts: {e}")
        return JSONResponse(content={"error": "Failed to fetch alerts"}, status_code=500)

@router.get("/fetch/alerts/by_name")
async def fetch_alerts_by_name_regex(
    name_regex: str = Query(..., description="Regex to match alertname, e.g., 'CPU'")
):
    try:
        pattern = re.compile(name_regex, re.IGNORECASE)
        async with httpx.AsyncClient() as client:
            response = await client.get(ALERTMANAGER_URL)
            response.raise_for_status()
            alerts = response.json()
            firing_alerts = [alert for alert in alerts if alert.get("status", {}).get("state") == "active"]
            matched_alerts = []
            for alert in firing_alerts:
                alertname = alert.get("labels", {}).get("alertname", "")
                if pattern.search(alertname):
                    matched_alerts.append({
                        "alertname": alertname,
                        "labels": alert.get("labels", {}),
                        "annotations": alert.get("annotations", {}),
                        "summary": alert.get("annotations", {}).get("summary", "")
                    })
            return JSONResponse(content=matched_alerts)
    except Exception as e:
        log.error(f"Error fetching alerts by name regex: {e}")
        return JSONResponse(content={"error": "Failed to fetch alerts"}, status_code=500)

