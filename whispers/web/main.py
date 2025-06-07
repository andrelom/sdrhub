from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import os

app = FastAPI()

# Caminhos padrões configuráveis
HEARTBEAT_PATH = "recordings/heartbeat.log"
LOG_PATH = "recordings/contacts_log.csv"

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
      <head><title>SDR Monitor Status</title></head>
      <body>
        <h1>✅ SDR Monitor is running</h1>
        <ul>
          <li><a href='/heartbeat'>Download <code>heartbeat.log</code></a></li>
          <li><a href='/log'>Download <code>contacts_log.csv</code></a></li>
        </ul>
      </body>
    </html>
    """

@app.get("/heartbeat")
def get_heartbeat():
    if not os.path.isfile(HEARTBEAT_PATH):
        raise HTTPException(status_code=404, detail="heartbeat.log not found")
    return FileResponse(HEARTBEAT_PATH, filename="heartbeat.log", media_type="text/plain")

@app.get("/log")
def get_log():
    if not os.path.isfile(LOG_PATH):
        raise HTTPException(status_code=404, detail="contacts_log.csv not found")
    return FileResponse(LOG_PATH, filename="contacts_log.csv", media_type="text/csv")
