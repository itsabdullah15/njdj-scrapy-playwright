import csv
from .mapping_file import IDENS
import time
import asyncio
import aiohttp
import time
import os

link_pdf_xpath='//tr/td[@align="left"]/a[@href]'
table_xpath='//table[@class="history_table"]/tbody'

async def get_table_data(case_frame,element_case_text,browser):    

    table_element = await case_frame.query_selector(table_xpath)
    row_elements = await table_element.query_selector_all('tr') # Find all rows in the table
    
    # Extract table header data
    table_header_data = []
    if row_elements:
        table_header_cells = await row_elements[0].query_selector_all('th')  # Assuming the header is in the first row
        table_header_data = [await cell.text_content() for cell in table_header_cells]
        # Remove "Registration Number" from table header data
        table_header_data = [header for header in table_header_data if header != "Registration Number"]

    print("Table Header Data:")
    print(table_header_data)

    # Initialize a list to store the table data
    table_data = []
    for row in row_elements:  # Iterate over each row in the table
        cell_elements = await row.query_selector_all('td')  # Get all cells in the row
        row_data = [await cell.text_content() for cell in cell_elements]  # Extract the text content from each cell and append to the row data
        row_data = row_data[1:] # Remove the first column from each row of table_data
        table_data.append(row_data)  # Append the row data to the table data list
    
    print("Table Data: \n",table_data) # Print the extracted table data (or use it as needed)

    
    async def fetch_data(link_element, browser):
        date = await link_element.text_content()
        print("These Date of Hearing pdf is going to download:", date)
        href = await link_element.get_attribute('href')
        print("Href value:", href)
        base_url = 'https://njdg.ecourts.gov.in/njdgv1/civil/'
        full_url = base_url + href
        
        context = await browser.new_context()
        page = await context.new_page()  # create a new page inside context.
        await page.goto(full_url)
        time.sleep(5)  # Not recommended in async code, but for demonstration purposes
        path = f'{IDENS.Output_Folder_Location}/{IDENS.STATE_NAME}/{IDENS.CaseOfHearingFolder}/{element_case_text}/{date}.pdf'
        await page.pdf(path=path)  # Generate PDF
        print(f"Date: {date} pdf is saved at {path}")
        await context.close()  # dispose context once it is no longer needed.

    async def main():
        try:
            link_elements = await case_frame.query_selector_all('//tr/td[@align="left"]/a[@href]')
            if link_elements:
                tasks = []
                async with aiohttp.ClientSession() as session:
                    for link_element in link_elements:
                        tasks.append(fetch_data(link_element, browser))  # Assuming browser is defined elsewhere
                    await asyncio.gather(*tasks)
        except Exception as e:
            print(f"An error occurred in the main function: {e}")
            
    await main()


    folder_path = os.path.join(IDENS.Output_Folder_Location, IDENS.STATE_NAME, IDENS.CaseOfHearingFolder, element_case_text)
    if not os.path.exists(folder_path): # Check if the directory exists
        os.makedirs(folder_path) # If it doesn't exist, create it
    
    csv_file_path = os.path.join(folder_path, 'history_of_hearing.csv')
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if table_header_data:
            writer.writerow(table_header_data)
        writer.writerows(table_data)

    print(f"Table data saved to {csv_file_path}/history_of_hearing.csv")
