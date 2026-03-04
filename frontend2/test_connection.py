
import urllib.request
import urllib.error
import sys

url = "http://127.0.0.1:8001/api/"

print(f"Testing connection to {url}...")

try:
    with urllib.request.urlopen(url, timeout=5) as response:
        print(f"Success! Status Code: {response.getcode()}")
        print("Backend is running and reachable.")
except urllib.error.HTTPError as e:
    # 404 is actually GOOD here - it means the server is running but just didn't find the root /api/ path (which might not have a view)
    print(f"Server reachable but returned error: {e.code} {e.reason}")
    print("This confirms the server IS running on port 8001.")
except urllib.error.URLError as e:
    print(f"Failed to connect: {e.reason}")
    print("The backend server is NOT reachable on port 8001.")
    print("Did you run 'python manage.py runserver 8001'?")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
