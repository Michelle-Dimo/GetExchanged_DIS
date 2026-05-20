from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
    driver = webdriver.Firefox(service=service)
    wait = WebDriverWait(driver, 10)
    driver.get(link)

    return driver, wait


def check_n_rows(driver: webdriver.Firefox, rows):
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
        
    return cells_data

def scrape():
    link = "https://www.service4mobility.com/europe/PortalServlet?identifier=KOBENHA01&preselectTab=ver_nav_button&showAll=0&showPartner=0&showAgreements=1"
    executable_path = "/usr/local/bin/geckodriver"

    driver, wait = initialize(link=link, executable_path=executable_path)

    # Wait for site to load
    wait.until(
        EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
    )

    # Switch to study report site
    try:
        button = driver.find_element(By.CSS_SELECTOR, "button.nav_inactive")
        button.click()
    except:
        menu = driver.find_element(By.CSS_SELECTOR, ".btn.dropdown-toggle.btn-outline-primary.mobileNavItem_col_c.border")
        menu.click()
        menu.send_keys(Keys.ARROW_DOWN)
        menu.send_keys(Keys.ENTER)


    wait.until(
        EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
    )

    n_visible_universities = driver.find_element(By.NAME, "result_table_length")
    select = Select(n_visible_universities)
    select.select_by_visible_text("All")


    print('########################## Checking number of rows matches site statistics ##########################')

    n_tries = 10
    for i in range(n_tries):
        wait.until(
            EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
        )
        try:
            reports_table = driver.find_element(By.ID, "result_table")
            rows = WebDriverWait(reports_table, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'tr'))
            )[1:]

            assert len(rows) > 10       
            break
        
        except:
            print(f'Did not find enough rows (found {len(rows)}). Try again.')
            time.sleep(3)

    check_n_rows(driver, rows)

    print(f'Number of rows found ({len(rows)}) matches!  :)\n')

    # Initalize dictionary to save data in.
    reports_dict = {
        "Report ID": [],
        "Institution": [],
        "Study field": [],
        "Academic year": [],
        "Report text": [],
        "Costs": [],
        "Choices": []
    }

    main_tab = driver.current_window_handle

    print('########################## Beginning report extraction ##########################')
    for i in range(len(rows)):
         
        for t in range(n_tries):
            try:
                cell_data = extract_row_data(driver, rows, i)
                reports_button = rows[i].find_element(By.CSS_SELECTOR, "button.btn.btn-outline-primary.btn_home.table_button")
                reports_button.click()
                break
            except:
                reports_table = driver.find_element(By.ID, "result_table")
                rows = WebDriverWait(reports_table, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'tr'))
                )[1:]
                cell_data = extract_row_data(driver, rows, i)
                reports_button = rows[i].find_element(By.CSS_SELECTOR, "button.btn.btn-outline-primary.btn_home.table_button")
                reports_button.click()
                time.sleep(3)


        wait.until(
            EC.invisibility_of_element_located((By.ID, "globalLoadingPage"))
        )

        partner_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal-body.print-content"))
            )

        print(f"========================== Extracting reports from {cell_data[0]} ==========================")
        # Find number of pages with reports
        more_pages = True
        report_counter = 0
        while more_pages:

            next_button = partner_table.find_element(By.ID, "partner_result_table_next")

            try:
                # Find all reports on current page
                partner_rows = partner_table.find_elements(By.CSS_SELECTOR, "tbody > tr")

                for j in range(len(partner_rows)):
                
                    row_data = extract_row_data(driver, partner_rows, j)

                    if j == 0:
                        row_button = WebDriverWait(partner_rows[j], 10).until(
                            EC.element_to_be_clickable((By.TAG_NAME, "button"))
                        )
                        row_button.click()
                    else:
                        partner_table_tmp = wait.until(
                        EC.presence_of_element_located((By.ID, 'partner_result_table'))
                        )
                        partner_rows_tmp = partner_table_tmp.find_elements(By.CSS_SELECTOR, "tbody > tr")
                        row_button = WebDriverWait(partner_rows_tmp[j], 10).until(
                            EC.element_to_be_clickable((By.TAG_NAME, "button"))
                        )
                        row_button.click()

                    # Wait until a new tab appears
                    WebDriverWait(driver, 10).until(
                        lambda d: len(d.window_handles) > 1
                    )

                    # Find new tab
                    new_tab = driver.window_handles[-1]
                    driver.switch_to.window(new_tab)

                    # Make sure the tab is fully loaded
                    WebDriverWait(driver, 20).until(
                        lambda d: d.current_url != "about:blank"
                    )

                    # Extract all text from the report
                    report = wait.until(
                        EC.presence_of_element_located((By.ID, "inputForm"))
                    )
                    report_text = report.text

                    # Find money spent
                    for t in range(n_tries):
                        try:
                            money_elements = report.find_elements(By.CSS_SELECTOR, "input.bt-input.form-control.numbers-plaintext.w-25.calculate-further-field")
                            assert len(money_elements) == 8
                            money_spent = [el.get_attribute("value") for el in money_elements]

                            if t > 0:
                                print("Succeded in finding all expenditure elements!")
                            break
                        except:
                            print(f"Did not find enough fields with money spent written in report {report_counter}. Found {len(money_elements)}. Trying again.")
                            time.sleep(5)

                    # Find the choices made on multiple choice questions
                    multiple_choice_elements = report.find_elements(By.CSS_SELECTOR, "div.controls.d-inline-block")
                    choices_made = []
                    for element in multiple_choice_elements:
                        choices = element.find_elements(By.CSS_SELECTOR, "div.form-check")

                        for choice in choices:
                            input = choice.find_element(By.TAG_NAME, "input")

                            if input.is_selected():
                                choices_made.append(choice.text)


                    driver.close()
                    driver.switch_to.window(main_tab)
                    
                    if len(row_data) != 5:
                        print(row_data, len(row_data))    
                        print("Missing Study field")
                        reports_dict["Study field"].append('')
                    else:
                        reports_dict["Study field"].append(row_data[3])
    
                    report_counter +=1
                    reports_dict["Report ID"].append(len(reports_dict["Report ID"]))
                    reports_dict["Institution"].append(row_data[1])
                    reports_dict["Academic year"].append(row_data[-1])
                    reports_dict["Costs"].append(pd.Series(money_spent))
                    reports_dict["Report text"].append(report_text)
                    reports_dict["Choices"].append(pd.Series(choices_made))

                next_button.click()

            except:
                more_pages = False
                print(f"Checked all pages for partner {cell_data[0]}")


        for t in range(n_tries):

            try:
                close_button = wait.until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "close"))
                        )
                close_button.click()
                break
            except:
                print("Failed to find close button on univsersity specific table.")

        try: 
            assert report_counter == int(cell_data[-1])
        except:
            print(f"Number of reports does not match the number of reports stated on the website for {cell_data[0]}")
            print("Checking if the number was updated while the reports where scraped.")
            time.sleep(5)
            reports_table = driver.find_element(By.ID, "result_table")
            rows = WebDriverWait(reports_table, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'tr'))
            )[1:]
            cell_data = extract_row_data(driver, rows, i)


        print(f"Extracted {report_counter} report(s)\n")

    print("Finished extracting all reports")

    df = pd.DataFrame(reports_dict)
    df.to_csv("Reports.csv", index=False)

    return 

rp_dict = scrape()
