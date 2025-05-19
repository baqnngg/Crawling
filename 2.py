from bs4 import BeautifulSoup

# 올바른 경로 설정
file_path = r"C:\Users\User\Downloads\충주 맛집_음식점 추천 순위 Best 10 - Tripadvisor.html"

# HTML 파일 열기
with open(file_path, "r", encoding="utf-8") as f:   
    html = f.read()

# 파싱
soup = BeautifulSoup(html, "html.parser")

# 맛집 이름 수집
restaurants = []
link2 = []
for link in soup.find_all("a", href=True):
    if "/Restaurant_Review-" in link["href"]:
        name = link.get_text(strip=True)
        if name and name not in restaurants:
            link2.append(link.get_text)
            restaurants.append(name)

# 출력
print("\n📋 [충주 맛집 리스트]")
for i, name in enumerate(restaurants, 1):
    print(f"{i}. {name}")

with open("restaurant_names.txt", "w", encoding="utf-8") as f:
        for name in restaurants:
            f.write(name + "\n")
print(link2)