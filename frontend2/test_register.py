
import urllib.request
import urllib.error
import json
import random
import sys

# Generate random user to avoid conflicts
rand_id = random.randint(1000, 9999)
email = f"test.user.{rand_id}@example.com"

url = "http://127.0.0.1:8001/api/auth/register/"

payload = {
    "email": email,
    "first_name": "Test",
    "last_name": "User",
    "phone_number": f"+92300000{rand_id}",
    "password": "password123",
    "password_confirm": "password123",
    "user_type": "donor",
    "blood_group": "O+",
    "date_of_birth": "1990-01-01",
    "city": "Lahore",
    "cnic": f"35202-0000{rand_id}-1" # Adding CNIC as it appeared in form HTML
}

data = json.dumps(payload).encode('utf-8')
headers = {
    "Content-Type": "application/json"
}

print(f"Testing Registration API: {url}")
print(f"Payload Email: {email}")

req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        print(f"Success! Status Code: {response.getcode()}")
        resp_body = response.read().decode('utf-8')
        try:
            print("Response:", json.loads(resp_body))
        except:
            print("Response Body:", resp_body)
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print("Error Body:", e.read().decode('utf-8'))
except urllib.error.URLError as e:
    print(f"Connection Failed: {e.reason}")
    print("Is the backend running on port 8001?")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
