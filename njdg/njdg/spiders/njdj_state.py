import scrapy
from playwright.async_api import async_playwright, TimeoutError
import asyncio
import time
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
from datetime import datetime
import re
import numpy as np
import os
import csv
from .mapping_file import IDENS
from ..utils import delete_png_files
from .Capthas_solution import first_captcha_solution,solving_second_captcha
from .get_data import case_type,filing_number,filing_date,registration_number,crn_number,\
registration_date,first_hearing_date, next_hearing,stage_of_case,court_number_and_judge,\
petitioner_and_advocate, respondent_and_advocate,under_act, under_section
from .back_function import fifth_back_fucntion, fourth_back_func, third_back_func, second_back_func, first_back_func
from njdg.spiders.njdj_constant import FETCH_YEAR_DATE, NETWORK_IDLE, STATE_BODY_REPORT,\
EXAMPLE_YEAR_NEXT_PAGENATION, SECOND_LOOP_BUTTON_STATE_REPORT, DIST_REPORT_BODY, \
EST_REPORT_BODY, CAPTCHA_IMAGE_XPATH, CAPTCHA_FILL_BOX, SUBMIT_BUTTON, \
POPUP_ALERT, CASES_XPATH, CASE_NEXT_PAGENATION_XPATH, \
SECOND_CAPTCHA_IFRAME_XPATH, SECOND_LOOP_CAPTCHA_XPATH, SECOND_CAPTCHA_BOX, \
SECOND_CAPTCHA_SUBMIT_BUTTON, SECOND_CAPTCHA_ERROR_XPATH, FIRST_BACK_XPATH, \
SECOND_BACK_XPATH, THIRD_BACK_XPATH, FOURTH_BACK_XPATH, FIFTH_BACK_XPATH, \
IFRAME_XPATH_DATA_PAGE


