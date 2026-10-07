# api/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil, os, sys, json, sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client.detector import process_video

app = FastAPI(title="A.R.E.S API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect("alerts.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT,
            client_id   TEXT,
            event_type  TEXT,
            confidence  REAL,
            frame_time  TEXT,
            video_name  TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def root():
    return {"status": "A.R.E.S API is running ✅"}

@app.post("/upload-video/{client_id}")
async def upload_video(client_id: str, file: UploadFile = File(...)):
    """Upload a footage file and run detection on it."""
    upload_path = f"uploads/{client_id}_{file.filename}"
    
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Run detection
    alerts = process_video(upload_path, client_id)
    
    # Save to database
    conn = sqlite3.connect("alerts.db")
    for alert in alerts:
        conn.execute("""
            INSERT INTO alerts (timestamp, client_id, event_type, confidence, frame_time, video_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            client_id,
            alert["event_type"],
            alert["confidence"],
            alert["timestamp"],
            file.filename
        ))
    conn.commit()
    conn.close()
    
    return {
        "status":           "success",
        "client_id":        client_id,
        "video":            file.filename,
        "total_detections": len(alerts),
        "alerts":           alerts
    }

@app.get("/alerts")
def get_alerts():
    """Get all logged alerts."""
    conn   = sqlite3.connect("alerts.db")
    rows   = conn.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
    conn.close()
    return {"alerts": [
        {"id": r[0], "timestamp": r[1], "client_id": r[2],
         "event_type": r[3], "confidence": r[4],
         "time_in_video": r[5], "video": r[6]}
        for r in rows
    ]}

@app.get("/training-history")
def get_training_history():
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    history_path = os.path.join(BASE_DIR, "outputs", "training_history.json")
    try:
        with open(history_path) as f:
            return {"history": json.load(f)}
    except FileNotFoundError:
        return {"history": []}

@app.get("/node-status")
def get_node_status():
    """Get status of all simulated camera nodes."""
    return {"nodes": [
        {"id": "Client_1", "status": "Active", "footage": "Street Scene"},
        {"id": "Client_2", "status": "Active", "footage": "Indoor Scene"},
        {"id": "Client_3", "status": "Active", "footage": "Mixed Scene"},
    ]}