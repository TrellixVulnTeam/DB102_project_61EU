from selenium import webdriver
import time
import pandas as pd  # 要改名的原因不可考
from selenium.webdriver.support.select import Select
import read_stock50 as stock50
from sqlalchemy import create_engine

col = ["id", "t_date", "code", "name", "p_open", "p_high", "p_low", "p_close", "volume"]
df = pd.DataFrame(columns=col)
code_list = stock50.code_list()
stock_list = stock50.stock_list()
code_len = len(code_list)
engine = create_engine(
    "mysql+pymysql://{user}:{pw}@{localhost}:{port}/{db}".format(user="db102stock", pw="db102stock_pwd",
                                                                 localhost="10.120.14.28", port=3306, db="stock"))

for i in range(code_len):
    try:
        url = "https://www.cnyes.com/twstock/ps_historyprice/" + str(code_list[i]) + ".htm"
        option = webdriver.ChromeOptions()
        option.add_argument("headless")
        driver = webdriver.Chrome(chrome_options=option)
        driver.get(url)
        # '''
        # 處理開始日期
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_startText").clear()
        time.sleep(7)
        select_year = Select(driver.find_element_by_class_name('datepicker_newYear'))
        select_year.select_by_visible_text(u"2011")  # 指向指定年分
        time.sleep(6)
        select_month = Select(driver.find_element_by_class_name('datepicker_newMonth'))
        select_month.select_by_visible_text(u"January")   # 指向指定月份
        time.sleep(6)
        driver.find_element_by_link_text("1").click()  # 指向指定日期
        time.sleep(3)
        # 處理結束日期
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_endText").clear()
        time.sleep(7)
        select_year = Select(driver.find_element_by_class_name('datepicker_newYear'))
        select_year.select_by_visible_text(u"2014")  # 指向指定年分
        time.sleep(6)
        select_month = Select(driver.find_element_by_class_name('datepicker_newMonth'))
        select_month.select_by_visible_text(u"January")   # 指向指定月份
        time.sleep(6)
        driver.find_element_by_link_text("1").click()  # 指向指定日期
        time.sleep(3)
        # 執行查詢
        driver.find_element_by_id("ctl00_ContentPlaceHolder1_submitBut").click()
        time.sleep(7)
        # '''
        table_data = driver.find_element_by_class_name("tab")
        table_tr = table_data.find_elements_by_tag_name("tr")
        table_tr.pop(0)

        # 表的內容
        for tr in table_tr:
            # 將表的每一行的每一列內容存在table_td_list中，從第1列開始
            table_td = tr.text
            table_td_list = table_td.split(" ")
            # 排掉不要的欄位
            table_td_list.pop(5)
            table_td_list.pop(5)
            table_td_list.pop()
            table_td_list.pop()
            # 設計id的格式
            td_year = str(table_td_list[0][:4])
            td_month = str(table_td_list[0][5:7])
            td_day = str(table_td_list[0][8:])
            td_id = code_list[i] + td_year + td_month + td_day
            # 把數字欄位的逗號去掉，否則會無法匯入DB(資料型態不對)
            for j in range(6):
                table_td_list[j] = table_td_list[j].replace(",", "")

            data = [td_id, table_td_list[0], code_list[i], stock_list[i], table_td_list[1], table_td_list[2], table_td_list[3], table_td_list[4], table_td_list[5]]
            s = pd.Series(data, index=col)
            df = df.append(s, ignore_index=True)
        # print(df)

    finally:
        driver.close()

# 儲存表格至csv & MySQL
df.to_sql(con=engine, name='stock_inf', if_exists='append', index=False)
df.to_csv("lack_stock_2014.csv", encoding="Big5", index=False)  # Big5不會變亂碼 LOL
