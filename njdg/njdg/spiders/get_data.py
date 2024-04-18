import re

async def case_type(case_frame):
    try:
        case_type_element = await case_frame.query_selector("(//span[@class='case_details_table'])[1]")  # Locate the element using XPath
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

async def filing_number(case_frame):
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

async def filing_date(case_frame):
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

async def registration_number(case_frame):
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

async def crn_number(case_frame):
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

async def registration_date(case_frame):  # Registration Date
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

async def first_hearing_date(case_frame):  # First Hearing Date
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

async def next_hearing(case_frame):
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

async def stage_of_case(case_frame):
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

async def court_number_and_judge(case_frame):
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

async def petitioner_and_advocate(case_frame) -> str:
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

async def respondent_and_advocate(case_frame) -> str:
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

async def under_act(case_frame) -> str:
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

async def under_section(case_frame) -> str:
    """Fetch the under section information from the page."""
    try:
        # Locate the under section element using XPath
        Under_Section_element = await case_frame.query_selector('//table[@id="act_table"]//tbody//tr[2]//td[2]')

        if Under_Section_element:
            Under_Section_text = await Under_Section_element.inner_text()
            return Under_Section_text
        else:
            print("Under Section element not found.")
            return None

    except Exception as e:
        print(f"An error occurred while fetching Under Section(s): {str(e)}")
        return None