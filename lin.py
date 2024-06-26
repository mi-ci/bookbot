from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://nid.naver.com/nidlogin.login?svctype=262144&url=https%3A%2F%2Ffin.land.naver.com%2Fcomplexes%2F139%3Ftab%3Dstory")
c=WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="id"]'))
)
c.send_keys('gameboyking')
c=WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="pw"]'))
)
c.send_keys('wwwliberta'+ Keys.ENTER)
time.sleep(5)
n = 139
while n < 10011 :
    driver.get(f"https://fin.land.naver.com/complexes/{n}?tab=story")
    c=WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="complexes-story"]/div/div[3]/div[1]/form/fieldset/div/div[1]/div[2]/div/label'))
    )
    c.click()
    c=WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="complexes-story__write_textarea"]'))
    )
    c.send_keys('ㅎㅇ')
    c=WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="complexes-story"]/div/div[3]/div[1]/form/fieldset/div/div[1]/div[6]/button/span[2]'))
    )
    c.click()
    time.sleep(1)
    try:
        alert = driver.switch_to.alert
        alert.accept()
        time.sleep(20)
    except:
        pass
        print(f'{n} - complete')
        n=n+1

print('end')
time.sleep(20)
