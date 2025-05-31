import requests
from dotenv import load_dotenv
import os

def get_coordinates_kakao(place_name, rest_api_key):
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {rest_api_key}"}
    params = {"query": place_name}

    response = requests.get(url, headers=headers, params=params)
    result = response.json()

    if result['documents']:
        first_match = result['documents'][0]
        name = first_match['place_name']
        lat = first_match['y']
        lng = first_match['x']
        return name, lat, lng
    else:
        return None, None, None

# 예시 사용
place = input()
load_dotenv()
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

name, lat, lng = get_coordinates_kakao(place, KAKAO_API_KEY)

if name:
    print(f"📍 {name} 의 위치는 위도: {lat}, 경도: {lng}")
else:
    print("😢 장소를 찾을 수 없습니다.")
