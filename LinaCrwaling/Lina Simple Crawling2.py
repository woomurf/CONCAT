from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import time

premium_df = pd.DataFrame(columns = ['성별','생년월일','보험 기간', '납입 기간', '납입 주기',
                                    '주 보험 금액', '특약 이름', '특약 금액'])

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
productUrl = baseUrl + links[0]

driver.get(productUrl)

# 이름 넣기
driver.find_element_by_name('name').send_keys('홍길동')

for age_i in range(0,30):
    # 나이 선택하기
    age_year = 1970 + i
    age_m_d  ='0625'
    age = str(age_year) + age_m_d

    driver.find_element_by_name('iresid_no1').send_keys(age)

    # 성별 선택하기
    for sex_i in range(2):
        sex = '남성'

        if i == 1:
            # 여성 선택
            driver.find_element_by_id('leftinlabel1_woman').click()
            sex = '여성'
        else :
            driver.find_element_by_id('leftinlabel1_man').click()
            sex = '남성'


        # 보험 기간 선택하기
        policy_period  = driver.find_element_by_id('policy_period')
        policy_options = policy_period.find_elements_by_tag_name('option')

        for policy_option in policy_options:
            if policy_option.text == '선택':
                continue

            policy_option.click()
            policy_option_name = policy_option.text


            # 납입 기간 선택하기
            pay_period  = driver.find_element_by_id('pay_period')
            pay_options = pay_period.find_elements_by_tag_name('option')

            for pay_option in pay_options:
                if pay_option.text == '선택':
                    continue

                pay_option.click()
                pay_option_name = pay_option.text


                # 납입 주기 선택하기
                premium_mode = driver.find_element_by_name('premium_mode')
                pm_options   = premium_mode.find_elements_by_tag_name('option')

                for pm_option in pm_options:
                    if pm_option.text == '선택':
                        continue

                    pm_option.click()
                    pm_option_name = pm_option.text



                    # 주 보험 가입 금액 선택
                    product_amount = driver.find_element_by_name('product_amount')
                    pa_options     = product_amount.find_elements_by_tag_name('option')

                    for pa_option in pa_options:
                        if pa_option.text == '선택':
                            continue

                        pa_option.click()
                        pa_option_name = pa_option.text


                        # 특약

                        # 특약 정보를 담은 테이블
                        rider_table = driver.find_element_by_id('riderInfo_div')
                        rider_list  = rider_table.find_elements_by_tag_name('tbody')[0].find_elements_by_tag_name('tr')

                        for rider in rider_list:
                            rider_amount  = rider.find_element_by_name('rider_amount')
                            rider_options = rider_amount.find_elements_by_tag_name('option')
                            rider_name    = rider.find_element_by_id('rider_name').get_attribute("value")

                            for rider_option in rider_options:
                                if rider_option.text == '선택':
                                    continue

                                rider_option.click()
                                rider_option_name = rider_option.text


                                # 보험료 조회하기

                                driver.find_element_by_class_name("g_btn_09.btnProductPremium").click()

                                result = driver.find_element_by_id("prm_result").get_attribute("value")
                                print(result)

                                result = re.sub(r'[A-Z]+[0-9]+:','',result)
                                print("result : ", result)

                                regex   = re.compile(r'[0-9]+')
                                premium = regex.findall(result)
                                print(premium)
                                premium = int(premium[0]) + int(premium[1])

                                premium_df.loc[sex_i] = [sex, age, policy_option_name,pay_option_name, pm_option_name, pa_option_name,
                                                         rider_name, rider_option_name]

writer = pd.ExcelWriter(premium_name + ".xlsx")
premium_df.to_excel(writer,'Sheet1')
writer.save()
