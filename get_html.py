import re
from selenium import webdriver as wd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# отправляем запрос с заголовками по нужному адресу
#driver_path =r"C:\Users\Евгения\Python\test_MillionAgents\chromedriver.exe"

driver = wd.Chrome()
general_link= r"https://online.metro-cc.ru"
driver.get(general_link)
data = {
    'id товара из сайта/приложения': [],
    'наименование': [],
    'ссылка на товар': [],
    'регулярная цена': [],
    'промо цена': [],
    'бренд': []
}

def prepare_driver(category):
   search_box = driver.find_element(By.CSS_SELECTOR,'input[type="text"]')
   search_box.send_keys(category) 

   button = driver.find_element(By.XPATH,'//button[@data-qa="header-search-button-submit"]')

   driver.execute_script("arguments[0].scrollIntoView(true);", button)

   driver.execute_script("arguments[0].click();", button)
   time.sleep(4)
   checkbox = driver.find_element(By.XPATH,'//input[@type="checkbox"]')

   driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)

   driver.execute_script("arguments[0].click();", checkbox)
   time.sleep(3)
class Data:
   def __init__(self) -> None:
      self.df = pd.DataFrame(data)
   def put_data(self, id, name, href, pr_1,pr_2, brend):

      self.df.loc[len(self.df.index)] = [id, name, href, pr_1, pr_2, brend]
   
   def save_csv(self, name):
      self.df.to_excel(f'{name}.xlsx', index=False)

def get_data(driver, data):
   soup = BeautifulSoup(driver.page_source, "html.parser")
   all_publications = soup.find(id="products-inner")
# форматируем результат
   for article in all_publications:
      product_card_text = article.find("a", class_="product-card-photo__link reset-link")
      title= product_card_text.get('title')
      link = general_link+product_card_text.get('href')
      product_card_text = article.find_all('span', class_='product-price__sum-rubles')
      
      en_price=None
      if len(product_card_text)==2:
         regular_price=product_card_text[1].get_text()
         en_price=product_card_text[0].get_text()
         en_price.replace(" ", "")
      else:
         regular_price=product_card_text[0].get_text()
      pattern = re.compile(r'[a-zA-Z].*?\s')
      result = re.search(pattern, title)
      print(title)
      brend=None
      if result:
         brend = result.group(0).strip()
      else:
         new=title.split(" ")
         brend=new[1]+" "+new[2]
      id = int(article["data-sku"])
      data.put_data(id, title,link, regular_price, en_price, brend)
      print(id, title,link, regular_price.replace(" ", ""), en_price, brend )
      
      
def get_new_page(driver):
   elements = driver.find_elements(By.CSS_SELECTOR,'li[data-v-2505d9ee]')
   last_element=elements[-1]
   link = last_element.find_element(By.TAG_NAME, 'a').get_attribute('href')
   driver.get(link)
time.sleep(3)
prepare_driver("Кофе")
data= Data()
time.sleep(3)
get_data(driver, data)
while(len(data.df)<500):
   
   get_new_page(driver)
   get_data(driver, data)
data.save_csv("data_metro")


