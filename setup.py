import os
import sys
import math
import urllib.request
import tarfile
import zipfile
import pip


# ----- Setup script for the DJ_bot application -----

# Download advance display function

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


# Create the needed directories

try:
    os.mkdir(".tmp/")
except FileExistsError as _:
    pass

try:
    os.mkdir("dj_bot/ffmpeg/")
except FileExistsError as _:
    pass

# Set the download urls

ffmpeg_lin_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
ffmpeg_win_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

print("===== Download and install dependencies =====\n")

# Download the dependencies

print("Download the ffmpeg binary for Linux 64... (It can take few minutes)")
urllib.request.urlretrieve(ffmpeg_lin_url, "./.tmp/fflin.tar.xz", download_hook)
print("Download successful !")

print("Download the ffmpeg binary for Windows 64... (It can take few minutes)")
urllib.request.urlretrieve(ffmpeg_win_url, "./.tmp/ffwin.zip", download_hook)
print("Download successful !")

# Extract and install dependencies

print("Extracting the ffmpeg binary for Linux...")
fflin_tar = tarfile.open(name="./.tmp/fflin.tar.xz")
fflin_tar.extract( fflin_tar.getmember("ffmpeg-4.3.1-amd64-static/ffmpeg"), path="./.tmp/" )
os.rename("./.tmp/ffmpeg-4.3.1-amd64-static/ffmpeg", "./dj_bot/ffmpeg/ffmpeg_linux64")
print("Exctraction successful !")

print("Extracting the ffmpeg binary for Windows...")
ffwin_zip = zipfile.ZipFile("./.tmp/ffwin.zip")
ffwin_zip.extract( "ffmpeg-4.3.1-2020-11-08-essentials_build/bin/ffmpeg.exe", path="./.tmp/" )
os.rename("./.tmp/ffmpeg-4.3.1-2020-11-08-essentials_build/bin/ffmpeg.exe", "./dj_bot/ffmpeg/ffmpeg_win64")
print("Exctraction successful !")

# Clean the temporary directory

print("Cleaning temporary files...")
os.remove("./.tmp/fflin.tar.xz")
os.rmdir("./.tmp/ffmpeg-4.3.1-amd64-static/")
os.remove("./.tmp/ffwin.zip")
os.rmdir("./.tmp/ffmpeg-4.3.1-2020-11-08-essentials_build/bin/")
os.rmdir("./.tmp/ffmpeg-4.3.1-2020-11-08-essentials_build/")
os.rmdir("./.tmp/")
print("Cleaning successful !\n")

# Install the pip dependencies

print("===== Install pip dependencies =====\n")
pip.main(["install", "-r", "requirements.txt"])
print("")

print("===== Installation complete ======")
