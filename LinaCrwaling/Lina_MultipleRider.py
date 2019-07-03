from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time
import openpyxl
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def getRiderInfo(rider_index, rider_list_size,data_list):
    # data_list는 각 rider의 name과 option name을 넣을 리스트이다.

    global loc_number

    rider = rider_list[rider_index]
    rider_amount  = rider.find_element_by_name('rider_amount')
    rider_name    = rider.find_element_by_id('rider_name').get_attribute("value")
    rider_options = rider_amount.find_elements_by_tag_name('option')


    for rider_option in rider_options:

        rider_option.click()
        rider_option_name = rider_option.text
        if rider_option_name == '선택':
            rider_option_name = '없음'

        data_list[rider_index*2]   = rider_name
        data_list[rider_index*2 + 1] = rider_option_name

        if rider_index < rider_list_size-1 :
            getRiderInfo(rider_index+1, rider_list_size, data_list)

        else :
            for i in range(0,rider_list_size):
                rider_name_df = '특약' + str(i+1) + ' 이름'
                rider_cost_df = '특약' + str(i+1) + ' 금액'
                premium_df.loc[loc_number, [rider_name_df]] = data_list[i*2]
                premium_df.loc[loc_number, [rider_cost_df]] = data_list[i*2+1]

            wait.until(EC.invisibility_of_element((By.ID,'LOADING_BAR')))
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'g_btn_09.btnProductPremium'))).click()
            #calc_btn.click()
            #driver.find_element_by_class_name("g_btn_09.btnProductPremium").click()
            time.sleep(2)
            try :
                result = driver.find_element_by_id("prm_result").get_attribute("value")

            except :
                continue



            result = re.sub(r'[A-Z]+[0-9]+:','',result)


            regex   = re.compile(r'[0-9]+')
            premium = regex.findall(result)
            premium = list(map(int,premium))
            premium = sum(premium)

            premium_df.loc[loc_number,['성별']] = sex
            premium_df.loc[loc_number,['생년월일']] = age
            premium_df.loc[loc_number,['보험 기간']] = policy_option_name
            premium_df.loc[loc_number,['납입 기간']] = pay_option_name
            premium_df.loc[loc_number,['납입 주기']] = pm_option_name
            premium_df.loc[loc_number,['주 보험 금액']] = pa_option_name
            premium_df.loc[loc_number,['보험료']]    = premium
            loc_number += 1
            #성별','생년월일','보험 기간', '납입 기간', '납입 주기','주 보험 금액'


premium_df = pd.DataFrame(columns = ['성별','생년월일','보험 기간', '납입 기간', '납입 주기',
                                    '주 보험 금액'])

driver = webdriver.Chrome("C:\\Users\\dngus\\dev\\2019Summer\\CONCAT\\LinaCrwaling\\chromdriver_win32\\chromedriver.exe")

url = "https://www.lina.co.kr/disclosure/insr_price.htm"
driver.get(url)

page = driver.page_source
soup = BeautifulSoup(page, 'html.parser')


# 보험료 계산 페이지 접근하기
table = soup.select("#content > table:nth-child(30)") # 치아 보험들이 있는 div
links = table[0].find_all("a")

premium_names = table[0].find_all("td",class_= "bdl")
premium_name  = premium_names[0].get_text()

for i  in range(0,len(links)):
    links[i] = links[i].get('href')
    links[i] = links[i][1:]

# 보험료 계산하기
baseUrl = "https://www.lina.co.kr/product/simulation.htm?paramProductCode="
productUrl = baseUrl + links[1] # 특약이 여러 개 있는 보험!!!

driver.get(productUrl)

# 이름 넣기
driver.find_element_by_name('name').send_keys('홍길동')

wait = WebDriverWait(driver,20)

loc_number = 0

# 보험 가능 나이 계산하기
age_regex = re.compile(r'[0-9]+')
age_range = driver.find_element_by_class_name('tbl_txt_01').text
age_      = age_regex.findall(age_range)

old_age   = 2019 - int(age_[1]) # 가입 가능한 가장 늙은 나이
young_age = 2019 - int(age_[0]) # 가입 가능한 가장 어린 나이

# 특약 정보를 담은 테이블
rider_table = driver.find_element_by_id('riderInfo_div')
rider_list  = rider_table.find_elements_by_tag_name('tbody')[0].find_elements_by_tag_name('tr')
rider_list_size = len(rider_list)

for i in range(0,rider_list_size) :
    rider_name_df = '특약' + str(i+1) + ' 이름'
    rider_cost_df = '특약' + str(i+1) + ' 금액'

    premium_df[rider_name_df] = np.NaN
    premium_df[rider_cost_df] = np.NaN

premium_df['보험료'] = np.NaN

for age_i in range(0,100,5):

    if age_i % 10 == 0:
        print("age_i : ", age_i)
        time.sleep(2)

    driver.find_element_by_name('iresid_no1').clear()
    time.sleep(0.1)

    # 나이 선택하기

    age_year = old_age + age_i
    age_m_d  ='0625'
    age = str(age_year) + age_m_d

    if age_year > young_age :
        break


    driver.find_element_by_name('iresid_no1').send_keys(age)
    time.sleep(0.1)

    # 성별 선택하기
    for sex_i in range(2):
        sex = '남성'


        if sex_i == 1:
            # 여성 선택
            sex_radio_btn = wait.until(EC.element_to_be_clickable((By.ID,'leftinlabel1_woman')))
            sex_radio_btn.click()
            #driver.find_element_by_id('leftinlabel1_woman').click()
            sex = '여성'
        else :
            sex_radio_btn = wait.until(EC.element_to_be_clickable((By.ID,'leftinlabel1_man')))
            sex_radio_btn.click()
            #driver.find_element_by_id('leftinlabel1_man').click()
            sex = '남성'



        time.sleep(0.7)

        # 보험 기간 선택하기
        policy_period  = driver.find_element_by_id('policy_period')
        policy_options = policy_period.find_elements_by_tag_name('option')

        for policy_option in policy_options:
            if policy_option.text == '선택':
                continue

            policy_option.click()
            policy_option_name = policy_option.text
            time.sleep(0.1)


            # 납입 기간 선택하기
            pay_period  = driver.find_element_by_id('pay_period')
            pay_options = pay_period.find_elements_by_tag_name('option')

            for pay_option in pay_options:
                if pay_option.text == '선택':
                    continue

                pay_option.click()
                pay_option_name = pay_option.text
                time.sleep(0.1)


                # 납입 주기 선택하기
                premium_mode = driver.find_element_by_name('premium_mode')
                pm_options   = premium_mode.find_elements_by_tag_name('option')

                for pm_option in pm_options:
                    if pm_option.text == '선택':
                        continue

                    pm_option.click()
                    pm_option_name = pm_option.text
                    time.sleep(0.1)



                    # 주 보험 가입 금액 선택
                    product_amount = driver.find_element_by_name('product_amount')
                    pa_options     = product_amount.find_elements_by_tag_name('option')

                    for pa_option in pa_options:
                        if pa_option.text == '선택':
                            continue

                        pa_option.click()
                        pa_option_name = pa_option.text
                        time.sleep(0.1)


                        # 특약
                        data = [0] * (rider_list_size * 2)
                        getRiderInfo(0,rider_list_size,data)


writer = pd.ExcelWriter(premium_name + ".xlsx")
premium_df.to_excel(writer,'Sheet1')
writer.save()
