import httpx

with open("test_resume.pdf", "wb") as f:
    f.write(b"%PDF-1.4 mock resume content")

# Let's get the token
response = httpx.post(
    "http://127.0.0.1:8000/api/v1/auth/login",
    json={"email": "nousinnihal4844@gmail.com", "password": "Password123!", "role": "student"}
)
print("Login status:", response.status_code)
if response.status_code != 200:
    print(response.text)
    exit(1)

token = response.json()["data"]["access_token"]

# Upload resume
files = {"file": ("test_resume.pdf", open("test_resume.pdf", "rb"), "application/pdf")}
headers = {"Authorization": f"Bearer {token}"}
response = httpx.post(
    "http://127.0.0.1:8000/api/v1/resumes/upload",
    files=files,
    headers=headers
)

print("\nUpload status:", response.status_code)
import json
print("Upload response:", json.dumps(response.json(), indent=2))
