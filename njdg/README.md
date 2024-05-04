# National Judicial Data Grid (NJDG) Scrapper

## Description

This Python script is designed to extract case details from the National Judicial Data Grid (NJDG) web app using Selenium WebDriver and save them to a CSV file in the output folder within the current date folder. The script navigates through the website with respect to state names, clicks on total cases, then proceeds and solves 2 CAPTCHAs internally. After solving them, it extracts case details and saves them to a CSV file. This logic runs in a loop until data from the specified states is extracted.

For more information about NJDG, please visit [National Judicial Data Grid](https://njdg.ecourts.gov.in/).


## Table of Contents

- [Dependencies](#dependencies)
- [Files](#files)
- [Contact](#contact)
- [Important Notes](#important-notes)

## Dependencies

- **Selenium**: A Python library for automating web browsers.
- **PIL (Python Imaging Library)**: Required for image manipulation.
- **OpenCV**: A library for computer vision and image processing tasks. Used to enhance the captcha image for text extraction.
- **Firefox WebDriver**: WebDriver for the Firefox browser. Automatically managed by `webdriver_manager`.
- **Pytesseract**: Python binding to the Tesseract OCR engine for extracting text from images.


## How to Run the Python Project

Follow these steps to run the Python project:

1. **Clone the Repository:** Start by cloning the project repository from GitHub or any other version control platform.

    ```bash
    git clone https://github.com/itsabdullah15/njdj-scrapy-playwright.git
    ```

2. **Navigate to Project Directory:** Use the `cd` command to navigate to the directory where the project is located.

    ```bash
    cd project_directory
    ```

3. **Install Dependencies:** Before running the project, make sure you have all the necessary dependencies installed. You can install them using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

4. **Update Configuration (if necessary):** If your project requires any configuration settings, make sure to update them in the appropriate configuration files. For example, you may need to modify paths in the `mapping.py` file.

    ```python
    # mapping.py

    # Update paths according to your environment
    OUTPUT_FOLDER = 'path/to/output/folder'
    ```

5. **Run the Project:** Once everything is set up, you can run the project using the main Python file. 

    ```bash
    python main.py
    ```

6. **Follow On-Screen Instructions:** Depending on the project, you may need to follow on-screen instructions or provide input when prompted.

7. **View Results:** Once the bot has completed its execution, you can examine the outcomes located within the designated output folder. Within this folder, organized by the current date, you'll find two CSV files. The first, labeled "Audit_log," contains the extracted case data. Meanwhile, the second file, named "error_log," documents cases the bot couldn't extract due to website errors.

8. **Troubleshooting:** If you encounter any issues while running the project, refer to the project's documentation or reach out to the project maintainers for assistance.

Following these steps should allow you to successfully run the Python project on your local machine. Remember to update any necessary configuration settings before running the project.


## Files

The `main.py` file contains all the code and logic for extracting case details from the National Judicial Data Grid (NJDG) web app. This file handles the navigation through the website, the process of clicking on total cases, solving CAPTCHAs, and extracting case details. The script runs in a loop until data from the specified states is successfully extracted.

The `mappingfile.py` contains important dynamic paths and configurations required for the bot to run smoothly. It serves as a configuration file where variables related to paths, URLs, or any other dynamic elements are stored. These variables may need to be adjusted based on the environment or specific requirements of the bot's execution.


## Important Notes

- Ensure an active internet connection as the script interacts with a live website.
- The script assumes the structure of the website remains unchanged. Any changes in the website structure may require modifications to the XPath expressions used in the script.


## Contact

If you encounter any difficulties during the process of downloading dependencies or executing the Python scripts, feel free to reach out for assistance. You can contact me via email at itsabdullah.cg@gmail.com or message me on WhatsApp at +91 9540743471. I'm here to help you resolve any issues and ensure a smooth experience with the setup and usage of the provided scripts.
