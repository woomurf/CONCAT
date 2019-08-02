from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import openpyxl
import pandas as pd 
from datetime import datetime
import re
import time

def getContent(page,content) : 

    soup = BeautifulSoup(page,'html.parser')

    result = soup.find(id = 'direcEntplDiv')

    # 보장 내역 and 보험료
    guaranteeList = result.find(id = "entplFinDiv").find(class_='box_area')
    premium = result.find(id = "entplFinDiv").find(class_='box2_area')

    # 원하지 않는 요소들을 제외시켜줍니다.
    not_wants = guaranteeList.find_all(class_='stnrdPrdtList')
    for nots in not_wants : 
        nots.extract()
    
    # 보장 내역을 뽑아와 이름과 내역을 매칭시켜줍니다. 
    gt_list = guaranteeList.find_all(class_='insurance_info_dental')

    for gt in gt_list : 
        title = gt.find('strong')
        price = gt.find('span')

        if title == None :
            continue
        
        title = title.get_text()
        price = price.get_text()
        content[title] = price
    
    premium_price = premium.find(id = "vwMnContPrm00").get_text()

    content['보험료'] = premium_price

    return content

def main() : 
    driver = webdriver.Chrome('C:/Users/concat/Desktop/LinaCrawling/CONCAT/chromedriver_win32/chromedriver.exe')
    url = 'https://online.abllife.co.kr/insurance-product/health-coverage/dental.abl?utm_campaign=dental&utm_source=insmarket-p&utm_medium=referral&utm_content=ebiz&utm_term=main_dental'

    driver.get(url)

    driver.set_window_size(1920,1028)

    # 가입 연령은 만 19세부터 만 70세까지입니다.
    young = 20
    old   = 70 

    year = datetime.now().year

    young = int(str(year - young) + '0728')
    old   = int(str(year - old)   + '0728')

    wait = WebDriverWait(driver,20)

    contents = list()

    for age in range(old,young,50000) : 
        driver.find_element_by_id('brthDay').clear()
        driver.find_element_by_id('brthDay').send_keys(age)

        # 성별 선택
        for i in range(2) : 
            if i == 0 : 
                driver.find_element_by_class_name('man').click()
                sex = '남자'
            else : 
                driver.find_element_by_class_name('woman').click()
                sex = '여자'

            # 보험료 계산하기
            driver.find_element_by_id('calcStrBtn').click()

            wait.until(EC.invisibility_of_element((By.ID,'globalLoadingDiv')))
            time.sleep(1)
            
            # 보험 기간 선택하기
            period = driver.find_element_by_id("mnInsrPrdYys00Div")
            period_options = period.find_elements_by_tag_name('option')
            
            try : 
                driver.find_element_by_id("direcEntplTab").click()
            except :
                pass 

            for option in period_options :
                option.click()
                time.sleep(2)
                
                content = dict()
                content['생년월일'] = age
                content['성별'] = sex 
                content['주계약 보험금액'] = '500만원'
                content['보험 기간'] = option.text
                content['납입 기간'] = option.text

                page = driver.page_source

                content = getContent(page,content)
                contents.append(content)

    df = pd.DataFrame(contents, columns = contents[0].keys())
    df.to_excel("ABL.xlsx")

if __name__ == "main" : 
    main()
    

                
