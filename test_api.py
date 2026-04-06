import httpx
import asyncio

async def test_query():
    url = "http://localhost:8000/api/query"
    payload = {"query": "Show the last 5 transactions"}
    headers = {"Content-Type": "application/json"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        print("Status code:", response.status_code)
        print("Response JSON:", response.json())

asyncio.run(test_query())
