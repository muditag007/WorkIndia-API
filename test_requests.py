import requests
import json
import urllib.parse

BASE_URL = "http://127.0.0.1:5000/api"

def test_signup():
    url = f"{BASE_URL}/signup"
    payload = {
        "username": "test_user",
        "password": "test_password",
        "email": "test_user@example.com"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Signup Response:", response.json())
        assert response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print(f"Response content: {response.text}")

def test_login():
    url = f"{BASE_URL}/login"
    payload = {
        "username": "test_user",
        "password": "test_password"
    }
    try:
        response = requests.post(url, json=payload)
        print("Login Response:", response.json())
        assert response.status_code == 200
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        print(f"Response content: {response.text}")



def test_add_short(access_token):
    url = f"{BASE_URL}/shorts/create"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-api-key': 'your_admin_api_key'
    }
    payload = {
        "category": "news",
        "title": "All The Best for placements",
        "author": "Pranav",
        "publish_date": "2023-01-01 16:00:00",
        "content": "Lorem ipsum ...",
        "actual_content_link": "http://instagram.com/placements",
        "image": "",
        "votes": {
            "upvote": 0,
            "downvote": 0
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        print("Response content:", response.content)
        return

    try:
        response_data = response.json()
        print("Add Short Response:", response_data)
        assert response.status_code == 200
        assert response_data['status_code'] == 200
        assert 'short_id' in response_data
    except requests.exceptions.JSONDecodeError as e:
        print("Failed to decode JSON response:", e)
        print("Response content:", response.content)

def test_get_shorts_feed():
    url = f"{BASE_URL}/shorts/feed"
    response = requests.get(url)
    print("Get Shorts Feed Response:", response.json())
    assert response.status_code == 200

def test_filter_shorts(access_token):
    url = f"{BASE_URL}/shorts/filter"
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    filter_params = {
        "category": "news",
        "publish_date": "2023-01-01T16:00:00Z",
        "upvote": 0
    }
    search_params = {
        "title": "placements",
        "keyword": "Lorem",
        "author": "Pranav"
    }
    params = {
        "filter": urllib.parse.urlencode(filter_params),
        "search": urllib.parse.urlencode(search_params)
    }

    response = requests.get(url, headers=headers, params=params)
    print("Filter Shorts Response:", response.json())
    assert response.status_code == 200

if __name__ == "__main__":
    test_signup()
    token = test_login()
    test_add_short(token)
    test_get_shorts_feed()
    test_filter_shorts(token)
