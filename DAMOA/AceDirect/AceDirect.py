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

def main() :

    driver = webdriver.Chrome('C:/Users/concat/Desktop/LinaCrawling/CONCAT/chromedriver_win32/chromedriver.exe')
    url = 'https://www.acedirect.co.kr/servlets/contract/contractForward.ace?target=pc/contract/step01Dental&cmd=Step01Command&layout=type2'
    driver.get(url)

    driver.set_window_size(1920,1028)

    page0 = driver.page_source
    soup  = BeautifulSoup(page0,'html.parser')

    # 보험가입 가능한 나이 범위 구하기 
    year = datetime.now().year
    age_range = soup.find(class_='bullet1').find_all('li')[1].get_text()
    age_range = re.findall(r'[0-9]+',age_range)

    young = int(str(int(year) - int(age_range[0])) + '0726')
    old   = int(str(int(year) - int(age_range[1])) + '0726')


    wait = WebDriverWait(driver,20)
    
    contents = list()
    
    # 나이에 따라 반복합니다
    for age in range(old,young,50000) : 
        
        # yymmdd
        age = str(age)[2:]
        
        # 성별에 따라 반복합니다. 
        for sex_i in range(2) :

            # 보험 납부 기간 유형에 따라 반복합니다.
            for option_i in range(1,3) : 
                
                driver.get(url)

                sexes = driver.find_elements_by_class_name('radio_type4')
                
                driver.find_element_by_name('insuredBirth').clear()
                driver.find_element_by_name('insuredBirth').send_keys(age)   

                if sex_i == 0 :
                    sexes[0].find_element_by_tag_name('span').click()
                    sex = '남자'
                else :
                    sexes[1].find_element_by_tag_name('span').click()
                    sex = '여자'

                period  = driver.find_element_by_name('periodPayFrequency')
                options = driver.find_elements_by_tag_name('option')

                option = options[option_i]
                option.click()
                period_option = option.text

                # 순수보장형 선택
                driver.find_element_by_class_name('radio_type2').find_element_by_tag_name('span').click()


                driver.find_element_by_id('btnNext').click()
                time.sleep(5)

                page = driver.page_source

                content = getContents(page,age,sex,period_option)
                contents += content
                
    # 가장 요소가 많은 녀석을 찾아서 
    length = 0
    maxC = list()
    for content in contents : 
        if length < len(content) : 
            length = len(content)
            maxC = content

    df = pd.DataFrame(contents, columns = maxC.keys())
    df.to_excel('AceDirect.xlsx')
                

'''
회원 정보 입력하는 페이지
--------------------
보험료 및 보장내역 나오는 페이지 -> 이 부분을 함수화해서 돌리는 것이 낫겠다.
'''



def getContents(page,age,sex,option_name) :
    
    soup = BeautifulSoup(page,'html.parser')

    result_table = soup.find(id = 'resultTable')

    head = result_table.find('thead')
    body = result_table.find('tbody')

    # 실속형, 기본형, (고급형) 정보를 담을 리스트
    plan_list = head.find_all(class_= 'radio_type3')
    # 자유선택형은 제외
    plan_list.pop()

    names = list()
    prices = list()
    
    for plan in plan_list : 
        tmp = re.findall(r'[가-힣]+|[0-9]+,[0-9]+',plan.text)
            
        names.append(tmp[0])
        prices.append(tmp[1])

    # 보장 내역 리스트
    gu_list = body.find_all('tr')

    # 실속,기본,(고급) 에 따라 보장 금액을 담을 리스트
    plan_premium = list()
    for i in range(len(plan_list)) :
        plan_premium.append([])

    for index, element in enumerate(plan_premium) : 
        element.append(age)
        element.append(sex)
        element.append(option_name)
        element.append(names[index])
    
    title = ['생년월일','성별','납부 유형','보험 유형']
    
    
    # 각 list에 내역 넣기
    # title에는 보장 내역 이름이 
    # 각 plan에는 유형에 맞는 보장 내역이 들어갑니다. 
    for gu in gu_list : 
        gu = gu.find_all('td')[:4]
        title.append(gu[0].get_text().replace('\t','').replace('\n','').replace('(치아당 보상)','').replace('(촬영당 보상)',''))
        
        for index, element in enumerate(plan_premium) : 
            element.append(gu[index+1].get_text().replace('\t','').replace('\n',''))
    
    title.append('보험료')
    
    for index, element in enumerate(plan_premium) : 
        element.append(prices[index])
    
    contents = list()
    
    for plan in plan_premium : 
        
        content = dict()
        for index,name in enumerate(title) : 
            content[name] = plan[index]
        
        contents.append(content)
    
    return contents 



if __name__ == "__main__" : 
    main()

