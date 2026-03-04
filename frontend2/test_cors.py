
import urllib.request
import urllib.error
import sys

url = "http://127.0.0.1:8001/api/auth/register/"
origin = "http://localhost:8000"

print(f"Testing CORS for {url} from Origin: {origin}")

req = urllib.request.Request(url, method="OPTIONS")
req.add_header("Origin", origin)
req.add_header("Access-Control-Request-Method", "POST")

try:
    with urllib.request.urlopen(req, timeout=5) as response:
        print(f"Status: {response.getcode()}")
        headers = response.info()
        cors_origin = headers.get("Access-Control-Allow-Origin")
        print(f"Access-Control-Allow-Origin: {cors_origin}")
        
        if cors_origin == origin or cors_origin == "*":
            print("CORS is configured correctly!")
        else:
            print("CORS Header missing or incorrect.")
            print("Response Headers:")
            print(headers)

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print(e.headers)
except Exception as e:
    print(f"Error: {e}")
