import os
import sys
import math
import shutil
import urllib.request
import tarfile
import zipfile
import pip


# ----- Setup script for the DJ_bot application -----


# Display the download state in the terminal
def download_hook(block_count, block_size, total_size):
    get_size = block_count * block_size
    get_prop = get_size / total_size
    percent = math.floor(get_prop * 100)

    done_number = math.floor(get_prop * 20)
    leave_number = 20 - done_number

    progress_bar = "\t[" + ("█" * done_number) + (" " * leave_number) + "] - " + str(percent) + "%"

    # Display the progress bar
    sys.stdout.write(progress_bar)
    sys.stdout.flush()

    # Display a carriage return
    if get_prop < 1:
        sys.stdout.write("\r")
        sys.stdout.flush()
    else:
        sys.stdout.write("\n")
        sys.stdout.flush()


# Extract a tar archive file into a specific path
def extract_tar(archive, member, final):
    tar_file = tarfile.open(archive)
    tar_file.extract(member=member, path=tmp_dir)
    tar_file.close()
    os.replace(tmp_dir + member, final)


# Extract a zip archive file into a specific path
def extract_zip(archive, member, final):
    zip_file = zipfile.ZipFile(archive)
    zip_file.extract(member=member, path=tmp_dir)
    zip_file.close()
    os.replace(tmp_dir + member, final)


# Define the directory and file variables
tmp_dir = "./.tmp/"
ffmpeg_dir = "./ffmpeg/"


# Define ffmpeg download urls, file names and extracting function
ffmpeg_download_info = [
    {
        "url": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
        "file": "fflinamd64.tar.xz",
        "func": extract_tar,
        "member": "ffmpeg-4.3.1-amd64-static/ffmpeg",
    },
    {
        "url": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz",
        "file": "fflini686.tar.xz",
        "func": extract_tar,
        "member": "ffmpeg-4.3.1-i686-static/ffmpeg"
    },
    {
        "url": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz",
        "file": "fflinarm64.tar.xz",
        "func": extract_tar,
        "member": "ffmpeg-4.3.1-arm64-static/ffmpeg"
    },
    {
        "url": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-armhf-static.tar.xz",
        "file": "fflinarmhf.tar.xz",
        "func": extract_tar,
        "member": "ffmpeg-4.3.1-armhf-static/ffmpeg"
    },
    {
        "url": "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-armel-static.tar.xz",
        "file": "fflinarmel.tar.xz",
        "func": extract_tar,
        "member": "ffmpeg-4.3.1-armel-static/ffmpeg"
    },
    {
        "url": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "file": "ffwin64.zip",
        "func": extract_zip,
        "member": "ffmpeg-4.3.1-2020-11-08-essentials_build/bin/ffmpeg.exe"
    }
]


# Ask the user the ffmpeg binary he/she wants to download
arch_choice = -1

print("To avoid BIG and USELESS downloads, please choose your OS and CPU model in the list below :")
print("\t1 - Linux x64 (amd64)")
print("\t2 - Linux x86 (i686)")
print("\t3 - Linux arm64")
print("\t4 - Linux armhf")
print("\t5 - Linux armel")
print("\t6 - Windows 64")

while arch_choice == -1:
    try:
        arch_choice = int(input("Input a number : ")) - 1
        if arch_choice < 0 or arch_choice > len(ffmpeg_download_info) - 1:
            print("Input a number between 1 and " + str(len(ffmpeg_download_info)))
            arch_choice = -1
    except ValueError as _:
        print("Please input a number...")
        arch_choice = -1

ffmpeg_download_url = ffmpeg_download_info[arch_choice]["url"]
ffmpeg_archive = tmp_dir + ffmpeg_download_info[arch_choice]["file"]
ffmpeg_member = ffmpeg_download_info[arch_choice]["member"]
ffmpeg_extract_func = ffmpeg_download_info[arch_choice]["func"]


# Create the needed directories
try:
    os.mkdir(tmp_dir)
except FileExistsError as _:
    pass

try:
    os.mkdir(ffmpeg_dir)
except FileExistsError as _:
    pass


# Finally, start the installation
print("\n===== Download and install dependencies =====\n")

# Download the ffmpeg binary
print("Download the ffmpeg binary... (It can take few minutes)")
urllib.request.urlretrieve(ffmpeg_download_url, ffmpeg_archive, download_hook)
print("Download successful !")

# Install the ffmpeg binary
print("Install the ffmpeg binary...")
ffmpeg_extract_func(ffmpeg_archive, ffmpeg_member, ffmpeg_dir + "ffmpeg")
print("Installation successful !")

# Clean the temporary directory
shutil.rmtree(tmp_dir, ignore_errors=True)

# Install the pip dependencies
print("\n===== Install pip dependencies =====\n")
pip.main(["install", "-r", "requirements.txt"])

print("\n===== Installation complete ======")
