
import urllib.request
import urllib.error

url = "http://127.0.0.1:8001/api/auth/register/"
origin = "http://localhost:8000"

print(f"Testing OPTIONS request (CORS Preflight) to: {url}")
print(f"Simulating Origin: {origin}")

req = urllib.request.Request(url, method="OPTIONS")
req.add_header("Origin", origin)
req.add_header("Access-Control-Request-Method", "POST")
req.add_header("Access-Control-Request-Headers", "Content-Type")

try:
    with urllib.request.urlopen(req, timeout=5) as response:
        print(f"Status: {response.getcode()}")
        for header, value in response.info().items():
            if header.lower().startswith("access-control-"):
                print(f"{header}: {value}")
        
        cors_origin = response.info().get("Access-Control-Allow-Origin")
        if cors_origin:
            print(f"✅ CORS Header Found: {cors_origin}")
        else:
            print("❌ CORS Header MISSING!")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
except Exception as e:
    print(f"Error: {e}")
