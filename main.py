import requests
from bs4 import BeautifulSoup
import re
import pprint
#this scrapes all the audio and vocab from 
#https://www.goethe-verlag.com/book2/EN/ENMK/ENMK002.HTM

def get_urls():
	urls = []
	for i in range(3,103):
		urls.append('https://www.goethe-verlag.com/book2/EN/ENMK/ENMK'+str(i).zfill(3)+'.HTM')
	return urls

def scrape_page(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	full_collection =[]

	english_header_spans = soup.find_all('span', {'class' : 'Stil36'})
	english_header_text = [span.get_text() for span in english_header_spans]
	english_header_text = [x.replace("\r","") for x in english_header_text]
	english_header_text = [x.replace("\n","") for x in english_header_text]

	english_regular_spans = soup.find_all('div', {'class' : 'Stil35'})
	print(english_regular_spans)
	english_regular_text = [span.get_text() for span in english_regular_spans]
	english_regular_text = [x.replace("\r","") for x in english_regular_text]
	english_regular_text = [x.replace("\n","") for x in english_regular_text]

	macedonian_header_spans = soup.find_all('span', {'class' : 'Stil46'})
	macedonian_header_text = [span.get_text() for span in macedonian_header_spans]
	macedonian_header_text = [x.replace("\r","") for x in macedonian_header_text]
	macedonian_header_text = [x.replace("\n","") for x in macedonian_header_text]

	macedonian_and_pronunciation_regular_spans = soup.find_all('div', {'id': re.compile(r'^hn_')})
	macedonian_and_pronunciation_regular_texts = [span.get_text() for span in macedonian_and_pronunciation_regular_spans]
	macedonian_and_pronunciation_regular_texts = [x.replace("\r","***") for x in macedonian_and_pronunciation_regular_texts]
	macedonian_and_pronunciation_regular_texts = [x.replace("\n","") for x in macedonian_and_pronunciation_regular_texts]

	macedonian_regular_text = []
	pronunciation_regular_text = []
	for item in macedonian_and_pronunciation_regular_texts:
		macedonian_regular_text.append(item.split('***')[0])
		pronunciation_regular_text.append(item.split('***')[1].replace("***",""))

	english_text = english_header_text
	english_text.extend(english_regular_text)

	macedonian_text = macedonian_header_text
	macedonian_text.extend(macedonian_regular_text)

	pronunciation_text = ['','']
	pronunciation_text.extend(pronunciation_regular_text)

	audio_files_lines = soup.find_all(type="audio/mpeg")
	audio_sources = []
	for line in audio_files_lines:
		audio_sources.append(line.get("src"))

	for i in range(0,len(audio_sources)-1):
		new_entry = [
			english_text[i],
			macedonian_text[i],
			pronunciation_text[i],
			audio_sources[i]
			]
		full_collection.append(new_entry)

	pprint.pprint(full_collection)

	tag = full_collection[1][0]

	for item in full_collection:
		filename = re.sub(r"[,.'`’'|—;:@#?¿!¡<>_\-\"”“&$\[\]\)\(\\\/]+\ *", " ", item[0])
		filename = filename.title()
		filename = filename.replace(' ','')
		print(filename)
		#download each file
		#rename it to filename
		#using the downloaded file, create the required notes


def scrape_all_pages():
	# urls = get_urls()
	# pprint.pprint(urls)
	urls = ['https://www.goethe-verlag.com/book2/EN/ENMK/ENMK003.HTM']
	for url in urls:
		scrape_page(url)
scrape_all_pages()
#create a loop that goes through the entire site
#create deck

#create a miscScraper github 

#figure out desired card layout
#	maybe 3 sided, english, macedonian, pronunciation on their own front
#		with the other 2 and audio on the back
#figure out how to put audio in with genanki
#scrape everything
