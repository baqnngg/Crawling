from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

# 결과 저장 리스트
all_restaurants = []

# 페이지 이동을 위한 offset 설정 (0, 30, 60...)
offset = 0

# Playwright 실행
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0")

    while True:
        url = f"https://www.tripadvisor.co.kr/Restaurants-g1047895-oa{offset}-Chungju_Chungcheongbuk_do.html"
        print(f"📡 크롤링 중: {url}")
        page.goto(url)
        page.wait_for_timeout(5000)  # 렌더링 대기

        # 페이지 HTML 가져오기
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # 맛집 이름 추출
        restaurant_names = []
        for link in soup.find_all("a", href=True):
            if "/Restaurant_Review-" in link["href"]:
                name = link.get_text(strip=True)
                if name and name not in all_restaurants:
                    restaurant_names.append(name)

        if not restaurant_names:
            print("🔚 더 이상 맛집 없음.")
            break

        print(f"✅ {len(restaurant_names)}개 수집됨")
        all_restaurants.extend(restaurant_names)

        offset += 30
        time.sleep(1)  # 서버에 부담 줄이기

    browser.close()

# 결과 출력
print("\n📋 [충주 맛집 리스트]")
for i, name in enumerate(all_restaurants, 1):
    print(f"{i}. {name}")

print(soup)