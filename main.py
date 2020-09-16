import requests
from bs4 import BeautifulSoup
import re
import pprint
import os
import time
import genanki




#make this model the way we want it
#go down to the place we will use the model and set that stuff up
lang_aud_model = genanki.Model(
	1839475849,
	'Language Audio Model',
	fields=[
		{'name': 'English'},
		{'name': 'Macedonian'},
		{'name': 'Pronunciation'},
		{'name': 'Audio'},
	],
	templates=[
		{
			'name': 'Card 1',
			'qfmt': '{{English}}',
			'afmt': '{{English}}<hr id="answer">{{Macedonian}}<br>{{Pronunciation}}<br>{{Audio}}',
		},
		{
			'name': 'Card 2',
			'qfmt': '{{Macedonian}}',
			'afmt': '{{Macedonian}}<hr id="answer">{{English}}<br>{{Pronunciation}}<br>{{Audio}}',
		},
		{
			'name': 'Card 3',
			'qfmt': '{{Audio}}',
			'afmt': '{{Audio}}<hr id="answer">{{Macedonian}}<br>{{Pronunciation}}<br>{{English}}',
		}
	])


#this scrapes all the audio and vocab from 
#https://www.goethe-verlag.com/book2/EN/ENMK/ENMK002.HTM

def get_urls():
	urls = []
	for i in range(3,103):
		urls.append('https://www.goethe-verlag.com/book2/EN/ENMK/ENMK'+str(i).zfill(3)+'.HTM')
	return urls

def get_data(url):
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

	return full_collection

def download_and_rename_file(filename,audio_source, tag):
	print('download_and_rename_file',filename, audio_source)
	r = requests.get(audio_source, allow_redirects=True)
	open(filename+'.mp3', 'wb').write(r.content)

def create_anki_notes(item, tag, filename, my_deck, all_audio_files):
	audio_file = filename+'.mp3'
	all_audio_files.append(audio_file)
	my_note = genanki.Note(
		model=lang_aud_model,
		tags=[tag.replace(" ", "")],
		fields=[item[0], item[1], item[2],'[sound:'+audio_file+']'])
	my_deck.add_note(my_note)
	return my_deck, all_audio_files

def scrape_page_into_anki_notes(my_deck, url, all_audio_files):
	full_collection = get_data(url)
	tag = full_collection[1][0]
	for item in full_collection:
		filename = re.sub(r"[,.'`’'|—;:@#?¿!¡<>_\-\"”“&$\[\]\)\(\\\/]+\ *", " ", item[0])
		filename = filename.title()
		filename = filename.replace(' ','')
		audio_source = item[3]
		download_and_rename_file(filename,audio_source,tag)
		my_deck, all_audio_files = create_anki_notes(item, tag, filename, my_deck, all_audio_files)
	return my_deck, all_audio_files

def create_anki_deck(my_deck, all_audio_files):
	my_package = genanki.Package(my_deck)
	my_package.media_files = all_audio_files
	my_package.write_to_file('macedonianBook2.apkg')

def run():
	my_deck = genanki.Deck(round(time.time()),'macedonian vocab book2')
	all_audio_files = []
	urls = get_urls()
	pprint.pprint(urls)
	# urls = ['https://www.goethe-verlag.com/book2/EN/ENMK/ENMK003.HTM']
	for url in urls:
		my_deck, all_audio_files = scrape_page_into_anki_notes(my_deck, url, all_audio_files)
	create_anki_deck(my_deck, all_audio_files)

run()