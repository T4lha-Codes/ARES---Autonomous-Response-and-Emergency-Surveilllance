# 🛡️ A.R.E.S — Autonomous Response and Emergency Surveillance

A privacy-preserving crime detection system built on **Federated Learning**, **YOLOv8**, and **Stackelberg Game Theory**. Multiple camera nodes collaboratively train a shared AI model to detect crimes — without ever sharing raw video footage.

---

## 📌 What It Does

- Detects **5 crime classes** in CCTV footage: `Arrest`, `Fighting`, `Shooting`, `Theft`, `Vandalism`
- Uses **Federated Learning** — raw video never leaves the camera node, only model weights are shared
- Applies **Stackelberg Game Theory** to intelligently select which camera nodes participate each training round
- Logs all detections to a database and displays them on a real-time **Electron dashboard**
- Achieved **83.9% accuracy** after 5 federated learning rounds (up from 73.8% baseline)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FL Server (Port 8085)              │
│         FedAvg Aggregation + Stackelberg Scheduler   │
└────────────┬─────────────────┬──────────────────────┘
             │                 │
     ┌───────▼──────┐  ┌───────▼──────┐  ┌────────────────┐
     │  FL Client 0 │  │  FL Client 1 │  │  FL Client 2   │
     │  footage1.mp4│  │  footage2.mp4│  │  footage3.mp4  │
     │  (Camera Node│  │  (Camera Node│  │  (Camera Node) │
     └──────────────┘  └──────────────┘  └────────────────┘
             │
     ┌───────▼──────────────────────────┐
     │       FastAPI Backend (Port 8000) │
     │       SQLite Database (alerts.db) │
     └───────┬──────────────────────────┘
             │
     ┌───────▼──────────────┐
     │  Electron Dashboard  │
     │  (7 screens)         │
     └──────────────────────┘
```

---

## 🧠 Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core backend language |
| **YOLOv8s (Ultralytics)** | Crime detection AI model |
| **Flower (flwr)** | Federated Learning framework |
| **PyTorch** | Model weight manipulation |
| **OpenCV (cv2)** | Video frame processing |
| **FastAPI + Uvicorn** | REST API backend |
| **SQLite** | Alert logging database |
| **Electron + Node.js** | Desktop dashboard application |
| **Chart.js** | Accuracy & reputation charts |
| **NumPy** | Numerical operations for FL |

---

## 📁 Project Structure

```
ARES/
├── model/
│   ├── best.pt               ← Original trained YOLOv8s model (baseline)
│   └── global_model.pt       ← Improved model after FL training (auto-generated)
│
├── server/
│   ├── fl_server.py          ← FL server — coordinates training rounds, FedAvg aggregation
│   └── stackelberg.py        ← Stackelberg scheduler — reputation-based client selection
│
├── client/
│   ├── fl_client.py          ← FL client — represents one camera node
│   └── detector.py           ← Video processor — runs YOLO on footage frames
│
├── api/
│   └── main.py               ← FastAPI backend — upload video, get alerts, get history
│
├── dashboard/                ← Electron desktop app (7 screens)
│
├── footage/
│   ├── client1/              ← Local footage for camera node 1
│   ├── client2/              ← Local footage for camera node 2
│   └── client3/              ← Local footage for camera node 3
│
├── outputs/
│   └── training_history.json ← FL accuracy per round (auto-generated)
│
└── alerts.db                 ← SQLite database of all detected crimes
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or 3.11
- Node.js 18+ (for dashboard)
- Windows / Linux / macOS

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ARES.git
cd ARES
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install flwr ultralytics torch torchvision fastapi uvicorn python-multipart opencv-python numpy
```

### 4. Install dashboard dependencies

```bash
cd dashboard
npm install
cd ..
```

### 5. Add your model

Place your trained YOLOv8 model file at:
```
model/best.pt
```

---

## 🚀 Running the System

You need **5 separate terminals**, all with the virtual environment activated.

> ⚠️ Always start the FL server **before** the clients.

### Terminal 1 — FL Server
```bash
cd server
python fl_server.py
```
You should see: `Waiting for 3 clients to connect...`

### Terminal 2 — FL Client 0
```bash
python client/fl_client.py 0 footage/client1/footage1.mp4
```

### Terminal 3 — FL Client 1
```bash
python client/fl_client.py 1 footage/client2/footage2.mp4
```

### Terminal 4 — FL Client 2
```bash
python client/fl_client.py 2 footage/client3/footage3.mp4
```

Once 2+ clients connect, FL training starts automatically and runs for **5 rounds**.

### Terminal 5 — API Server
```bash
cd api
uvicorn main:app --reload --port 8000
```

### Dashboard
```bash
cd dashboard
npm start
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload-video/{client_id}` | Upload footage and run detection |
| `GET` | `/alerts` | Get all logged crime alerts |
| `GET` | `/training-history` | Get FL accuracy per round |
| `GET` | `/node-status` | Get camera node status |

API documentation auto-generated at: `http://localhost:8000/docs`

---

## 📈 Training Results

| Round | Accuracy |
|---|---|
| Round 1 | 73.8% |
| Round 2 | 76.9% |
| Round 3 | 79.6% |
| Round 4 | 79.6% |
| Round 5 | **83.9%** |

---

## 🔒 Privacy Guarantee

A.R.E.S is built with **Privacy by Design**. Raw video footage **never leaves** the camera node. Only mathematical model weights (numpy arrays) are transmitted to the FL server. It is mathematically impossible to reconstruct any video frame from the transmitted weights.

---

## 🎮 How Stackelberg Game Theory Works

The FL server acts as the **Leader** and camera nodes act as **Followers** in a Stackelberg game:

- Each client starts with a reputation score of `0.5`
- After each round, if a client's weight update **improved** the model → reputation `+0.1` (max `1.0`)
- If a client's update **worsened** the model → reputation `-0.05` (min `0.1`)
- Clients with **higher reputation** are prioritized for selection in the next round
- This makes training more efficient and resistant to poor-quality nodes

---

## 🗄️ Database Schema

Alerts are stored in `alerts.db` (SQLite):

```sql
CREATE TABLE alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT,
    client_id   TEXT,
    event_type  TEXT,
    confidence  REAL,
    time_in_video TEXT,
    video_name  TEXT
)
```

---

## 🐛 Common Issues

| Error | Cause | Fix |
|---|---|---|
| `Connection refused on port 8085` | FL server not started | Start server before clients |
| `Could not import module main` | Running uvicorn from wrong directory | `cd api` first, then run uvicorn |
| `Failed to serialize response!` | Client crashed in `fit()` method | Check video path exists and model loads correctly |
| `Module not found: flwr` | Virtual env not activated | Run `venv\Scripts\activate` |
| `Video not found` | Wrong footage path | Verify path: `footage/client1/footage1.mp4` |

---

## 📄 License

This project was developed as a Final Year Project at NUCES. For academic use only.
