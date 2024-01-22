# install chromium, its driver, and selenium
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
import time
import pandas as pd
# options = uc.ChromeOptions()

df = pd.DataFrame(columns=['Ticker', 'Company Name', 'Market Cap', 'Current Price', 'Open', 'Volume', 'PE', 'EPS', 'BETA', 'EARNINGS DATE'])


stock_tickers = open('Tickers.csv', 'r')
tickers = stock_tickers.readlines()

count = 0
for ticker in tickers:
    try:
        count+= 1
        print("cool", count)
        # Create a new Chrome driver instance
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = uc.Chrome(options=options)
        driver.get("https://finance.yahoo.com/")
        # Wait for the search input element to be present and clickable.
        search = WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#yfin-usr-qry"))
            )
        WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#yfin-usr-qry"))
            )

            # Send the ticker to the search input element.
        search.send_keys(ticker)

            # Wait for the search button element to be present and clickable.
        button = WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#header-desktop-search-button"))
            )
        WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#header-desktop-search-button"))
            )
        # Click the search button element.
        button.submit()
        time.sleep(5)
        company = driver.find_element(By.CSS_SELECTOR, value='#quote-header-info > div.Mt\(15px\).D\(f\).Pos\(r\) > div.D\(ib\).Mt\(-5px\).Maw\(38\%\)--tab768.Maw\(38\%\).Mend\(10px\).Ov\(h\).smartphone_Maw\(85\%\).smartphone_Mend\(0px\) > div.D\(ib\) > h1').text
        market_cap = driver.find_element(By.CSS_SELECTOR, value='#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pstart\(12px\).Va\(t\).ie-7_D\(i\).ie-7_Pos\(a\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pstart\(0px\).smartphone_BdB.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(1) > td.Ta\(end\).Fw\(600\).Lh\(14px\)').text
        current_price = driver.find_element(By.CSS_SELECTOR, value='#quote-header-info > div.My\(6px\).Pos\(r\).smartphone_Mt\(6px\).W\(100\%\) > div.D\(ib\).Va\(m\).Maw\(65\%\).Ov\(h\) > div.D\(ib\).Mend\(20px\) > fin-streamer.Fw\(b\).Fz\(36px\).Mb\(-4px\).D\(ib\)').text
        open = driver.find_element(By.CSS_SELECTOR, value='#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pend\(12px\).Va\(t\).ie-7_D\(i\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pend\(0px\).smartphone_BdY.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(2)').text
        volume = driver.find_element(By.CSS_SELECTOR, value='#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pend\(12px\).Va\(t\).ie-7_D\(i\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pend\(0px\).smartphone_BdY.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(7) > td.Ta\(end\).Fw\(600\).Lh\(14px\)').text
        beta = driver.find_element(By.CSS_SELECTOR, value='#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pstart\(12px\).Va\(t\).ie-7_D\(i\).ie-7_Pos\(a\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pstart\(0px\).smartphone_BdB.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(2) > td.Ta\(end\).Fw\(600\).Lh\(14px\)').text
        pe = driver.find_element(By.CSS_SELECTOR, value='#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pstart\(12px\).Va\(t\).ie-7_D\(i\).ie-7_Pos\(a\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pstart\(0px\).smartphone_BdB.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(3) > td.Ta\(end\).Fw\(600\).Lh\(14px\)').text
        eps = driver.find_element(By.CSS_SELECTOR, value='#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pstart\(12px\).Va\(t\).ie-7_D\(i\).ie-7_Pos\(a\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pstart\(0px\).smartphone_BdB.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(4) > td.Ta\(end\).Fw\(600\).Lh\(14px\)').text
        earnings_date = driver.find_element(By.CSS_SELECTOR, value = '#quote-summary > div.D\(ib\).W\(1\/2\).Bxz\(bb\).Pstart\(12px\).Va\(t\).ie-7_D\(i\).ie-7_Pos\(a\).smartphone_D\(b\).smartphone_W\(100\%\).smartphone_Pstart\(0px\).smartphone_BdB.smartphone_Bdc\(\$seperatorColor\) > table > tbody > tr:nth-child(5) > td.Ta\(end\).Fw\(600\).Lh\(14px\)').text
        df = pd.concat([df, pd.DataFrame([[ticker, company, market_cap, current_price, open, volume, beta, pe, eps, earnings_date]], columns=df.columns)], ignore_index=True)
        driver.close()
        time.sleep(1)
    except:
        pass

df.to_csv('today_Stock_market_snapshot.csv')
time.sleep(1)
# # Verify that the keys were sent successfully
# assert search_box.get_attribute('value') == 'Boston'