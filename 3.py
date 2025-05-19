import os
import re
import requests
from bs4 import BeautifulSoup
import glob
from urllib.parse import urlparse

# 타겟 클래스 리스트
TARGET_CLASSES = ['biGQs _P fiohW alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU mtnKn ngXxk']

def extract_restaurant_names_from_file(file_path):
    """HTML 파일에서 식당 이름을 추출합니다."""
    restaurant_names = []

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        soup = BeautifulSoup(content, 'html.parser')

        # 1. 타이틀에서 찾기
        #if soup.title:
            #title_text = soup.title.text
            #if any(keyword in title_text.lower() for keyword in ['식당', '레스토랑', 'restaurant']):
                #restaurant_names.append(title_text.strip())

        # 2. 지정된 클래스명을 가진 요소에서 찾기
        restaurant_elements = soup.find_all(
            lambda tag: (
                tag.name in ['div', 'span', 'h1', 'h2', 'h3', 'a']
                and tag.has_attr('class')
                and all(cls in tag['class'] for cls in TARGET_CLASSES)
            )
        )
        for element in restaurant_elements:
            restaurant_names.append(element.text.strip())

        # 3. "restaurant" 또는 "식당"이 포함된 텍스트 찾기
        restaurant_texts = soup.find_all(string=lambda text: text and ('식당' in text))
        for text in restaurant_texts:
            parent = text.parent
            if parent.name not in ['script', 'style']:
                restaurant_names.append(text.strip())

        # 4. 메타 태그에서 식당 이름 찾기
        #meta_tags = soup.find_all('meta', attrs={'property': re.compile('og:title')})
        #for tag in meta_tags:
            #content = tag.get('content', '')
            #if content:
                #restaurant_names.append(content.strip())

        # 5. 이미지 alt 또는 src에서 식당 이름 유추
        #img_tags = soup.find_all('img', src=re.compile('restaurant'))
        #for img in img_tags:
            #src = img.get('src', '')
            #alt = img.get('alt', '')
            #if alt and ('restaurant' in alt.lower() or '식당' in alt):
                #restaurant_names.append(alt.strip())
            #elif src:
                #filename = os.path.basename(urlparse(src).path)
                #match = re.search(r'restaurant[_-]([^/._]+)', filename)
                #if match:
                    #restaurant_names.append(match.group(1).replace('-', ' ').replace('_', ' '))

    except Exception as e:
        print(f"파일 처리 중 오류 발생: {file_path} - {e}")

    restaurant_names = [name for name in restaurant_names if name.strip()]
    return list(set(restaurant_names))


def extract_restaurant_names_from_network_data(html_content):
    """네트워크 응답 데이터에서 식당 이름을 추출합니다."""
    restaurant_names = []

    soup = BeautifulSoup(html_content, 'html.parser')
    keywords = ['restaurant', '식당', '레스토랑', 'bistro', 'cafe', '카페', 'dining', '다이닝']

    # 텍스트 기반 추출
    for keyword in keywords:
        elements = soup.find_all(string=lambda text: text and keyword.lower() in text.lower())
        for element in elements:
            if element.parent.name not in ['script', 'style']:
                restaurant_names.append(element.strip())

    # 특정 클래스 포함 요소 추출
    restaurant_elements = soup.find_all(
        lambda tag: (
            tag.has_attr('class')
            and all(cls in tag['class'] for cls in TARGET_CLASSES)
        )
    )
    for element in restaurant_elements:
        restaurant_names.append(element.text.strip())

    # 리스트 항목에서 식당 추출
    list_items = soup.find_all('li')
    for item in list_items:
        item_text = item.text.strip()
        if len(item_text) < 50 and any(keyword in item_text.lower() for keyword in keywords):
            restaurant_names.append(item_text)

    restaurant_names = [name for name in restaurant_names if name.strip()]
    return list(set(restaurant_names))


def download_and_parse_from_urls(url_list):
    """URL 목록에서 식당 이름을 파싱합니다."""
    all_restaurant_names = []

    for url in url_list:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            restaurant_names = extract_restaurant_names_from_network_data(response.text)
            all_restaurant_names.extend(restaurant_names)

            print(f"URL에서 발견된 식당 이름: {url}")
            for name in restaurant_names:
                print(f" - {name}")

        except Exception as e:
            print(f"URL 처리 중 오류 발생: {url} - {e}")

    return list(set(all_restaurant_names))


def main():
    # 1. 로컬 HTML 파일에서 파싱
    html_files = glob.glob("*.html")
    print(f"총 {len(html_files)}개의 HTML 파일을 발견했습니다.")

    all_restaurant_names = []

    for file_path in html_files:
        print(f"파일 처리 중: {file_path}")
        restaurant_names = extract_restaurant_names_from_file(file_path)
        all_restaurant_names.extend(restaurant_names)

        print(f"파일에서 발견된 식당 이름:")
        for name in restaurant_names:
            print(f" - {name}")
        print("-" * 50)

    # 2. 네트워크 URL로부터 파싱
    urls = [
        "https://www.tripadvisor.co.kr/Restaurants-g1047895-oa0-Chungju_Chungcheongbuk_do.html"
    ]

    if urls:
        print("URL에서 식당 이름 파싱 중...")
        url_restaurant_names = download_and_parse_from_urls(urls)
        all_restaurant_names.extend(url_restaurant_names)

    # 결과 출력 및 저장
    all_restaurant_names = list(set(all_restaurant_names))
    print("\n=== 최종 식당 이름 목록 ===")
    for i, name in enumerate(all_restaurant_names, 1):
        print(f"{i}. {name}")

    with open("restaurant_names.txt", "w", encoding="utf-8") as f:
        for name in all_restaurant_names:
            f.write(name + "\n")

    print(f"\n총 {len(all_restaurant_names)}개의 식당 이름을 'restaurant_names.txt' 파일에 저장했습니다.")


if __name__ == "__main__":
    main()
