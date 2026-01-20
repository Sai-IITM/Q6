from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import numpy as np

app = FastAPI()

# Fix CORS completely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Handles OPTIONS + POST
    allow_headers=["*"],
)

@app.post("/")  # Handles POST {"regions":["emea","apac"],"threshold_ms":185}
@app.options("/")  # Handles browser OPTIONS preflight
async def analytics(request: Request):
    if request.method == "OPTIONS":
        return {}
    
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 0)
    
    # Load your q-vercel-latency.json data
    data_str = os.environ.get('TELEMETRY_DATA', '[]')
    if not data_str:
        # Fallback: try local file for testing
        try:
            with open('q-vercel-latency.json') as f:
                data = json.load(f)
        except:
            data = []
    else:
        data = json.loads(data_str)
    
    results = {}
    for region in regions:
        region_data = [r for r in data if r.get('region') == region]
        if not region_data:
            results[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
            continue
        
        latencies = np.array([r.get('latency_ms', 0) for r in region_data])
        uptimes = [r.get('uptime', 0) for r in region_data])
        
        results[region] = {
            "avg_latency": float(np.mean(latencies)) if len(latencies) > 0 else 0,
            "p95_latency": float(np.percentile(latencies, 95)) if len(latencies) > 0 else 0,
            "avg_uptime": float(np.mean(uptimes)) if uptimes else 0,
            "breaches": int(np.sum(latencies > threshold_ms))
        }
    
    return results


