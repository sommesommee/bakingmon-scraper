import csv
import time
import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

# 셀레니움 드라이버를 초기화, 원격 제어할 브라우저 오픈
op = webdriver.ChromeOptions()
chrome_service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=chrome_service, options=op)

baseurl="https://cafe.naver.com/bakingmon"

clubid=30214192     # 베이킹몬 네이버 카페
menuid=15           # 베이킹 일지 게시판
pageNum=1           # 페이지 위치
boardtype="L"       # 게시판   타입 (리스트)
userDisplay=50      # 게시물 노출 수량

driver.get(baseurl
           + '/ArticleList.nhn?search.clubid=' + str(clubid)
           + '&search.menuid=' + str(menuid)
           + '&search.boardtype=' + str(boardtype)
           + '&search.page=' + str(pageNum)
           + '&userDisplay=' + str(userDisplay)
           )

time.sleep(3)

# cafe_main 아이디를 가진 iframe 요소 찾은 후 iframe으로 전환
cafe_main_frame = driver.find_element(By.CSS_SELECTOR, '#cafe_main')
driver.switch_to.frame(cafe_main_frame)


# BeautifulSoup을 사용 HTML 파싱
soup = bs(driver.page_source, 'html.parser')
# article-board 클래스를 가진 div 태그 찾기
article_board_div = soup.find('div', class_='article-board', id=lambda x: x != 'upperArticleList')
# article-board의 tbody 태그 내부의 td 태그들 찾기
tr_elements = article_board_div.select('table > tbody > tr')

# 딕셔너리 리스트
dataList = []
for tr in tr_elements:

    title = tr.select_one(".td_article > .board-list > .inner_list > .article")
    #하위 tr 태그 제외 처리
    if not title:
        continue
    dataDict = {
        "inner_number" : int(tr.select_one(".td_article > .board-number > .inner_number").text),
        "title" : title.text.strip(),
        "nick" : tr.select_one(".td_name > .pers_nick_area > table > tbody > tr > .p-nick > .m-tcol-c").text,
        "regDate" : tr.select_one(".td_date").text,
        "viewCount" : tr.select_one(".td_view").text,
        "likeCount" : tr.select_one(".td_likes").text,
        "href" : title.get('href')
    }
    dataList.append(dataDict)

# 현재 위치한 iframe에서 나가기 (상위로 이동)
driver.switch_to.default_content()

time.sleep(3)

# 딕셔너리 리스트 -> .json 저장
with open('temp/dataList.json', 'w', encoding='utf-8') as json_file:
    json.dump(dataList, json_file, ensure_ascii=False, indent=2)






# dataList.json 파일 상세 페이지 순환
with open('temp/dataList.json', 'r', encoding='utf-8') as json_file:
    loaded_dataList = json.load(json_file)

for data in loaded_dataList:
    href_value = data.get('href', None)

    # 각 리스트의 페이지 이동
    driver.get(baseurl + href_value)

    # 찾은 iframe으로 전환
    desc_cafe_main_frame = driver.find_element(By.CSS_SELECTOR, '#cafe_main')
    driver.switch_to.frame(desc_cafe_main_frame)

    descSoup = bs(driver.page_source, 'html.parser')
    descTag = descSoup.find('div', class_='se-main-container')


    # image 저장
    image_list = descTag.select('.se-component.se-image .se-section-image .se-module-image a img')

    for index, image in enumerate(image_list):
        image_url = image['src']
        response = requests.get(image_url, stream=True)

        image_filename = f"{data.get('inner_number')}_{index + 1}.jpg"
        image_filepath = os.path.join(os.path.expanduser("temp/images"), image_filename)
        with open(image_filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)

    # 이미지 경로 변경(CDN -> LOCAL)
    for index, img_tag in enumerate(image_list, start=1):
        img_tag['src'] = f'images/{data.get("inner_number")}_{index}.jpg' #새로운 파일명으로 변경

    filename = f"{data.get('inner_number')}.html"
    filename = os.path.join(os.path.expanduser("temp"), filename)

    # html 저장
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(str(descTag))






"""
# 로그인, PW 2차인증과정이 강제발생 하는 이슈가 있어 개선 필요
my_id = ""
my_pw = ""
driver.get("https://nid.naver.com/nidlogin.login")

time.sleep(3)

try:
    id_input = driver.find_element(By.CSS_SELECTOR, '#id')
    ActionChains(driver).move_to_element(id_input).click().send_keys(my_id).perform()
    time.sleep(1)
    pw_input = driver.find_element(By.CSS_SELECTOR, '#pw')
    ActionChains(driver).move_to_element(pw_input).click().send_keys(my_pw).perform()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="log.login"]').click()
    time.sleep(1)
except:
    print("Exception occurred")
"""