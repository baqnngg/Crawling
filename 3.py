from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 크롬 옵션 설정 (필요하면 추가)
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # 창 최대화

# 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 테스트용으로 구글 접속
driver.get("https://www.google.com")

print("정상 실행됨!")
driver.quit()