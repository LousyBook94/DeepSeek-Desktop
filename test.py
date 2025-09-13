FORWARD_BASE = "https://chat.z.ai/api"  # Change to your kimi-free-api URL
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImU2NTA4OWM3LWI0NmUtNDgzZC1hYjhiLWVlMDAxMmQxODdjNyIsImxhc3RfcGFzc3dvcmRfY2hhbmdlIjoxNzUwNjYwODczLCJleHAiOjE3NTc3NjMwMzB9.0vh-FuRgzN775AH_VffUOymnxdI2v6Nxa0yygSrWxWA"         # The refresh_token from kimi.moonshot.cn

import os
import json
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, Any, AsyncGenerator

app = FastAPI()

FORWARD_URL = os.getenv("FORWARD_URL", FORWARD_BASE)

async def forward_request(request: Request) -> httpx.Response:
    """Forward the incoming request to the target URL"""
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    url = f"{FORWARD_URL}{request.url.path}"
    if request.url.query:
        url += f"?{request.url.query}"
    
    async with httpx.AsyncClient() as client:
        return await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=await request.body(),
            timeout=30.0
        )

def transform_json_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform the JSON response to add 'object': 'list' field"""
    if isinstance(data, dict) and "data" in data:
        # Create a new response with the 'object': 'list' field
        transformed_response = {
            "object": "list",
            "data": data["data"]
        }
        return transformed_response
    return data

async def process_stream(response: httpx.Response) -> AsyncGenerator[str, None]:
    """Process streaming response to transform data chunks"""
    buffer = ""
    async for chunk in response.aiter_text():
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if line.startswith("data: "):
                try:
                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str.strip() == "[DONE]":
                        yield "data: [DONE]\n"
                    else:
                        json_data = json.loads(data_str)
                        transformed = transform_json_response(json_data)
                        yield f"data: {json.dumps(transformed)}\n"
                except json.JSONDecodeError:
                    yield line + "\n"
            else:
                yield line + "\n"
    if buffer:
        yield buffer

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request):
    try:
        response = await forward_request(request)
        content_type = response.headers.get("content-type", "").split(";")[0].strip()
        
        # Handle JSON responses
        if content_type == "application/json":
            json_data = response.json()
            transformed_data = transform_json_response(json_data)
            return JSONResponse(content=transformed_data, status_code=response.status_code)
        
        # Handle streaming responses
        elif content_type == "text/event-stream":
            return StreamingResponse(
                process_stream(response),
                media_type="text/event-stream",
                status_code=response.status_code
            )
        
        # Handle all other response types
        else:
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items() 
                         if k.lower() not in ["content-encoding", "content-length"]}
            )
    
    except httpx.RequestError as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Upstream request failed: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)