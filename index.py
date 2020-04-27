# To use this app:
# 1) Create the folder for the download (the "download folder") - eg "20190217 - My books"
# 2) Visit the HB website and !!inspect!! the page and right-click the opening <html> tag and "copy tag"
# 3) Paste that text into a file and save it !!as index.html!! in the download folder
# 4) Set the folder_name value to the name of the folder, not the full path (eg "20190217 - My Books")
# 5) Let it run

from bs4 import BeautifulSoup
import os
import sys
from urllib.parse import urlparse
from urllib.request import urlretrieve
import requests
import re
import time
from multiprocessing.dummy import Pool as ThreadPool
import itertools


def sanitize_filename(filename):
	for needle in ['\\', '/', ':', '?', '\n', '*', '"', '|']:
		filename = filename.replace(needle, "-")
	return filename


def human_readable_size_to_bytes(size):
	# Accepts "10MB", or "100 GB", etc
	# 2.8 GB, 2.4 MB, 10.8 kB

	units = {'k': 1, 'm': 2, 'g': 3, 't': 4}

	re_size = re.search("^(\\d+\\.?\\d*)\\s*(\\w+)$", size, flags=re.MULTILINE)
	num = float(re_size.group(1))
	unit = re_size.group(2)

	bit_or_byte = 1024 if unit[1].isupper() else 1000  # Is it kB, or kb? (upper = byte, lower = bit)
	converted_bytes = bit_or_byte ** units[unit[0].lower()]

	return num * converted_bytes


def download_book(download_dir, book_name, download_div):
	start_time = time.time()
	# Get the download information
	dl_button = download_div.find("span", class_="js-start-download")
	download_a = dl_button.find("a")
	download_url = download_a['href']
	download_type = download_a.text.strip()

	# Get the file size
	download_size_human = download_div.find("span", class_="mbs").text
	# download_size = human_readable_size_to_bytes(download_size_human)
	h = requests.head(download_url).headers
	download_size = int(h.get('content-length', None))

	# Build the file name to save the file
	url_file_name = urlparse(download_url).path
	file_extension = os.path.splitext(url_file_name)[1]
	file_name = book_name
	if download_type == "Supplement":
		file_name += " - Supplement"
	file_name += file_extension
	download_path = os.path.join(download_dir, file_name)

	# Check if the file already exists
	if os.path.isfile(download_path):
		existing_size = os.path.getsize(download_path)
		if existing_size < download_size:  # Humble Bundle seems to have wrong file sizes. So just check filesize to 1%
			print("Replacing existing file (existing: %s, download: %s): %s" % (
				existing_size,
				download_size,
				file_name
			))
			os.remove(download_path)
		else:
			print("Skipping this file, because it already exists: %s -> %s" % (
				file_name,
				download_url
			))
			return False

	# Download the file
	print("Downloading: (%s) %s -> %s" % (download_size_human, file_name, download_path))
	print(download_url)
	urlretrieve(download_url, download_path)
	print("Completed downloading: (%s -> %s) %s" % (
		download_size_human,
		time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time)),
		file_name
	))
	# TODO: Extract the zip to a folder


