from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd

def crawl_naver_map(url, fields, scroll_count=7, driver_path=None, excel_filename="output.xlsx"):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(3)

    # 검색 결과 iframe 진입
    driver.switch_to.frame("searchIframe")
    time.sleep(2)

    data_list = []

    while True:
        scroll_container = driver.find_element(By.ID, "_pcmap_list_scroll_container")

        # 현재 페이지 스크롤 다운
        for _ in range(scroll_count):
            driver.execute_script("arguments[0].scrollTop += 1000;", scroll_container)
            time.sleep(1.2)

        # 아이템 수집
        items = driver.find_elements(By.CSS_SELECTOR, "li.UEzoS.rTjJo")

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

        # 다음 페이지 버튼 찾기
        try:
            next_button = driver.find_element(
                By.XPATH,
                '//a[contains(@class, "eUTV2") and .//span[text()="다음페이지"] and @aria-disabled="false"]'
            )
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
        except:
            print("🔚 다음 페이지 없음 또는 이동 불가 → 종료")
            break


    driver.quit()

    df = pd.DataFrame(data_list)
    df.to_excel(excel_filename, index=False)
    print(f"✅ 저장 완료 - {excel_filename}")


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

    crawl_naver_map(url, fields, scroll_count=25, driver_path=driver_path, excel_filename="충주음식점.xlsx")