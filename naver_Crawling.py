from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd

def crawl_naver_map(url, fields, scroll_count=7, driver_path=None, excel_filename="output.xlsx"):
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # 필요하면 주석 해제
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    time.sleep(3)

    # iframe 전환
    driver.switch_to.frame("searchIframe")
    time.sleep(2)

    scroll_container = driver.find_element(By.ID, "_pcmap_list_scroll_container")

    # 스크롤 내려서 더 많은 데이터 로드
    for _ in range(scroll_count):
        driver.execute_script("arguments[0].scrollTop += 1000;", scroll_container)
        time.sleep(1.2)

    items = driver.find_elements(By.CSS_SELECTOR, "li.UEzoS.rTjJo")

    data_list = []

    for item in items:
        data = {}
        for col_name, (selector, method) in fields.items():
            try:
                if method == "css":
                    elements = item.find_elements(By.CSS_SELECTOR, selector)
                elif method == "xpath":
                    elements = item.find_elements(By.XPATH, selector)
                else:
                    elements = []

                text = elements[0].text.strip() if elements else f"{col_name} 없음"
                data[col_name] = text

            except Exception as e:
                data[col_name] = f"오류 발생: {str(e)}"
        data_list.append(data)

    driver.quit()

    df = pd.DataFrame(data_list)
    df.to_excel(excel_filename, index=False)
    print(f"✅ 크롤링 완료 및 저장 - {excel_filename}")

# 엑셀 파일 읽고 데이터 수정하는 함수
def modify_excel(filename, new_filename):
    df = pd.read_excel(filename)

    # 예시: '별점'이 없으면 0으로 수정
    df.loc[df['별점'].str.contains('없음'), '별점'] = '0'

    # 예시: '이름' 컬럼 뒤에 ' (수정됨)' 추가
    df['이름'] = df['이름'].apply(lambda x: x + ' (수정됨)')

    # 수정된 데이터 저장
    df.to_excel(new_filename, index=False)
    print(f"✅ 엑셀 수정 완료 및 저장 - {new_filename}")

if __name__ == "__main__":
    driver_path = "C:\\Users\\il869\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    url = "https://map.naver.com/p/search/충주음식점"

    fields = {
        "이름": ("span.TYaxT", "css"),
        "카테고리": ("span.KCMnt", "css"),
        "설명": ("a.nyHXH", "css"),
        "별점": ("span.orXYY", "css"),
        "리뷰 수": (".//span[contains(text(), '리뷰')]", "xpath")
    }

    raw_excel = "충주음식점.xlsx"
    modified_excel = "충주음식점_수정본.xlsx"

    # 1. 크롤링해서 엑셀 저장
    crawl_naver_map(url, fields, scroll_count=20, driver_path=driver_path, excel_filename=raw_excel)

    # 2. 저장된 엑셀 읽고 수정 후 다시 저장
    modify_excel(raw_excel, modified_excel)
