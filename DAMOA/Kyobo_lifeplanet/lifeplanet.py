from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import openpyxl
import re
import pandas as pd 
from bs4 import BeautifulSoup
import time
from datetime import datetime 

driver = webdriver.Chrome('C:/Users/concat/Desktop/LinaCrawling/CONCAT/chromedriver_win32/chromedriver.exe')
wait = WebDriverWait(driver,20)



def main() : 
    global driver 
    
    url = 'https://www.lifeplanet.co.kr/products/pe/HPPE800S1.dev'
    driver.get(url)

    now_year = datetime.now().year 

    # 나이는 만 19세 ~ 50세 (20년 만기의 경우 45세까지)
    young = 19
    old   = 50

    today = int(str(now_year) + '0803')

    contents = list()

    for age in range(young,old+1,5) : 
        
        for sxCd in range(2) : 

            for insCd in range(2) : 

                if age > 45 : 
                    continue
                
                input_age = str(now_year-age)[2:] + '0505'

                inputClient(input_age,sxCd)
                time.sleep(3)
                content = getContents(insCd,input_age,sxCd)
                contents += content

    df = pd.DataFrame(contents, columns = contents[0].keys())
    df.to_excel('lifePlanet.xlsx')


def inputClient(age,sxCd) :
    global driver 
    global wait
    
    inputbox = driver.find_element_by_class_name('list_calc')

    inputbox.find_element_by_name('plnnrBrdt').clear()
    inputbox.find_element_by_name('plnnrBrdt').send_keys(age)

    sexes = inputbox.find_elements_by_class_name('rdo_m')
    sexes[sxCd].find_element_by_tag_name('label').click()

    driver.find_element_by_id('fastPayCalc').click()
    wait.until(EC.invisibility_of_element((By.ID,"loadingWrap")))

def getContents(insCd,age,sxCd) :

    global driver
    global wait

    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
    time.sleep(1)
    # 치료보험금 선택 10만원 or 20만원
    driver.find_element_by_class_name('box_sel').click()
    time.sleep(1)
    insure_ = driver.find_element_by_class_name('_sel_option').find_elements_by_tag_name('li')
    insure_[insCd].click()

    wait.until(EC.invisibility_of_element((By.ID,"loadingWrap")))

    page = driver.page_source 
    soup = BeautifulSoup(page,'html.parser')
    cvrList = soup.find(class_= 'box_info').find_all('li')

    # 치료 보장 내역
    insure_dict = dict() 


    for cvr in cvrList :

        # 자세한 설명은 제외한다.
        not_want = cvr.find(class_='box_tooltip')
        not_want.extract()
        
        title  = cvr.find(class_='tooltip_include').get_text()
        insure = cvr.find('strong').get_text() 

        title = title.replace('\t','')
        title = title.replace('\n','')

        insure_dict[title] = insure


    period_box = driver.find_element_by_class_name('section_plan_info').find_element_by_class_name('box_rdo')
    period_options = period_box.find_elements_by_class_name("rdo_m")
    
    contents = list()

    # 보험기간, 납부기간 선택 
    for index, per_option in enumerate(period_options) : 
        
        per_option = per_option.find_element_by_tag_name('label')
        per_option.click()
        wait.until(EC.invisibility_of_element((By.ID,"loadingWrap")))
        period = per_option.text

        payments = driver.find_element_by_id('insuTermContents').find_elements_by_tag_name('label')

        for pay_index in range(index + 1) :
            
            payment = payments[pay_index]
            payment.click()
            wait.until(EC.invisibility_of_element((By.ID,"loadingWrap")))
            pay_option = payment.text

            driver.find_element_by_id("btnExpectInsuPay").click()

            # 보험료
            prm = driver.find_element_by_class_name('section_premium').find_element_by_class_name('area_r').find_element_by_class_name('txt_2').text
            time.sleep(2)

            content = dict()

            content['생년월일'] = age
            content['성별'] = '남자' if sxCd == 0 else '여자'
            content['보험기간'] = period
            content['납입기간'] = pay_option
            
            content.update(insure_dict)
            content['보험료'] = prm 
            contents.append(content)
    
    return contents




            