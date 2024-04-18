import os

def delete_png_files(folder_path):
    try:
        # Get list of files in the folder
        files = os.listdir(folder_path)
        # Iterate over files and delete .png files
        for file in files:
            if file.endswith('.png'):
                os.remove(os.path.join(folder_path, file))
                print(f"Deleted: {file}")

        print("All .png files deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")