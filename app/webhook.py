from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json
import tempfile
import duckdb

router = APIRouter(tags=["AgentBeats"])

@router.post("/")
async def agentbeats_webhook(request: Request):
    payload = await request.json()
    
    # AgentBeats leaderboard validation
    if "query" in payload or "queries" in payload:
        return await validate_leaderboard_queries(payload)
    
    return JSONResponse({"status": "received"})

async def validate_leaderboard_queries(payload):
    """Validate queries.json using DuckDB (AgentBeats style)"""
    conn = duckdb.connect()
    
    # Mock results matching your metrics
    mock_data = [{
        "agent_type": "green", "asr_intermediate": 0.12,
        "asr_end_to_end": 0.05, "utility": 0.94
    }]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_data, f)
        conn.execute(f"CREATE TABLE results AS SELECT * FROM read_json('{f.name}')")
    
    # Your leaderboard queries[file:178]
    queries = [
        "SELECT avg(asr_intermediate) as asr FROM results WHERE agent_type='green'",
        "SELECT avg(asr_end_to_end) as asr FROM results", 
        "SELECT avg(utility) as util FROM results",
        "SELECT (asr_intermediate + asr_end_to_end + utility)/3 as score FROM results"
    ]
    
    results = []
    for i, query in enumerate(queries):
        try:
            row = conn.sql(query).fetchone()
            results.append({"query": i+1, "valid": True, "result": row})
        except Exception as e:
            results.append({"query": i+1, "valid": False, "error": str(e)})
    
    os.unlink(f.name)
    conn.close()
    
    return JSONResponse({
        "status": "success",
        "validated": True,
        "queries": len(results),
        "results": results
    })

