import requests
import pandas as pd

def get_coordinates_to_excel(query, search_coord, output_file):
    base_url = "https://map.naver.com/v5/api/search/allSearch"
    
    params = {
        'query': query,
        'type': 'all',
        'searchCoord': search_coord,
        'boundary': ''
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Referer': 'https://map.naver.com/',
        'Accept': 'application/json, text/plain, */*',
    }
    
    response = requests.get(base_url, params=params, headers=headers)
    
    try:
        data = response.json()
    except Exception as e:
        print("JSON parsing error:", e)
        return
    
    places = data.get('result', {}).get('place', {}).get('list', [])
    
    # 리스트를 딕셔너리 리스트로 변환
    rows = []
    for place in places:
        name = place.get('name')
        x = place.get('x')
        y = place.get('y')
        rows.append({'이름': name, 'x좌표': x, 'y좌표': y})
    
    # pandas DataFrame 생성
    df = pd.DataFrame(rows)
    
    # 엑셀 파일로 저장
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"{output_file} 파일로 저장 완료!")

if __name__ == "__main__":
    query = input()
    search_coord = "127.93883339999621;36.96102790000016"
    output_file = "좌표.xlsx"
    get_coordinates_to_excel(query, search_coord, output_file)
