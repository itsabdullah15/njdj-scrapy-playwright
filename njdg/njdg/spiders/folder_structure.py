import os
import csv
from datetime import datetime
from .mapping_file import IDENS

class FileLogger:
    def __init__(self):
        # Call setup_files to initialize paths for CSV and error files, as well as the case of hearing folder
        self.csv_file_path, self.error_file_path, self.case_of_hearing_folder, self.data_tracker_file_path = self.setup_files()

    def setup_files(self):
        current_date = datetime.now().strftime("%Y-%m-%d")  # Get the current date in "YYYY-MM-DD" format
        Output_Folder_Location = IDENS.Output_Folder_Location  # Get the output folder location from the IDENS object
        folder_path = os.path.join(Output_Folder_Location, IDENS.STATE_NAME)  # Construct the folder path using the output folder location and state name

        # Create the folder if it doesn't exist
        try:
            os.makedirs(folder_path)
            print(f"Folder created successfully at {Output_Folder_Location}")
        except FileExistsError:
            print(f"Folder already exists at {Output_Folder_Location}")

        # Define the paths for the CSV files
        csv_file_path = os.path.join(Output_Folder_Location, IDENS.STATE_NAME, "Audit_Logs.csv")
        error_file_path = os.path.join(Output_Folder_Location, IDENS.STATE_NAME, "Error_logs.csv")
        data_tracker_file_path = os.path.join(Output_Folder_Location, IDENS.STATE_NAME, "data_track.csv")
        case_of_hearing_folder = os.path.join(Output_Folder_Location, IDENS.STATE_NAME, IDENS.CaseOfHearingFolder)

        # Check if the audit log CSV file exists; if not, create it and write the header
        if not os.path.isfile(csv_file_path):
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
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

        # Check if the error log CSV file exists; if not, create it and write the header
        if not os.path.isfile(error_file_path):
            with open(error_file_path, 'w', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([
                    'Cases',
                    'Error',
                    'Date'
                ])

        # Create the case of hearing folder if it doesn't exist
        if not os.path.exists(case_of_hearing_folder):
            os.makedirs(case_of_hearing_folder)
            print(f"Folder '{case_of_hearing_folder}' created successfully.")
        else:
            print(f"Folder '{case_of_hearing_folder}' already exists.")

        # Return the paths of the CSV files and the case of hearing folder
        return csv_file_path, error_file_path, case_of_hearing_folder

    def log_to_csv(self, data):
        # Log data to the CSV file specified in self.csv_file_path
        with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(data)

    def log_to_error_file(self, error_log):
        # Log error data to the error log CSV file specified in self.error_file_path
        with open(self.error_file_path, 'a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(error_log)
    
    def update_and_save(self, variable_name, new_value):
        try:
            with open(IDENS.data_tracker_path, "r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            print("No existing data file found.")
            return

        updated_lines = []
        for line in lines:
            if line.startswith(variable_name):
                updated_lines.append(f"{variable_name} = {repr(new_value)}\n")
            else:
                updated_lines.append(line)

        try:
            with open(IDENS.data_tracker_path, "w") as file:
                file.writelines(updated_lines)
        except Exception as e:
            print("Error:", e)

    
    def create_case_folder(self,element_case_text):
        path=f'{self.case_of_hearing_folder}/{element_case_text}'
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Folder '{path}' created successfully.")
        else:
            print(f"Folder '{path}' already exists.")


