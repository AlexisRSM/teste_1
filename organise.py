55ogt import os
from datetime import datetime
import shutil
import logging
from tqdm import tqdm
from collections import defaultdict
from tkinter import filedialog, Tk
from rich.progress import Progress

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='organizer.log')

def create_folder_structure(root_folder, file_types=None, max_photo_years=5, skip_existing=False, detect_duplicates=True, sort_files=False):
    try:
        if not file_types:
            # Default file types if not specified
            file_types = {
                "Documents": [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
                "Photos": [".jpg", ".jpeg", ".png", ".gif"],
                "Videos": [".mp4", ".avi", ".mov", ".mkv"],
                "Music": [".mp3", ".wav", ".flac"],
                "Projects": [".py", ".java", ".cpp", ".html", ".css", ".js"],
                "Personal": [".zip", ".rar", ".7z", ".tar", ".gz"]
            }

        # Create main folders
        for folder in file_types:
            folder_path = os.path.join(root_folder, folder)
            os.makedirs(folder_path, exist_ok=True)
            logging.info(f"Created folder: {folder_path}")

        # Create photo folders by month and year
        if "Photos" in file_types:
            current_year = datetime.now().year
            for year in range(current_year, current_year - max_photo_years - 1, -1):  # Create folders for specified years
                year_folder = os.path.join(root_folder, "Photos", str(year))
                os.makedirs(year_folder, exist_ok=True)
                logging.info(f"Created folder: {year_folder}")
                for month in range(1, 13):
                    month_folder = os.path.join(year_folder, f"{month:02d}")
                    os.makedirs(month_folder, exist_ok=True)
                    logging.info(f"Created folder: {month_folder}")

        # Move files to respective folders
        total_files_moved = 0
        duplicates_found = defaultdict(list)
        with Progress() as progress:
            move_files_task = progress.add_task("[green]Moving files...", total=sum(len(files) for _, _, files in os.walk(root_folder)))
            for folder, extensions in file_types.items():
                for root, _, files in os.walk(root_folder):
                    for file in files:
                        progress.update(move_files_task, advance=1)
                        if os.path.splitext(file)[1].lower() in extensions:
                            source_path = os.path.join(root, file)
                            destination_folder = os.path.join(root_folder, folder)
                            destination_path = os.path.join(destination_folder, file)
                            
                            if detect_duplicates:
                                # Check for duplicate files
                                if os.path.exists(destination_path):
                                    logging.info(f"Duplicate file found: {file}")
                                    duplicates_found[folder].append(file)
                                    continue
                            
                            # Move the file
                            if not os.path.exists(destination_path) or not skip_existing:
                                shutil.move(source_path, destination_path)
                                total_files_moved += 1
                                logging.info(f"Moved file from {source_path} to {destination_path}")
                            else:
                                logging.info(f"File {file} already exists in {destination_folder}. Skipping.")

        # Sort files within folders
        if sort_files:
            for folder in file_types:
                folder_path = os.path.join(root_folder, folder)
                files_in_folder = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                files_in_folder.sort()
                for idx, file in enumerate(files_in_folder):
                    src = os.path.join(folder_path, file)
                    dst = os.path.join(folder_path, f"{idx+1:03d}_{file}")
                    os.rename(src, dst)
                    logging.info(f"Sorted file {file} in folder {folder} to {dst}")

        # Log summary of duplicates found
        if duplicates_found:
            logging.info("Duplicates found:")
            for folder, files in duplicates_found.items():
                logging.info(f"In folder '{folder}': {', '.join(files)}")

        # Remove empty folders
        for folder in os.listdir(root_folder):
            folder_path = os.path.join(root_folder, folder)
            if os.path.isdir(folder_path) and not os.listdir(folder_path):
                os.rmdir(folder_path)
                logging.info(f"Removed empty folder: {folder_path}")

        logging.info(f"Total files moved: {total_files_moved}")
        logging.info("Files organized successfully!")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

def get_root_folder():
    # Use a Tkinter file dialog to select the root folder
    root = Tk()
    root.withdraw()  # Hide the main window
    root_folder = filedialog.askdirectory(title="Select Root Folder")
    root.destroy()  # Clean up the Tkinter window
    return root_folder

def confirm_action(action_summary):
    while True:
        response = input(f"\nPlease confirm the following actions:\n{action_summary}\nProceed with organization? (yes/no): ").lower()
        if response in ["yes", "no"]:
            return response == "yes"
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def summarize_actions(file_types, max_photo_years, skip_existing, detect_duplicates, sort_files):
    summary = ""
    summary += f"Root Folder: {root_folder}\n"
    summary += f"Maximum Photo Years: {max_photo_years}\n"
    summary += f"Skip Existing Files: {'Yes' if skip_existing else 'No'}\n"
    summary += f"Detect and Handle Duplicates: {'Yes' if detect_duplicates else 'No'}\n"
    summary += f"Sort Files within Folders: {'Yes' if sort_files else 'No'}\n"
    summary += "File Types:\n"
    for folder, extensions in file_types.items():
        summary += f" - {folder}: {', '.join(extensions)}\n"
    return summary

if __name__ == "__main__":
    root_folder = get_root_folder()
    file_types = {
        "Documents": [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
        "Photos": [".jpg", ".jpeg", ".png", ".gif"],
        "Videos": [".mp4", ".avi", ".mov", ".mkv"],
        "Music": [".mp3", ".wav", ".flac"],
        "Projects": [".py", ".java", ".cpp", ".html", ".css", ".js"],
        "Personal": [".zip", ".rar", ".7z", ".tar", ".gz"]
    }
    max_photo_years = int(input("Enter the maximum number of years for photo folders (default is 5): ") or "5")
    skip_existing = input("Skip existing files with the same name? (yes/no, default is no): ").lower() == "yes"
    detect_duplicates = input("Detect and handle duplicate files? (yes/no, default is yes): ").lower() != "no"
    sort_files = input("Sort files within folders? (yes/no, default is no): ").lower() == "yes"
    
    action_summary = summarize_actions(file_types, max_photo_years, skip_existing, detect_duplicates, sort_files)
    if confirm_action(action_summary):
        create_folder_structure(root_folder, file_types, max_photo_years, skip_existing, detect_duplicates, sort_files)
    else:
        print("Organization canceled.")
