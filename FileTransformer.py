import os
from PIL import Image
import pillow_heif  # Ensure this is installed
from multiprocessing import Pool
from tqdm import tqdm
import subprocess

# Register HEIC support with Pillow
pillow_heif.register_heif_opener()

# Function to list available directories for the user to select from
def select_directory(available_directories):
    print("Select the directory containing the HEIC files:")
    for i, directory in enumerate(available_directories):
        print(f"{i + 1}. {directory}")

    while True:
        try:
            choice = int(input("Enter the number corresponding to your choice: "))
            if 1 <= choice <= len(available_directories):
                return available_directories[choice - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Function to get HEIC files from a directory
def get_heic_files(path):
    files = []
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        if filename.lower().endswith(".heic"):
            files.append(file_path)
    return files

# Function to convert HEIC to JPG
def convert_heic_to_jpg(args):
    file_path, destination_directory = args
    try:
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            new_filename = os.path.splitext(os.path.basename(file_path))[0] + ".jpg"
            destination_path = os.path.join(destination_directory, new_filename)
            img.save(destination_path, "JPEG")
        return 1  # Notify success
    except Exception as e:
        print(f"Failed to convert {os.path.basename(file_path)}: {e}")
        return 0  # Notify failure

if __name__ == "__main__":
    print("Installing dependencies...\n\n")
    subprocess.run(['pip', 'install', '-r','./requirements.txt'])
    print("\n\nDependencies Installed!\n\n")

    # Predefined directories for input selection
    available_directories = os.listdir()

    # Ask the user to select the source directory
    source_directory = select_directory(available_directories)

    # Ask the user to input the destination directory
    destination_directory = input("Enter the output directory path (free text allowed): ").strip()

    # Create destination directory if it doesn't exist
    os.makedirs(destination_directory, exist_ok=True)

    # Get HEIC files from the source directory
    files = get_heic_files(source_directory)
    total_files = len(files)

    if total_files == 0:
        print("No HEIC files found in the selected directory.")
        exit()

    # Prepare the arguments for each conversion
    args = [(file, destination_directory) for file in files]

    # Initialize the progress bar
    with tqdm(total=total_files, desc="Converting HEIC files", unit="file") as progress_bar:
        # Convert files using a pool of processes
        with Pool() as pool:
            for result in pool.imap_unordered(convert_heic_to_jpg, args):
                if result == 1:
                    progress_bar.update(1)  # Update the progress bar for each successful conversion

    print("Conversion completed!")
