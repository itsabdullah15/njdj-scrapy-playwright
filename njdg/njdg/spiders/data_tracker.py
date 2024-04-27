import asyncio
from playwright.async_api import async_playwright
import time
from .Capthas_solution import first_captcha_solution
from .njdj_constant import CAPTCHA_IMAGE_XPATH,CAPTCHA_FILL_BOX,SUBMIT_BUTTON,POPUP_ALERT

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()   
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto("https://njdg.ecourts.gov.in/njdgnew/?p=main/index&state_code=35~28")
        # Click on the link
        await page.evaluate("fetchYearData(\'tot\', 1)")
        await page.wait_for_load_state('networkidle')  # Wait for the content to update


        async def check_year_element(page, year):
            print("Checking Year")
            while True:
                # elements = await page.query_selector_all('(//tbody[@id="state_report_body"]/tr/td[@class="sorting_1"])')
                elements = await page.query_selector_all('//tbody[@id="state_report_body"]/tr')
                await page.wait_for_load_state('networkidle')
                time.sleep(1)  # Avoid using time.sleep() in async code, consider using asyncio.sleep() instead
                i = 0
                for element in elements:
                    text = await element.text_content()
                    text=text[:4]
                    print(text)
                    text = text.replace(' ', '')
                    print("Text:", text)
                    if text == year:
                        break
                    else:
                        i += 1
                
                print("No Match Year found, Going to check in the next page")
                next_page_elements = await page.query_selector_all('//a[@class="paginate_button next" and @aria-controls="example_year"]')
                if next_page_elements:  # Check if any next page elements are found
                    await next_page_elements[0].click()
                    await asyncio.sleep(1)  # Optional: wait for a specific amount of time (e.g., 1 seconds) if needed
                else:
                    print("Button not present")
                    break

            print(i)
            year_element = f"(//tbody[@id='state_report_body']/tr/td[4]/a)[{i}]"
            print(year_element)
            await page.click(year_element)
            time.sleep(1)
   
        
        async def check_state_element(page, state):
            element= await page.query_selector('(//tbody[@id="state_report_body"]/tr/td[@class="sorting_1"])[1]')
            await page.wait_for_load_state('networkidle')
            text = await element.text_content()
            print(text)
            if text==state:
                await page.click("(//tbody[@id='state_report_body']/tr/td[4]/a)[1]")
            time.sleep(10)


        async def check_district_element(page,district):
            elements = await page.query_selector_all('(//tbody[@id="dist_report_body"]/tr/td[@class="sorting_1"])')
            await page.wait_for_load_state('networkidle')
            i=1
            for element in elements:
                text = await element.text_content()
                print(text)
                if text==district:
                    break
                else:
                    i+=1

            dist_element=f'(//tbody[@id="dist_report_body"]/tr/td[4]/a)[{i}]'
            print(dist_element)
            await page.click(dist_element)
            time.sleep(5)


        async def check_establishment_element(page, establishment):
            elements = await page.query_selector_all('(//tbody[@id="est_report_body"]/tr/td[@class="sorting_1"])')
            await page.wait_for_load_state('networkidle')
            i=1
            for element in elements:
                text = await element.text_content()
                print(text)
                if text==establishment:
                    break
                else:
                    i+=1
            establishment_element=f'(//tbody[@id="est_report_body"]/tr/td[4]/a)[{i}]'
            print(establishment_element)
            await page.click(establishment_element)
            time.sleep(5)


        async def check_case_element(page, case):
            print("Checking Cases Element")
            while True:
                i=0
                elements= await page.query_selector_all("(//td[@class='sorting_1']/a)")
                for element in elements:
                    text = await element.text_content()
                    print("Text:", text.strip())
                    if text==case:
                        break
                    else:
                        i+=1
                
                print(i)
                
                CASE_NEXT_PAGENATION_XPATH = '//a[@class="paginate_button next" and @aria-controls="example_cases"]'
                next_page_elements = await page.query_selector_all(CASE_NEXT_PAGENATION_XPATH)
                if next_page_elements:
                    await next_page_elements[0].click()
                else:
                    print("Button not present")
                    break




        year=''
        state='Andaman and Nicobar'
        district='Port Blair'
        establishment='Civil Judge Sr Divn, Port Blair, Andaman'
        case='Misc. Civil Cases / 24 / 2024'

        await check_year_element(page, year)
        await check_state_element(page, state)
        await check_district_element(page, district)
        await check_establishment_element(page, establishment)
        await first_captcha_solution(page,CAPTCHA_IMAGE_XPATH,CAPTCHA_FILL_BOX,SUBMIT_BUTTON,POPUP_ALERT)
        await check_case_element(page, case)
        time.sleep(10)

