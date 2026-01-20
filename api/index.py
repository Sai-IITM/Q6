from fastapi import FastAPI, Request
import json
import os
import numpy as np

app = FastAPI()

@app.post("/")
async def analytics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 0)
    
    data_str = os.environ.get('TELEMETRY_DATA', '[]')
    data = json.loads(data_str)
    
    results = {}
    for region in regions:
        region_data = [r for r in data if r.get('region') == region]
        latencies = np.array([r.get('latency_ms', 0) for r in region_data])
        uptimes = [r.get('uptime', 0) for r in region_data]  # ← FIXED
        
        results[region] = {
            "avg_latency": float(np.mean(latencies)) if len(latencies) > 0 else 0,
            "p95_latency": float(np.percentile(latencies, 95)) if len(latencies) > 0 else 0,
            "avg_uptime": float(np.mean(uptimes)) if uptimes else 0,
            "breaches": int(np.sum(latencies > threshold_ms))
        }
    
    return results