def main():
	# Setup the download path
	base_download_dir = "D:\\Ebooks\\1 - Humble Bundles"
	if len(sys.argv) > 2: 		# Pull the information from the command line:
		folder_names = [sys.argv[1]]
	else: 						# Hard code the values
		folder_names = [
				# "20170210 - Hacks",
				# "20170831 - Data Science",
				# "20180128 - National Parks by Lonely Planet",
				# "20180212 - Crazy Sexy Love",
				# "20180225 - Functional Programming by OReilly",
				# "20180311 - Code Your Own Games",
				# "20180323 - AI by Packt",
				# "20180323 - DIY Electronics by Wiley",
				# "20180512 - DevOps by Packt",
				# "20180518 - Python Dev Kit",
				# "20180524 - Web Design and Development by OReilly",
				# "20180616 - Pocket Primers by Mercury",
				# "20180629 - Survive Anything by Skyhorse",
				# "20180716 - Virtual Reality by Springer Nature",
				# "20180726 - Linux Geek by No Starch Press",
				# "20180818 - Big Data by Packt",
				# "20180818 - Program Your Own Games by Mercury",
				# "20180901 - Essential Knowledge by MIT Press",
				# "20180906 - Machine Learning by OReilly",
				# "20180906 - UIUX by Wiley",
				# "20180929 - Game Development by Packt",
				# "20180929 - Learn You Some Code by No Starch Press",
				# "20181002 - Head First Series by OReilly",
				# "20181111 - Java by Packt",
				# "20181121 - Big Data & Infographics by Wiley",
				# "20181209 - Cybersecurity by Packt",
				# "20181225 - Hacking for the Holidays by No Starch Press",
				# "20190106 - Professional Photography",
				# "20190106 - STEM by Mercury Learning",
				# "20190114 - Blood, Sweat and New Year's by Callisto",
				# "20190114 - Python 2019 by Packt",
				# "20190201 - Computer Music by MIT Press",
				# "20190216 - Break into the Game Industry by CRC Press",
				# "20190218 - Robotics & IoT by Packt",
				# "20190304 - Computer Science by Mercury Learning",
				# "20190318 - Linux by Wiley",
				# "20190318 - Web Programming by O'Reilly",
				# "20190329 - Coder's Bookshelf by No Starch Press",
				# "20190412 - Blockchain & Cryptocurrency by Packt",
				# "20190412 - Microsoft & .NET by Apress",
				# "20190424 - Max Your Mind by Open Road Media",
				# "20190424 - National Parks Travel Guides 2019 by Lonely Planet",
				# "20190506 - Python by O'Reilly",
				# "20190518 - Artificial Intelligence & Deep Learning by Packt",
				# "20190602 - Computer Graphics by CRC Press",
				# "20190602 - Hacking 2.0 by No Starch Press",
				# "20190620 - Programming by Packt",
				# "20190620 - Summer of Adventure by AdventureKEEN",
				# "20190628 - Jumpstart Your Tech Career by Apress",
				# "20190729 - Data Analysis & Machine Learning",
				# "20190729 - World Foods by Lonely Planet",
				# "20190815 - Build It Yourself by Chronicle Books & Princeton Architectural Press",
				# "20190815 - Coding & App Development by Packt",
				# "20190914 - IT Security by Taylor & Francis",
				# "20190925 - Level Up Your Python",
				# "20191002 - Linux & UNIX by O'Reilly",
				# "20191002 - Network & Security Certification 2.0",
				# "20191014 - Computer Productivity & Coding by Mercury Learning",
				# "20191014 - Developing Your Own Games by Springer",
				# "20191116 - Linux & BSD Bookshelf by No Starch Press",
				# "20191208 - Cybersecurity 2019 by Packt",
				# "20191208 - Data Science by No Starch Press",
				# "20200112 - Python & Machine Learning by Packt",
				# "20200202 - Project Management by Taylor & Francis",
				# "20200301 - User Experience (UX) Design By Morgan & Claypool",
				# "20200308 - Cybersecurity 2020 by Wiley",
				# "20200329 - Land a Tech Job 2.0 by For Dummies",
				# "20200412 - Software Development by O'Reilly",
				"20200427 - Artificial Intelligence & Machine Learning by Morgan & Claypool",
			]

	# Loop through each directory
	for folder_name in folder_names:
		download_dir = os.path.join(base_download_dir, folder_name)
		print("== Downloading book bundle: %s -> %s" % (folder_name, download_dir))

		# Parse the HTML
		with open(os.path.join(download_dir, "index.html"), "r") as html_file:
			html = html_file.read()
		dom = BeautifulSoup(html, "html.parser")

		# Extract the information from the DOM
		books = dom.find_all("div", class_="row")
		for book in books:
			# Get the name and publisher's link to the book
			try:
				publisher_url = book.find("a", class_="afulllink")['href']
				book_name = book.find("div", class_="title").find("a").text
			except TypeError:  # If no publisher URL found
				book_name = book.find("div", class_="title").text

			book_name = sanitize_filename(book_name.strip())

			# Loop through each type of download button (PDF, MOBI, etc)
			download_divs = book.find_all("div", class_="download")
			thread_results = []
			with ThreadPool(2) as thread_pool:
				thread_results = thread_pool.starmap(
					download_book,
					zip(itertools.repeat(download_dir), itertools.repeat(book_name), download_divs)
				)
			thread_pool.close()
			thread_pool.join()

			#for download_div in download_divs:
				#download_books(download_dir, book_name, download_div)

			# TODO: Save JSON of information about the bundle (publisher URL, book name, etc)


if __name__ == '__main__':
	total_start_time = time.time()
	main()
	print("Done downloading everything: %s" % time.strftime('%H:%M:%S', time.gmtime(time.time() - total_start_time)))