import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import pandas as pd

async def scrape_ofac_data():
    """Scrapes OFAC data for all countries and saves it to a CSV file."""

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.maximize_window()
        driver.get('https://sanctionssearch.ofac.treas.gov/')
 
        wait = WebDriverWait(driver, 10)

        country_dropdown = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_ddlCountry')))

        ofac_data = []

        select_object = Select(country_dropdown)
        country_options = [option.text for option in select_object.options]

        for country in range(1,len(country_options)):  # Skipping the first option ('All')
            country_dropdown_in = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_ddlCountry')))
            select_object1 = Select(country_dropdown_in)
            option = select_object1.options[country]

            option.click()
            time.sleep(1)

            print(country_options[country],country,'out of', len(country_options)-1,'countries.')
            search_button = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_btnSearch')))
            search_button.click()

            await asyncio.sleep(3)

            results_container = wait.until(EC.presence_of_element_located((By.ID, 'scrollResults')))

            html_content = results_container.get_attribute('innerHTML')
            soup = BeautifulSoup(html_content, 'html.parser')

            for row in soup.find_all('tr'):
                data_cells = row.find_all('td')

                if data_cells:
                    ofac_entry = {
                        'Country': country_options[country],
                        'URL': f"https://sanctionssearch.ofac.treas.gov/" + data_cells[0].find('a')['href'],
                        'Name': data_cells[0].find('a').text.strip(),
                        'Address': data_cells[1].text.strip(),
                        'Type': data_cells[2].text.strip(),
                        'Program': data_cells[3].text.strip(),
                        'List': data_cells[4].text.strip(),
                        'Score': data_cells[5].text.strip()
                    }
                    ofac_data.append(ofac_entry)

            reset_button = wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_btnReset')))
            reset_button.click()

            await asyncio.sleep(3)
        print('Data Extraction Done')
        df = pd.DataFrame(ofac_data)
        df.to_csv('ofac_list_final.csv', index=False)
        print('Data is transferred to ofac_list_final.csv file')

    finally:
        driver.quit()

if __name__ == '__main__':
    asyncio.run(scrape_ofac_data())