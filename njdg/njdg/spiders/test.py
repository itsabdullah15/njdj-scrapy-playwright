import csv

def update_csv(file_path, row, column, value):
    # Open the CSV file in append mode
    with open(file_path, 'a', newline='') as csvfile:
        # Create a CSV writer object
        csv_writer = csv.writer(csvfile)
        # Write the data to the specified row and column
        csv_writer.writerow([''] * (column - 1) + [value])

# Example usage:
file_path = "/home/abdullah/Desktop/Code/Python/PythonBasicProject/Abdullah/njdj-scrapy-playwright/njdg/njdg/spiders/Output/ANDAMAN & NICOBAR/data_track.csv"

update_csv(file_path, 2, 1, '2024')  # Fill cell A2 with '2024'
update_csv(file_path, 2, 2, '2024')  # Fill cell B2 with '2024'
update_csv(file_path, 2, 3, '2024')  # Fill cell B2 with '2024'
update_csv(file_path, 2, 4, '2024')  # Fill cell B2 with '2024'

