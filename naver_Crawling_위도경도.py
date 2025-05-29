from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import requests

def get_coordinates_to_excel(query, search_coord):
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
        rows.append({'x좌표': x, 'y좌표': y})
    return rows

def crawl_naver_map(url, fields, scroll_count=7, driver_path=None, excel_filename="output.xlsx"):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(3)

    # 검색 결과 iframe 진입
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
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

            # 기본 정보 추출
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

            # ✅ 주소 수집
            try:
                # 자세히 보기 클릭
                detail_button = item.find_element(By.CSS_SELECTOR, "a.place_bluelink.N_KDL.CtW3e")
                driver.execute_script("arguments[0].click();", detail_button)
                time.sleep(1)

                # entryIframe 전환
                driver.switch_to.default_content()
                WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe")))
                time.sleep(0.5)

                # 주소 추출
                address_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.LDgIH"))
                )
                address = address_element.text.strip()
                if data["이름"] != None:
                    time.sleep(0.5)
                    lalo = get_coordinates_to_excel(data["이름"], search_coord)
                    latitude, longitude = lalo[0]['x좌표'], lalo[0]['y좌표']
                    data["위도"], data["경도"] = latitude, longitude

                print(address)
            except Exception as e:
                address = f"주소 오류: {str(e)}"

            # 다시 검색 프레임으로 전환
            driver.switch_to.default_content()
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
            time.sleep(0.5)

            data["주소"] = address
            data_list.append(data)

        # 다음 페이지 버튼 클릭 시도
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
    driver_path = "C:\\Users\\User\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
    url = "https://map.naver.com/p/search/충주음식점"

    search_coord = "127.93883339999621;36.96102790000016"

    fields = {
        "이름": ("span.TYaxT", "css"),
        "카테고리": ("span.KCMnt", "css"),
        "설명": ("a.nyHXH", "css"),
        "별점": ("span.orXYY", "css"),
        "리뷰 수": (".//span[contains(text(), '리뷰')]", "xpath")
    }

    crawl_naver_map(url, fields, scroll_count=25, driver_path=driver_path, excel_filename="충주음식점_네이버_위도경도.xlsx")