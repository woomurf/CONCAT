from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re 
import pandas as pd

driver = webdriver.Chrome('C:/Users/dngus/Desktop/CONCAT_INTERN/LinaCrawling/CONCAT/chromedriver_win32/chromedriver.exe')

def main() : 

    # 기본 설정 및 고객 정보 입력
    global driver 

    url = 'https://direct.samsunglife.com/dental.eds'
    driver.get(url)

    # 나이 입력
    # 가입 나이는 20 ~ 65세 입니다. 
    now_year = datetime.now().year 

    young = now_year - 20
    old   = now_year - 65

    contents = list()

    for age in range(young,old,5) : 
        
        client_age = str(age) + '0805'

        for sxCd in range(2) : 
            
            driver.get(url)

            driver.find_element_by_id('birthday').clear()
            driver.find_element_by_id('birthday').send_keys(client_age)
            
            # 0은 남자 1은 여자 
            genders = driver.find_element_by_id('proCalculatorArea1').find_element_by_class_name('label-check1').find_elements_by_tag_name('span')
            genders[sxCd].find_element_by_tag_name('label').click()

            # 보험료 계산하기 
            driver.find_element_by_id('calculate').click()
            wait.until(EC.invisibility_of_element((By.ID,"uiPOPLoading1")))

            contents += getContents(age,sxCd) 
    
    length = 0
    maxC = dict()

    for element in contents : 
        if len(element) > length : 
            length = len(element)
            maxC = element

    df = pd.DataFrame(contents, columns = maxC.keys())
    df.to_excel('Samsung_Dental.xlsx')
            


def getContents(age,sxCd) : 

    contents = list()
    
    global driver

    directCookie = driver.get_cookie('directJSESSIONID')['value']

    post_url = 'https://direct.samsunglife.com/dentalCalc.eds'

    post_header = {
        'Content-Type' : "application/x-www-form-urlencoded; charset=UTF-8",
        'X-Requested-With' : 'XMLHttpRequest',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        'Referer' : 'https://direct.samsunglife.com/dental.eds'
    }

    post_cookie = {
        'directJSESSIONID' : directCookie
    }
    # 임플란트 치료비는 50, 100, 150, 200 입니다. 

    options = driver.find_element_by_id('selImplant').find_elements_by_tag_name('option')
    implant_option = list()

    for option in options : 
        implant.append(option.get_attribute('value'))

    for impl in implant_option: 

        post_data = {
            "selImplStr":impl,
            "proType":"15",
            "prcdId":487,
            "prcd":"A053801ANNNAG01",
            "insCd":"LA0538001",
            "repCd":"LQ_GGG0L55L0000_G00",
            "prdtnm":"삼성생명 인터넷치아보험(재가입형,무배당)",
            "insrVcd":"001",
            "contName":"고객님",
            "contBirth":age,
            "contGender":sxCd+1,
            "insuPeriod":"10",
            "payPeriod":"10",
            "planType":"single",
            "planSubType":"2",
            "stats":"Y"
        }

        post_data = json.dumps(post_data)

        response = requests.post(post_url,headers = post_header, cookies = post_cookie, data = post_data.encode("utf-8"))

        guarantee = json.loads(response.text)

        standard = getGuaranteeList(guarantee,1,age,sxCd)
        contents.append(standard)

    type0_content = getGuaranteeList(guarantee,0,age,sxCd)
    type2_content = getGuaranteeList(guarantee,2,age,sxCd)

    contents.append(type0_content)
    contents.append(type2_content)

    return contents 

# 엑셀 구성 
# 생년월일 성별 유형 보장내역 보험금 


def getGuaranteeList(guarantee,code,age,sxCd) : 

    content = dict()

    content['생년월일'] = age
    content['성별'] = '남자' if sxCd == 0 else '여자'
    
    types = ['실속형','기본형','고급형']

    content['유형'] = types[code]

    for element in guarantee['arryData'][code]['guaranteeArry'] : 
        name  = element['name']
        price = element['amt']

        if name == "" : 
            continue

        price = int(re.findall(r'([0-9]+)만원',price)[0])

        if name not in content : 
            content[name] = price 
        else :
            content[name] += price 
    
    content['보험료'] = guarantee['arryData'][code]['inputObj']['premium']

    
    return content 