class MySpider(scrapy.Spider):
    name = "njdj_state"
    start_urls = [IDENS.state_url]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    async def parse(self, response):
        async with async_playwright() as p:
            current_datetime = datetime.now()  # Get the current date and time
            current_date = datetime.now().strftime("%Y-%m-%d")  # Assign Current Dates

            # STEP 0: Creating FOLDER/FILE STRUCTURE FOR OUTPUT 
            delete_png_files(IDENS.capctcha_folder_path)
            Output_Folder_Location = IDENS.Output_Folder_Location
            folder_path = os.path.join(Output_Folder_Location, current_date)  # Construct folder path

            try:
                os.makedirs(folder_path)  # Create folder if it doesn't exist
                print(f"Folder '{current_date}' created successfully at {Output_Folder_Location}")
            except FileExistsError:
                print(f"Folder '{current_date}' already exists at {Output_Folder_Location}")

            csv_file_path = f'{Output_Folder_Location}/{current_date}/Audit_{current_date}.csv'  # Assign CSV Paths
            if not os.path.isfile(csv_file_path):  # Check if the CSV file existss
                with open(csv_file_path, 'w', newline='',
                          encoding='utf-8') as csv_file:  # If it doesn't exist, create the file and write header
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([
                        'Cases',
                        'Case Type',
                        'Filing Number',
                        'Filing Date',
                        'Registration Number',
                        'Registration Date',
                        'CNR Number',
                        'First Hearing Date',
                        'Next Hearing Date',
                        'Stage of Case',
                        'Court Number and Judge',
                        'Petitioner and Advocate',
                        'Respondent and Advocate',
                        'Under Act(s)',
                        'Under Section(s)',
                        'Date of data scraping'
                    ])

            error_file_path = f'{Output_Folder_Location}/{current_date}/Error_log_{current_date}.csv'
            if not os.path.isfile(error_file_path):
                with open(error_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([
                        'Cases',
                        'Error',
                        'Date'
                    ])

            def csv_file(data):
                # CRNNumber_for_file_name = CRNNumber[0]
                with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(data)

            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.goto(response.url)

            # Click on the link
            await page.evaluate(FETCH_YEAR_DATE)
            await page.wait_for_load_state(NETWORK_IDLE)  # Wait for the content to update

            async def get_data_from_file():    
                await page.wait_for_selector(IFRAME_XPATH_DATA_PAGE,timeout=10000)
                iframe_element = await page.query_selector(IFRAME_XPATH_DATA_PAGE)
                case_frame = await iframe_element.content_frame()

                # Extract the "Case Types" value
                # Run all asynchronous functions concurrently
                results = await asyncio.gather(
                    case_type(case_frame),
                    filing_number(case_frame),
                    filing_date(case_frame),
                    registration_number(case_frame),
                    crn_number(case_frame),
                    registration_date(case_frame),
                    first_hearing_date(case_frame),
                    next_hearing(case_frame),
                    stage_of_case(case_frame),
                    court_number_and_judge(case_frame),
                    petitioner_and_advocate(case_frame),
                    respondent_and_advocate(case_frame),
                    under_act(case_frame),
                    under_section(case_frame)
                )
                
                # Unpack the results for use
                (case_type_result, filing_number_result, filing_date_result,
                registration_number_result, crn_number_result,
                registration_date_result, first_hearing_date_result,
                next_hearing_result, stage_of_case_result,
                court_number_and_judge_result, petitioner_and_advocate_result,
                respondent_and_advocate_result, under_act_result,
                under_section_result) = results

                # Print the results
                print(f"Case Type: {case_type_result}")
                print(f"Filing Number: {filing_number_result}")
                print(f"Filing Date: {filing_date_result}")
                print(f"Registration Number: {registration_number_result}")
                print(f"CRN Number: {crn_number_result}")
                print(f"Registration Date: {registration_date_result}")
                print(f"First Hearing Date: {first_hearing_date_result}")
                print(f"Next Hearing: {next_hearing_result}")
                print(f"Stage of Case: {stage_of_case_result}")
                print(f"Court Number and Judge: {court_number_and_judge_result}")
                print(f"Petitioner and Advocate: {petitioner_and_advocate_result}")
                print(f"Respondent and Advocate: {respondent_and_advocate_result}")
                print(f"Under Act: {under_act_result}")
                print(f"Under Section: {under_section_result}")

                # Example usage:
                data_to_save = [
                    case[0],
                    case_type_result,
                    filing_number_result,
                    filing_date_result,
                    registration_number_result,
                    registration_date_result,
                    crn_number_result,
                    first_hearing_date_result,
                    next_hearing_result,
                    stage_of_case_result,
                    court_number_and_judge_result,
                    petitioner_and_advocate_result,
                    respondent_and_advocate_result,
                    under_act_result,
                    under_section_result,
                    current_date
                ]

                csv_file(data_to_save)
                case.clear()
                time.sleep(3)

            case = []
            async def get_case_text_and_click_on_case_button():
                while True:
                    await page.wait_for_selector(CASES_XPATH, state='visible')
                    elements = await page.query_selector_all(CASES_XPATH)
                    for element in elements:
                        element_case_text = await element.inner_text() # Retrieve the text of the element
                        case.append(element_case_text)
                        print("ELEMENT TEXT: ", element_case_text)
                        await page.wait_for_load_state(NETWORK_IDLE)
                        await element.click() #Clicking on Case(Element) for second captcha

                        #STEP 7: SOLVING THE SECOND CAPTHCHA
                        await solving_second_captcha(page,SECOND_CAPTCHA_IFRAME_XPATH,
                                 SECOND_LOOP_CAPTCHA_XPATH,SECOND_CAPTCHA_BOX,
                                 SECOND_CAPTCHA_SUBMIT_BUTTON,SECOND_CAPTCHA_ERROR_XPATH)
                        await get_data_from_file()
                        await fifth_back_fucntion(page, FIFTH_BACK_XPATH)
                    
                    next_page_elements = await page.query_selector_all(CASE_NEXT_PAGENATION_XPATH)
                    if next_page_elements:
                        await next_page_elements[0].click()
                    else:
                        print("Button not present")
                        break

            async def fourth_loop_establishment():
                time.sleep(3)
                await page.wait_for_selector(EST_REPORT_BODY, state='visible', timeout=5000)
                elements = await page.query_selector_all(EST_REPORT_BODY)
                print("LEN OF ELEMENTS in ESTABLISHMENT: ",len(elements))
                establishment_row = 0
                for element in elements:
                    # if establishment_row < 1:
                    #     establishment_row+=1
                    #     continue
                    time.sleep(3)
                    await asyncio.sleep(1)
                    await element.is_visible()
                    await element.click()
                    await page.wait_for_load_state(NETWORK_IDLE)

                    #STEP 5: First Captcha Solution
                    await first_captcha_solution(page,CAPTCHA_IMAGE_XPATH,CAPTCHA_FILL_BOX,SUBMIT_BUTTON,POPUP_ALERT)

                    #STEP 6: Click on Button and Get Case text
                    await get_case_text_and_click_on_case_button()
                    await fourth_back_func(page, FOURTH_BACK_XPATH)

            async def third_loop_district():
                await page.wait_for_selector(DIST_REPORT_BODY, state="visible",timeout=5000)
                elements = await page.query_selector_all(DIST_REPORT_BODY)
                print("LENGTH OF District Element: ",len(elements))
                dist_row = 0
                for element in elements:
                    # if dist_row < 4:
                    #     dist_row+=1
                    #     continue
                    await asyncio.sleep(1)
                    await element.is_visible()
                    await element.click()
                    await page.wait_for_load_state(NETWORK_IDLE)

                    #STEP 4: Fourth Button
                    print("GOING TO ENTER IN THE FOURTH LOOP ")
                    await fourth_loop_establishment()
                    await third_back_func(page, THIRD_BACK_XPATH)

            async def second_loop_state():
                await page.wait_for_selector(SECOND_LOOP_BUTTON_STATE_REPORT, state="visible",timeout=5000)
                await page.click(SECOND_LOOP_BUTTON_STATE_REPORT)
                await page.wait_for_load_state(NETWORK_IDLE) 

            # STEP 1: First Loop
            async def first_loop_year():
                while True:
                    await page.wait_for_selector(STATE_BODY_REPORT,state='visible',timeout=5000)
                    elements = await page.query_selector_all(STATE_BODY_REPORT)
                    await page.wait_for_load_state(NETWORK_IDLE)
                    print("LENGTH OF FIRST LOOP ELEMETS: ",len(elements))
                    first_loop_year_row = 0
                    for element in elements:
                        # if first_loop_year_row < 7:
                        #     first_loop_year_row += 1
                        #     continue

                        await element.click()
                        await page.wait_for_load_state(NETWORK_IDLE)
                        
                        #STEP 2: Second Button
                        await second_loop_state()
                        time.sleep(1)
                        print("GOING TO ENTER IN THE THIRD LOOP DISTRICT")
                        
                        #STEP 3: Third Button
                        await third_loop_district()
                        print("THIRD LOOP DISTRICT DONE")
                        time.sleep(1)
                        await second_back_func(page, SECOND_BACK_XPATH)
                        time.sleep(1)
                        await first_back_func(page, FIRST_BACK_XPATH)
                        time.sleep(1)
                    
                    next_page_elements = await page.query_selector_all(EXAMPLE_YEAR_NEXT_PAGENATION)
                    if next_page_elements: # Check if any next page elements are found
                        await next_page_elements[0].click()
                        await asyncio.sleep(3) # Optional: wait for a specific amount of time (e.g., 3 seconds) if needed
                    else:
                        print("Button not present")
                        break

            await first_loop_year()      

            time.sleep(2)

              

# Run the spider
if __name__ == "__main__":
    print("Starting the script...")
    process = MySpider()
    print("Calling start_requests()...")
    asyncio.run(process.start_requests())
