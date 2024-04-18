import scrapy
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
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

            browser = await p.chromium.launch(headless=True)
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

                # Extract the "Case Type" value
                async def case_type():
                    try:
                        case_type_element = await case_frame.query_selector(
                            "(//span[@class='case_details_table'])[1]")  # Locate the element using XPath
                        case_type_text = await case_type_element.text_content() if case_type_element else None  # Get the text content of the element
                        # If the element is found, split the text and get the "Case Type"
                        if case_type_text:
                            case_type = case_type_text.split(':')[-1].strip()
                            return case_type
                        else:
                            print("Case Type element not found.")
                            return None

                    except Exception as e:
                        print(f"An error occurred while fetching Case Type: {str(e)}")
                        return None

                async def filing_number():
                    """
                    This function locates the filing number information on a webpage using Playwright and returns the extracted filing number.
                    Returns:
                        filing_number: The extracted filing number as a string, or None if not found.
                    """
                    try:
                        # Locate the element containing filing information using XPath
                        filing_number_element = await case_frame.query_selector("(//span[@class='case_details_table'])[2]")

                        if filing_number_element:
                            # Get the text content of the located element
                            filing_info_text = await filing_number_element.text_content()

                            # Use regular expression to extract the filing number
                            filing_number_match = re.search(r'Filing\s*Number\s*:\s*(\d+/\d+)', filing_info_text)

                            # Check if a match is found
                            if filing_number_match:
                                filing_number = filing_number_match.group(1).strip()
                                # Return the extracted filing number
                                return filing_number
                            else:
                                print("Filing number not found.")
                        else:
                            print("Filing number element not found.")

                    except Exception as e:
                        print(f"An error occurred while fetching Filing Number: {str(e)}")
                        return None

                async def filing_date():
                    """Extract the filing date value."""
                    try:
                        # Locate the element with the filing date
                        filing_date_label = await case_frame.query_selector("(//span[@class='case_details_table'])[2]")

                        # Get the text content of the element
                        filing_date_text = await filing_date_label.text_content()

                        # Extract the filing date value from the text
                        filing_date_value = filing_date_text.split(':')[-1].strip()
                        # print("Filing Date:", filing_date_value)
                        return filing_date_value
                    except Exception as e:
                        print(f"An error occurred while fetching Filing Date Value: {str(e)}")
                        return None

                async def registration_number():
                    """Extract the registration number value."""
                    try:
                        # Locate the element with the registration number
                        registration_number_element = await case_frame.query_selector(
                            "(//span[@class='case_details_table'])[3]")

                        # Get the text content of the element
                        registration_number_text = await registration_number_element.text_content()

                        # Use regular expression to extract the registration number
                        registration_number_match = re.search(r'Registration Number\s*:\s*(\d+/\d+)',
                                                            registration_number_text)
                        if registration_number_match:
                            registration_number = registration_number_match.group(1).strip()
                            # print("Registration Number:", registration_number)
                            return registration_number
                        else:
                            print("Registration number not found.")
                            return None
                    except Exception as e:
                        print(f"An error occurred while fetching Registration Number: {str(e)}")
                        return None

                async def crn_number():
                    """Extract the CRN number value."""
                    try:
                        # Locate the element with the CRN number
                        CRN_Number_element = await case_frame.query_selector("(//span[@class='case_details_table'])[4]")

                        # Get the text content of the element
                        CRN_Number_text = await CRN_Number_element.text_content()

                        # Extract the CRN number value from the text
                        CRN_Number = CRN_Number_text.split(':')[-1].strip()
                        # print("CRN Number:", CRN_Number)
                        return CRN_Number
                    except Exception as e:
                        print(f"An error occurred while fetching CRN Number: {str(e)}")
                        return None

                async def registration_date():  # Registration Date
                    try:
                        # Locate the element using the XPATH and await for it
                        registration_date_element = await case_frame.query_selector(
                            '//*[@id="part1"]/div[1]/span[4]/span[2]/label[2]')

                        # Retrieve the text content of the element
                        registration_date = await registration_date_element.text_content()
                        if registration_date:
                            registration_date = registration_date.strip()
                            # Remove any colons from the date
                            if ':' in registration_date:
                                registration_date = registration_date.replace(':', '')
                            # Return the cleaned registration date
                            return registration_date
                        else:
                            print("Failed to retrieve registration date content.")
                            return None
                    except Exception as e:
                        print(f"An error occurred while fetching Registration Date: {str(e)}")
                        return None

                async def first_hearing_date():  # First Hearing Date
                    try:
                        # Locate the element using the XPATH and await for it
                        first_hearing_date_element = await case_frame.query_selector('(//div//span//label//strong)[2]')

                        # Retrieve the text content of the element
                        first_hearing_date = await first_hearing_date_element.text_content()
                        if first_hearing_date:
                            first_hearing_date = first_hearing_date.strip()
                            # Remove any colons from the date
                            if ':' in first_hearing_date:
                                first_hearing_date = first_hearing_date.replace(':', '')
                            # Return the cleaned first hearing date
                            return first_hearing_date
                        else:
                            print("Failed to retrieve first hearing date content.")
                            return None
                    except Exception as e:
                        print(f"An error occurred while fetching First Hearing Date: {str(e)}")
                        return None

                async def next_hearing():
                    """Next Hearing Date"""
                    try:
                        # Use Playwright's query_selector method with XPath to locate the element
                        next_hearing_date_element = await case_frame.query_selector('(//div//span//label//strong)[4]')
                        # Get the text content of the element
                        next_hearing_date = await next_hearing_date_element.text_content()
                        # Strip the text and remove colons if present
                        next_hearing_date = next_hearing_date.strip().replace(':', '')
                        return next_hearing_date
                    except Exception as e:
                        print(f"An error occurred while fetching Next Hearing Date: {str(e)}")
                        return None

                async def stage_of_case():
                    """Stage of Case"""
                    try:
                        # Use Playwright's query_selector method with XPath to locate the element
                        stage_of_case_element = await case_frame.query_selector('(//div//span//label//strong)[6]')
                        # Get the text content of the element
                        stage_of_case = await stage_of_case_element.text_content()
                        # Strip the text and remove colons if present
                        stage_of_case = stage_of_case.strip().replace(':', '')
                        return stage_of_case
                    except Exception as e:
                        print(f"An error occurred while fetching Stage of Case: {str(e)}")
                        return None

                async def court_number_and_judge():
                    """Court Number and Judge"""
                    try:
                        # Use Playwright's query_selector method with XPath to locate the element
                        court_number_and_judge_element = await case_frame.query_selector('(//div//span//label//strong)[8]')
                        # Get the text content of the element
                        court_number_and_judge = await court_number_and_judge_element.text_content()
                        # Strip the text and remove colons if present
                        court_number_and_judge = court_number_and_judge.strip().replace(':', '')
                        return court_number_and_judge
                    except Exception as e:
                        print(f"An error occurred while fetching Court Number and Judge: {str(e)}")
                        return None

                async def petitioner_and_advocate() -> str:
                    """Petitioner and Advocate"""
                    try:
                        # Use Playwright's query_selector method with class name to locate the element
                        petitioner_and_advocate_element = await case_frame.query_selector('.Petitioner_Advocate_table')
                        # Get the text content of the element and remove newlines
                        petitioner_and_advocate = await petitioner_and_advocate_element.text_content()
                        petitioner_and_advocate = petitioner_and_advocate.replace('\n', '')
                        return petitioner_and_advocate
                    except Exception as e:
                        print(f"An error occurred while fetching Petitioner and Advocate: {str(e)}")
                        return None

                async def respondent_and_advocate() -> str:
                    """Fetch the respondent and advocate information from the page."""
                    try:
                        # Locate the respondent and advocate table element by its class name
                        respondent_advocate_table_element = await case_frame.query_selector('.Respondent_Advocate_table')

                        if respondent_advocate_table_element:
                            # Retrieve the text of the element and replace newlines with an empty string
                            respondent_advocate_text = await respondent_advocate_table_element.inner_text()
                            respondent_advocate_text = respondent_advocate_text.replace('\n', '')
                            return respondent_advocate_text
                        else:
                            print("Respondent and Advocate table element not found.")
                            return None

                    except Exception as e:
                        print(f"An error occurred while fetching Respondent and Advocate: {str(e)}")
                        return None

                async def under_act() -> str:
                    """Fetch the under act information from the page."""
                    try:
                        # Locate the under act element using XPath
                        Under_Act_element = await case_frame.query_selector('//table[@id="act_table"]//tbody//tr[2]//td[1]')

                        if Under_Act_element:
                            Under_Act_text = await Under_Act_element.inner_text()
                            return Under_Act_text
                        else:
                            print("Under Act element not found.")
                            return None

                    except Exception as e:
                        print(f"An error occurred while fetching Under Act(s): {str(e)}")
                        return None

                async def under_section() -> str:
                    """Fetch the under section information from the page."""
                    try:
                        # Locate the under section element using XPath
                        Under_Section_element = await case_frame.query_selector(
                            '//table[@id="act_table"]//tbody//tr[2]//td[2]')

                        if Under_Section_element:
                            Under_Section_text = await Under_Section_element.inner_text()
                            return Under_Section_text
                        else:
                            print("Under Section element not found.")
                            return None

                    except Exception as e:
                        print(f"An error occurred while fetching Under Section(s): {str(e)}")
                        return None

                # case_type = await case_type()
                # filing_number = await filing_number()
                # filing_date = await filing_date()
                # registration_number = await registration_number()
                # crn_number = await crn_number()
                # registration_date = await registration_date()
                # first_hearing_date = await first_hearing_date()
                # next_hearing = await next_hearing()
                # stage_of_case = await stage_of_case()
                # court_number_and_judge = await court_number_and_judge()
                # petitioner_and_advocate = await petitioner_and_advocate()
                # respondent_and_advocate = await respondent_and_advocate()
                # under_act = await under_act()
                # under_section = await under_section()

                # Use asyncio.gather to run all functions concurrently
                (
                    case_type,
                    filing_number,
                    filing_date,
                    registration_number,
                    crn_number,
                    registration_date,
                    first_hearing_date,
                    next_hearing,
                    stage_of_case,
                    court_number_and_judge,
                    petitioner_and_advocate,
                    respondent_and_advocate,
                    under_act,
                    under_section,
                ) = await asyncio.gather(
                    case_type(),
                    filing_number(),
                    filing_date(),
                    registration_number(),
                    crn_number(),
                    registration_date(),
                    first_hearing_date(),
                    next_hearing(),
                    stage_of_case(),
                    court_number_and_judge(),
                    petitioner_and_advocate(),
                    respondent_and_advocate(),
                    under_act(),
                    under_section()
                )


                print(f"Case Type: {case_type}")
                print(f"Filling Number: {filing_number}")
                print(f"Filling Date: {filing_date}")
                print(f"Registration Number: {registration_number}")
                print(f"CRN Number: {crn_number}")
                print(f"Registration Number: {registration_date}")
                print(f"First Hearing Date: {first_hearing_date}")
                print(f"Next Hearing: {next_hearing}")
                print(f"Stage of Case: {stage_of_case}")
                print(f"Court Number and judge: {court_number_and_judge}")
                print(f"Petitioner and Advocate: {petitioner_and_advocate}")
                print(f"Respondent and Advocate: {respondent_and_advocate}")
                print(f"Under Act: {under_act}")
                print(f"Under Section: {under_section}")

                # Example usage:
                data_to_save = [
                    case[0],
                    case_type,
                    filing_number,
                    filing_date,
                    registration_number,
                    registration_date,
                    crn_number,
                    first_hearing_date,
                    next_hearing,
                    stage_of_case,
                    court_number_and_judge,
                    petitioner_and_advocate,
                    respondent_and_advocate,
                    under_act,
                    under_section,
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
                        await element.click() #Clicking on Case(Element) for second captcha
                        await page.wait_for_load_state(NETWORK_IDLE)

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
                        alert = await page.wait_for_event(POPUP_ALERT)
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
                    elements = await page.query_selector_all(STATE_BODY_REPORT)
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
