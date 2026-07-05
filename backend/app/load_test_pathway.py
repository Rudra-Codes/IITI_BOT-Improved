import asyncio
import httpx
import time
import statistics

URL = "http://0.0.0.0:8003/ask"
PAYLOAD = {
    "chat_id": 0,
    "email": "load_test",
    "queries": "Who Is Rudra Chitkara?"
}
HEADERS = {
    "Content-Type": "application/json"
}

# Configuration for the load test
NUM_REQUESTS = 15
CONCURRENCY = 5

async def fetch(client, i):
    start_time = time.time()
    try:
        response = await client.post(URL, json=PAYLOAD, headers=HEADERS, timeout=60.0)
        latency = time.time() - start_time
        return {"status_code": response.status_code, "latency": latency, "error": None}
    except Exception as e:
        latency = time.time() - start_time
        return {"status_code": None, "latency": latency, "error": str(e)}

async def run_load_test():
    print(f"Starting load test on {URL}")
    print(f"Total Requests: {NUM_REQUESTS}")
    print(f"Concurrency Limit: {CONCURRENCY}")
    
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    async def bound_fetch(client, i):
        async with semaphore:
            return await fetch(client, i)

    start_time = time.time()
    
    # httpx.AsyncClient handles connection pooling for us
    limits = httpx.Limits(max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY)
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = [bound_fetch(client, i) for i in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
    total_time = time.time() - start_time
    
    # Process results
    latencies = [r["latency"] for r in results if r["status_code"] == 200]
    errors = [r for r in results if r["status_code"] != 200]
    
    successful_requests = len(latencies)
    failed_requests = len(errors)
    
    print("\n" + "="*40)
    print("--- Load Test Results ---")
    print("="*40)
    print(f"Total Time Taken:     {total_time:.2f} seconds")
    print(f"Successful Requests:  {successful_requests}")
    print(f"Failed Requests:      {failed_requests}")
    
    if successful_requests > 0:
        throughput = successful_requests / total_time
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Calculate percentiles (handle case where not enough data points exist)
        if len(latencies) > 1:
            p95_latency = statistics.quantiles(latencies, n=100)[94]
            p99_latency = statistics.quantiles(latencies, n=100)[98]
        else:
            p95_latency = latencies[0]
            p99_latency = latencies[0]
        
        print("\n" + "="*40)
        print("--- Metrics for Resume ---")
        print("="*40)
        print(f"Throughput:           {throughput:.2f} Requests/sec")
        print(f"Average Latency:      {avg_latency:.4f} seconds")
        print(f"Min Latency:          {min_latency:.4f} seconds")
        print(f"Max Latency:          {max_latency:.4f} seconds")
        print(f"95th Percentile (P95): {p95_latency:.4f} seconds")
        print(f"99th Percentile (P99): {p99_latency:.4f} seconds")
        
        print("\n[Resume Bullet Point Inspiration]")
        print(f"- Engineered and stress-tested backend architecture, achieving a throughput of {throughput:.2f} RPS with a P95 latency of {p95_latency:.4f}s under concurrent load.")
        print(f"- Optimized Pathway RAG server to handle {CONCURRENCY} concurrent users seamlessly, maintaining an average response time of {avg_latency:.4f}s.")
        
    if failed_requests > 0:
        print("\n--- Errors ---")
        error_counts = {}
        for r in errors:
            err_key = r['status_code'] or type(r['error']).__name__ if r['error'] else "Unknown"
            error_counts[err_key] = error_counts.get(err_key, 0) + 1
        for k, v in error_counts.items():
            print(f"Error [{k}]: {v} occurrences")

if __name__ == "__main__":
    asyncio.run(run_load_test())
