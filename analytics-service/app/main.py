import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyticsEvent
import clickhouse_connect

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse-server")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DATABASE", "analytics")
CLICKHOUSE_TABLE = os.getenv("CLICKHOUSE_TABLE", "events")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_client_with_retry(retries: int = 20, delay: float = 1.5):
    """
    Lazily create a client with retry so the pod doesn't crash if ClickHouse isn't ready yet.
    """
    last_err = None
    for _ in range(retries):
        try:
            return clickhouse_connect.get_client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD)
        except Exception as e:
            last_err = e
            time.sleep(delay)
    raise last_err

@app.on_event("startup")
def bootstrap_clickhouse():
    try:
        client = get_client_with_retry(retries=60, delay=2)  # ~2 minutes
        client.command(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB}")
        client.command(f"""
            CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB}.{CLICKHOUSE_TABLE} (
                event_type String,
                page_url String,
                user_agent Nullable(String),
                session_id Nullable(String),
                ts DateTime DEFAULT now()
            ) ENGINE = MergeTree ORDER BY ts
        """)
    except Exception as e:
        # Don't crash the container; we'll retry on the first /track call.
        import logging
        logging.warning("ClickHouse not ready yet: %s", e)

@app.get("/")
def health():
    return {"status": "ok", "db": CLICKHOUSE_DB, "table": CLICKHOUSE_TABLE}

@app.post("/track")
async def track_event(event: AnalyticsEvent):
    try:
        client = get_client_with_retry()
        client.insert(
            f"{CLICKHOUSE_DB}.{CLICKHOUSE_TABLE}",
            [[event.event_type, event.page_url, event.user_agent, event.session_id]],
            column_names=["event_type", "page_url", "user_agent", "session_id"],
        )
        return {"message": "Event tracked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ClickHouse insert failed: {str(e)}")
