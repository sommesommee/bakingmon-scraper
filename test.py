import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.action_chains import ActionChains

import pyperclip
import re

# 셀레니움 드라이버를 초기화, 원격 제어할 브라우저 오픈
op = webdriver.ChromeOptions()
chrome_service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=chrome_service, options=op)

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

baseurl="https://cafe.naver.com/bakingmon"
pageNum=1
clubid=30214192 #베이킹몬 네이버 카페
menuid=15 #베이킹 일지 게시판
boardtype="L"
userDisplay=50

#아래 url의 get파라미터인 page값에 따라 페이지 이동 가능
#https://cafe.naver.com/bakingmon/ArticleList.nhn?search.clubid=30214192&search.menuid=15&search.boardtype=I&search.page=12
#태그 article-album-sub 의 하위에 있는 <li> 의 <a> 에 있는 articleid 값을 수집하면 모든 게시물의 articleid 접근이 가능하게 됨...
#그 페이지의 모든 아티클아이디를 확보한 후...별도 별도 페이지로 띄운 후 카피를 진행...???
#https://cafe.naver.com/bakingmon?iframe_url=/ArticleList.nhn&search.clubid=30214192&search.menuid=15&search.boardtype=I

driver.get(baseurl
           + '/ArticleList.nhn?search.clubid=' + str(clubid)
           + '&search.menuid=' + str(menuid)
           + '&search.boardtype=' + str(boardtype)
           + '&search.page=' + str(pageNum)
           + '&userDisplay=' + str(userDisplay)

           )

time.sleep(3)

# cafe_main 아이디를 가진 iframe 요소 찾기
cafe_main_frame = driver.find_element(By.CSS_SELECTOR, '#cafe_main')

# 찾은 iframe으로 전환
driver.switch_to.frame(cafe_main_frame)

# 페이지가 로드된 후 페이지 소스를 가져옴
# BeautifulSoup을 사용하여 HTML 파싱
soup = bs(driver.page_source, 'html.parser')
# article-board 클래스를 가진 div 태그 찾기
article_board_div = soup.find('div', class_='article-board', id=lambda x: x != 'upperArticleList')
# article-board의 tbody 태그 내부의 td 태그들 찾기
tr_elements = article_board_div.select('table > tbody > tr')

dataList = []


for tr in tr_elements:

    title = tr.select_one(".td_article > .board-list > .inner_list > .article")
    #하위 tr 태그 제외 처리
    if not title:
        continue
    #print(title.text.strip())

    inner_number = tr.select_one(".td_article > .board-number > .inner_number")
    #print(int(inner_number.text))
    href = title.get('href')
    #print(href)

    nick = tr.select_one(".td_name > .pers_nick_area > table > tbody > tr > .p-nick > .m-tcol-c")
    #print(nick.text)

    regDate = tr.select_one(".td_date")
    #print(regDate.text)

    viewCount = tr.select_one(".td_view")
    #print(int(viewCount.text))

    likeCount = tr.select_one(".td_likes")
    #print(int(likeCount.text))

    dataTuple = (int(inner_number.text), title.text.strip(), nick.text, regDate.text, int(viewCount.text), int(likeCount.text), href)
    dataList.append(dataTuple)

print('dataList')
print(dataList)

# 현재 위치한 iframe에서 나가기 (상위로 이동)
driver.switch_to.default_content()

driver.get(baseurl + dataList[0][-1])

time.sleep(3)

# 찾은 iframe으로 전환
desc_cafe_main_frame = driver.find_element(By.CSS_SELECTOR, '#cafe_main')
driver.switch_to.frame(desc_cafe_main_frame)

descSoup = bs(driver.page_source, 'html.parser')
descTag = descSoup.find('div', class_='se-main-container')

print('DESC')
print(descTag)
