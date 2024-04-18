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
                await page.wait_for_selector(IFRAME_XPATH_DATA_PAGE)
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



            async def solving_second_captcha():
                for _ in range(15):
                    current_datetime = datetime.now()
                    current_datetime = current_datetime.strftime("%d_%m_%Y_%H_%M_%S")
                    img_download_path = f'{IDENS.capctcha_folder_path}/{current_datetime}.png'

                    iframe_element = await page.query_selector(SECOND_CAPTCHA_IFRAME_XPATH)
                    frame = await iframe_element.content_frame()

                    for _ in range(5):
                        await frame.wait_for_selector(SECOND_LOOP_CAPTCHA_XPATH,timeout=10000)
                        image_element = await frame.query_selector(SECOND_LOOP_CAPTCHA_XPATH)  # Locate the captcha image element within the iframe
                        time.sleep(2)
                    
                    image_bounding_box = await image_element.bounding_box()  # Get the bounding box of the captcha image element

                    # Calculate the absolute position of the captcha image element
                    absolute_left = image_bounding_box['x']
                    absolute_top = image_bounding_box['y']
                    width = image_bounding_box['width']  # Calculate the width and height of the captcha image element
                    height = image_bounding_box['height']

                    screenshot = await page.screenshot(full_page=True)  # Take a full-page screenshot
                    image = Image.open(BytesIO(screenshot)) # Convert the screenshot data to a Pillow image

                    # Calculate the coordinates of the captcha image within the screenshot
                    left = absolute_left
                    top = absolute_top
                    right = left + width
                    bottom = top + height
                    time.sleep(1.5)

                    cropped_image = image.crop((left, top, right, bottom))  # Crop the image to the specified area
                    cropped_image.save(img_download_path)  # Save the cropped image to a file

                    if img_download_path is not None:
                        image_path = img_download_path

                        def enhance_image(image_path, image_path_download, color_correction_factor=1.5):
                            img = cv2.imread(image_path)  # Read the image
                            color_corrected_img = np.clip(img * color_correction_factor, 0, 255).astype(np.uint8)  # Apply color correction
                            cv2.imwrite(image_path_download, color_corrected_img)  # Save the enhanced image
                            text = pytesseract.image_to_string(image_path_download)  # Or use 'thresh' if you applied thresholding
                            text = re.sub(r'[^a-zA-Z0-9]', '', text)
                            text = text[:5].lstrip()
                            print("SECOND CAPTCHA TEXT: ",text)
                            return text

                        image_path_download = f'{IDENS.capctcha_folder_path}/enhanced_one.png'
                        text = enhance_image(image_path, image_path_download)
                        if text == '':
                            text = 123

                        print("Extracted Text:", text)  # Print the extracted text
                    else:
                        print("Not Able to find the img Path")

                    captcha_input = frame.locator(SECOND_CAPTCHA_BOX)  # Interact with the CAPTCHA input field
                    await captcha_input.clear()
                    text = str(text)
                    await captcha_input.fill(text)

                    submit_button = await frame.query_selector(SECOND_CAPTCHA_SUBMIT_BUTTON)  # Locate and click the submit button
                    if submit_button:
                        await submit_button.click()
                        print("Clicked the submit button.")
                    else:
                        print("Submit button not found.")

                    print("CHECKING THE ERROR ELEMENT")
                    await asyncio.sleep(2)
                    error_element = await frame.query_selector(SECOND_CAPTCHA_ERROR_XPATH)
                    if error_element:
                        print("Error detected, retrying...")
                        await asyncio.sleep(0.5)
                        continue  # Retry the loop if there is an error
                    else:
                        print("Successfully submitted the captcha.")
                        break  # Exit the loop if successful

                print("Exited from 2nd Captcha Loop")

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
                        await solving_second_captcha()
                        await get_data_from_file()
                        await fifth_back_fucntion(page, FIFTH_BACK_XPATH)
                    
                    next_page_elements = await page.query_selector_all(CASE_NEXT_PAGENATION_XPATH)
                    if next_page_elements:
                        await next_page_elements[0].click()
                    else:
                        print("Button not present")
                        break

            async def first_captcha_solution():
                for _ in range(15):
                    current_datetime = datetime.now()
                    current_datetime = current_datetime.strftime("%d_%m_%Y_%H_%M_%S")
                    img_download_path = f'{IDENS.capctcha_folder_path}/{current_datetime}.png'

                    time.sleep(1.5)
                    async def get_captcha_image_element(page, max_retries=5, retry_delay=1):
                        for attempt in range(max_retries):
                            # Try to find the image element
                            image_element = await page.query_selector(CAPTCHA_IMAGE_XPATH)    
                            if image_element:
                                return image_element # If image element is found, return it
                            
                            # If not found, wait for some time before retrying
                            print(f"Captcha image not found, retrying in {retry_delay} seconds (Attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            
                        # If after all retries, the element is still not found, return None
                        print("Max retries reached. Captcha image not found.")
                        return None
                    
                    image_element = await get_captcha_image_element(page) # Usage example

                    bounding_box = await image_element.bounding_box()  # Get the bounding box of the image element
                    screenshot = await page.screenshot(full_page=True)  # Capture screenshot of the entire page

                    image = Image.open(BytesIO(screenshot))  # Use Pillow to open the screenshot and crop the desired area
                    left = bounding_box['x']
                    top = bounding_box['y']
                    right = left + bounding_box['width']
                    bottom = top + bounding_box['height']
                    cropped_image = image.crop((left, top, right, bottom))

                    cropped_image.save(img_download_path)  # Save the cropped image to a file

                    '''STEP 7 == Solving the Captcha img for solving'''
                    if img_download_path is not None:
                        image_path = img_download_path
                        img = cv2.imread(image_path)
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        blur = cv2.bilateralFilter(gray, 9, 75, 75)
                        text = pytesseract.image_to_string(blur)
                        text = text[:5]
                        print("Extracted Text:", text)
                    else:
                        print("Not Able to find")

                    '''STEP 8 == After Solving the Captcha Filling the data captcha data into input & Submit'''
                    await page.fill(CAPTCHA_FILL_BOX, text)  # Find and fill captcha input
                    await page.click(SUBMIT_BUTTON)  # Click on the submit button

                    # Handle alert if present
                    try:
                        alert = await page.wait_for_event(POPUP_ALERT,timeout=5000)
                        await alert.accept()  # Wait for alert and accept it
                        continue
                    except:
                        print("No alert found within the specified timeout.")
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
                    await first_captcha_solution()

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
