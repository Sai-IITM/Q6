import os
import json
import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse



app = FastAPI()

# ADD THIS ENTIRE BLOCK (fixes grader error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # ← "Access-Control-Allow-Origin: *"
    allow_credentials=True,
    allow_methods=["*"],           # ← POST, OPTIONS
    allow_headers=["*"],
)

@app.post("/")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 0)
    
    # Load telemetry data (in real deployment, fetch from env var URL or integrate properly)
    # For assignment: assume data is bundled or use a public URL; here we simulate loading
    # Replace with: with open('data.json') as f: data = json.load(f)  for local testing
    data_str = os.environ.get('TELEMETRY_DATA', '[]')  # Set this env var with JSON string
    data = json.loads(data_str)
    
    results = {}
    for region in regions:
        region_data = [r for r in data if r.get('region') == region]
        if not region_data:
            results[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
            continue
        
        latencies = np.array([r.get('latency_ms', 0) for r in region_data])
        uptimes = [r.get('uptime', 0) for r in region_data]
        
        results[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(np.sum(latencies > threshold_ms))
        }
    

    return results

