from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options
import os
os.environ["MOZ_HEADLESS"] = "1"

def initialize(link, executable_path):
    service = Service(executable_path=executable_path)
    options = Options()
    #options.add_argument("--headless")
    driver = webdriver.Firefox(service=service)
    wait = WebDriverWait(driver, 10)
    driver.get(link)

    return driver, wait

def locate_menu_options(driver: webdriver.Firefox, wait: WebDriverWait, search_string: str):
    # wait until loading overlay disappears
    wait.until(
        EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
    )

    # Locate container
    container = driver.find_element(By.XPATH, f"//label[text()='{search_string}']/parent::div")

    # Locate drop down menu
    dropdown_button = WebDriverWait(container, 3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dropdown-toggle"))
    )

    # Click drop down menu.
    dropdown_button.click()

    # Locate options in the menu.
    menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.dropdown-menu.show"))
    )

    # Get menu options
    menu_items = menu.find_elements(By.CSS_SELECTOR, "li a.dropdown-item")

    return menu_items

def check_n_rows(driver: webdriver.Firefox, rows, study_field):
    n = len(rows)

    for i in range(10):
        try:    
            WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, "count_partner"), str(n))
            )
            time.sleep(0.5)
            stats = driver.find_element(By.CLASS_NAME, "count_partner")
            n_partners = int(stats.text)   

            assert n == n_partners, f'Number of rows ({n}) does not match the number in the stats ({n_partners})'
            break
        
        except:
            print(f"Failed check {i+1} (found {n} expected {n_partners}). Try agian")
            time.sleep(5)            


def extract_row_data(driver, rows, row_index):
    try:
        cells = rows[row_index].find_elements(By.TAG_NAME, 'td')
        cells_data = [cell.text for cell in cells if cell.text != '']
    except:
        agreement_table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "result_table"))
        )
        rows_tmp = WebDriverWait(agreement_table, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'tr'))
        )[1:]
        cells = rows_tmp[row_index].find_elements(By.TAG_NAME, 'td')        
        cells_data = [cell.text for cell in cells if cell.text != '']

    assert len(cells_data) == 5

    return cells_data


def extract_agreement(driver, table, index):

    n_tries = 10

    for j in range(n_tries):
        try:
            # Extract agreement text
            rows = WebDriverWait(table, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'tr'))
            )[1:]
            row = rows[index]
            button = row.find_element(By.TAG_NAME, 'button')
            button.click()

            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))

            )
            university = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, "partner_result_table"))
            )
            break

        except:
            print("Failed to click on agreements button. Try again.")
            time.sleep(5)

    agreement_buttons = university.find_elements(By.CSS_SELECTOR, "a.btn")

    total_text = []
    for i in range(len(agreement_buttons)):


        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
        )

        for j in range(n_tries):
            try:
                if i == 0:
                    WebDriverWait(agreement_buttons[i], 10).until(
                        EC.element_to_be_clickable(agreement_buttons[i])
                    )
                    agreement_buttons[i].click()
                else:
                    university = driver.find_element(By.ID, "partner_result_table")
                    agreement_buttons_tmp = university.find_elements(By.CSS_SELECTOR, "a.btn")
                    agreement_buttons_tmp[i].click()

                agreement = WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "modal-content"))
                            )   

                WebDriverWait(driver, 10).until(
                   EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content .form-group"))
                )

                agreement_text = agreement.text

                if total_text == [] or agreement_text != total_text[0]:
                    total_text.append(agreement_text)

                # Close agreement
                close_button = agreement.find_element(By.CLASS_NAME, "close")
                close_button.click()

                break
            except:
                print("Failed to click on agreement and extract text. Try agian")
                time.sleep(5)

    # Close university popup
    close_button = driver.find_element(By.CLASS_NAME, "close")
    close_button.click()

    return total_text

