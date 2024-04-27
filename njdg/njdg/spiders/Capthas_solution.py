import time
import asyncio
from io import BytesIO
from PIL import Image
import pytesseract
import cv2
from datetime import datetime
import re
import numpy as np
from .mapping_file import IDENS

async def first_captcha_solution(page,CAPTCHA_IMAGE_XPATH,CAPTCHA_FILL_BOX,SUBMIT_BUTTON,POPUP_ALERT):
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



async def solving_second_captcha(page,SECOND_CAPTCHA_IFRAME_XPATH,
                                 SECOND_LOOP_CAPTCHA_XPATH,SECOND_CAPTCHA_BOX,
                                 SECOND_CAPTCHA_SUBMIT_BUTTON,SECOND_CAPTCHA_ERROR_XPATH):
    for _ in range(15):
        Flag = False
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
            Flag = True
            break  # Exit the loop if successful
    print("Exited from 2nd Captcha Loop")
    return Flag