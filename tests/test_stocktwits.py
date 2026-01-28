import requests
import json

def test_stocktwits():
    ticker = "AAPL"
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            print(f"Found {len(messages)} messages.")
            for msg in messages[:2]:
                print(f"User: {msg['user']['username']}")
                print(f"Body: {msg['body'][:50]}...")
                print(f"Sentiment: {msg.get('entities', {}).get('sentiment')}")
                print("-" * 10)
        else:
            print(f"Failed to fetch data: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stocktwits()