def pick_menu_options(wait: WebDriverWait, driver, index, output_studies=True):
    
    wait.until(
    EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
    )

    n_visible_universities = driver.find_element(By.NAME, "result_table_length")
    select = Select(n_visible_universities)
    select.select_by_visible_text("All")

    time.sleep(1)

    acd_years = locate_menu_options(driver, wait, 'Academic year')

    for year in acd_years:
        if year.text == '2026/2027':
            year.click()

    
    wait.until(
    EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
    )

    time.sleep(1)

    study_fields = locate_menu_options(driver, wait, 'Study field')
    study_fields_text = [i.text for i in study_fields]
    item = study_fields[index]

    if item.text == study_fields_text[index]:
        item.click()


    if output_studies:
        return (study_fields, study_fields_text)

    return study_fields

def scrape(save_data = True):
    link = "https://www.service4mobility.com/europe/PortalServlet?identifier=KOBENHA01&preselectTab=ver_nav_button&showAll=0&showPartner=0&showAgreements=1"
    executable_path = "/usr/local/bin/geckodriver"
        
    print(f'Now scraping: {link}\n')

    driver, wait = initialize(link, executable_path)
    
    study_fields, study_fields_text = pick_menu_options(wait, driver, index=0)
    
    data_dict = {'Study field': [],
                 'Institution': [],
                 'Continent': [],
                 'Country': [],
                 'City': [],
                 'N agreements': [],
                 'Agreement_ID': []}
    agreement_data = {
        'Agreement_ID': [],
        'Institution': [],
        'Agreement_text': {}
    }
    
    for i in range(len(study_fields_text)):
        print(f'################### {study_fields_text[i]} ###################')
        count_agree = 0
        study_agree_count = 0
    
        if i > 0:
            driver, wait = initialize(link, executable_path)
    
        wait.until(
        EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
        )
        
        if i > 0:
            pick_menu_options(wait, driver, index=i, output_studies=False)
    
        # Find all agreements for current study field
    
        for t in range(10):
            time.sleep(1)
            try:
                agreement_table = driver.find_element(By.ID, "result_table")
    
                rows = WebDriverWait(agreement_table, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'tr'))
                )[1:]
    
                assert len(rows) > 10
                
                break
            
            except:
                print(f'Did not find enough rows (found {len(rows)}). Try again.')
                time.sleep(5)
    
    
        check_n_rows(driver, rows, study_fields_text[i])
    
        for j in range(len(rows)):
        
            cells_data = extract_row_data(driver, rows, j)
    
    
            total_text = extract_agreement(driver, agreement_table, j)
    
            for n, agreement_text in enumerate(total_text):
                study_agree_count += 1
            
                # Update data dict
                data_dict['Study field'].append(study_fields_text[i])
                data_dict['Institution'].append(cells_data[0])
                data_dict['Continent'].append(cells_data[1])
                data_dict['Country'].append(cells_data[2])
                data_dict['City'].append(cells_data[3])
                data_dict['N agreements'].append(int(cells_data[4]))
    
                if agreement_text in agreement_data['Agreement_text']:
                    data_dict['Agreement_ID'].append(agreement_data['Agreement_text'][agreement_text])
                    print(f'Agreement already found. ID: {agreement_data['Agreement_text'][agreement_text]}')
                else:
                    new_ID = len(agreement_data['Agreement_text'].keys())
                    data_dict['Agreement_ID'].append(new_ID)
                    count_agree += 1
    
                if agreement_text not in agreement_data['Agreement_text']:
                    agreement_data['Agreement_text'][agreement_text] = new_ID
                    agreement_data['Institution'].append(cells_data[0])
                    agreement_data['Agreement_ID'].append(new_ID)

        print(f'Number of agreements for this study field: {study_agree_count}')
        print(f'New agreements found: {count_agree}')
        print(f'Total unique agreements found: {len(agreement_data['Agreement_ID'])}\n')
    
        driver.quit()
    
    studies_df = pd.DataFrame(data_dict)
    agreement_data_df = pd.DataFrame((agreement_data['Agreement_ID'],
                                      agreement_data['Institution'],
                                      agreement_data['Agreement_text'].keys())).T

    agreement_data_df.columns = ['Agreement_ID', 'Institution', 'Agreement_text']

    if save_data:
        studies_df.to_csv('Study_fields_data.csv')
        agreement_data_df.to_csv('Agreement_data.csv')

    return (studies_df, agreement_data_df)


data_dict, agreement_data = scrape()


print("Data was scraped succesfully!")
