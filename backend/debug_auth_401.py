import requests

def test():
    # Attempt to sign up or login
    email = "test401@test.com"
    pwd = "Password123"
    role = "student"
    
    url = "http://localhost:8000/api/v1/auth/signup"
    signup_data = {
        "email": email,
        "password": pwd,
        "confirmPassword": pwd,
        "name": "Test User",
        "role": role,
    }
    
    res = requests.post(url, json=signup_data)
    
    if res.status_code == 400 and "already registered" in res.text:
       print("User already exists, attempting login instead")
       res = requests.post("http://localhost:8000/api/v1/auth/login", json={"email": email, "password": pwd, "role": role})
       
    print("Auth Result:", res.status_code, res.text)
    
    if res.status_code != 200:
        return
        
    data = res.json()
    token = data["data"]["access_token"]
    user_id = data["data"]["user"]["id"]
    
    print("Token length:", len(token))
    
    # Now attempt fetching resumes
    print("Fetching resumes for user_id:", user_id)
    headers = {"Authorization": f"Bearer {token}"}
    res2 = requests.get(f"http://localhost:8000/api/v1/resumes/user/{user_id}", headers=headers)
    print("Resumes Result:", res2.status_code, res2.text)

if __name__ == "__main__":
    test()
