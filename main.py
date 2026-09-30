import subprocess
import time
import urllib.request
import atexit
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import config
from app.api import upload, query, documents

logger = logging.getLogger(__name__)

# ============================================================
# OLLAMA SERVER PROCESS MANAGEMENT
# ============================================================

ollama_process = None

def is_ollama_running(url: str = "http://localhost:11434/api/tags") -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_ollama_server():
    global ollama_process
    if is_ollama_running():
        print("[INFO] Ollama server is already running on http://localhost:11434")
        return

    print("[INFO] Starting local Ollama server process ('ollama serve')...")
    try:
        creation_flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        ollama_process = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags
        )
        
        start_time = time.time()
        while time.time() - start_time < 10:
            if is_ollama_running():
                print("[INFO] Ollama server started successfully and is ready.")
                return
            time.sleep(0.5)
        print("[WARNING] Ollama server process launched, but did not respond on port 11434 within 10 seconds.")
    except Exception as e:
        print(f"[ERROR] Failed to launch Ollama server process: {e}")

def stop_ollama_server():
    global ollama_process
    if ollama_process and ollama_process.poll() is None:
        print("\n[INFO] Stopping Ollama server process...")
        try:
            ollama_process.terminate()
            ollama_process.wait(timeout=5)
        except Exception:
            try:
                ollama_process.kill()
            except Exception:
                pass
        print("[INFO] Ollama server process stopped.")
        ollama_process = None

atexit.register(stop_ollama_server)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_ollama_server()
    yield
    stop_ollama_server()

# ============================================================
# FASTAPI APPLICATION SETUP
# ============================================================

app = FastAPI(
    title="PDF AI Assistant",
    description="Dual-Intelligence System featuring AI PDF Chatbot & Semantic Search Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(documents.router)

# ============================================================
# TAB HEARTBEAT & AUTO SHUTDOWN MANAGEMENT
# ============================================================

last_heartbeat_time = time.time()
heartbeat_received = False

@app.post("/api/heartbeat", tags=["System"])
@app.get("/api/heartbeat", tags=["System"])
async def heartbeat_ping():
    global last_heartbeat_time, heartbeat_received
    last_heartbeat_time = time.time()
    heartbeat_received = True
    return {"status": "alive", "timestamp": last_heartbeat_time}

@app.post("/api/shutdown", tags=["System"])
async def shutdown_server():
    print("\n[INFO] Browser tab closed. Shutdown signal received. Terminating application...")
    stop_ollama_server()
    os._exit(0)

def monitor_tab_closure():
    global last_heartbeat_time, heartbeat_received
    # Wait 20s initial grace period for browser window to connect
    time.sleep(20)
    while True:
        time.sleep(3)
        if heartbeat_received and (time.time() - last_heartbeat_time > 12):
            print("\n[INFO] Browser tab closed or inactive (>12s since last heartbeat). Automatically shutting down server...")
            stop_ollama_server()
            os._exit(0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    import threading
    start_ollama_server()
    monitor_thread = threading.Thread(target=monitor_tab_closure, daemon=True)
    monitor_thread.start()
    yield
    stop_ollama_server()

# Health check route
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "PDF AI Assistant",
        "version": "1.0.0"
    }

# Serve Frontend static assets
frontend_dir = config.PROJECT_ROOT / "frontend"
if (frontend_dir / "css").exists():
    app.mount("/css", StaticFiles(directory=frontend_dir / "css"), name="css")
if (frontend_dir / "js").exists():
    app.mount("/js", StaticFiles(directory=frontend_dir / "js"), name="js")

@app.get("/", tags=["Frontend"])
async def serve_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend index.html not found."}

if __name__ == "__main__":
    import os
    import socket

    def find_available_port(start_port: int) -> int:
        for p in range(start_port, start_port + 20):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", p))
                    return p
                except OSError:
                    continue
        return start_port

    target_port = int(os.getenv("PORT", "8000"))
    port = find_available_port(target_port)
    if port != target_port:
        print(f"\n[WARNING] Port {target_port} is currently locked or in use. Automatically falling back to free port {port}.")
    print(f"[INFO] Serving PDF AI Assistant on http://127.0.0.1:{port}\n")
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=False)
