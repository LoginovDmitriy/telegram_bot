import misc
from flask import Flask
from flask import request
from flask import jsonify
import requests
import json
from flask_sslify import SSLify
import re
from bs4 import BeautifulSoup
import lxml
from PIL import ImageOps
from PIL import Image
import os
import shutil
import telebot
# from telebot import types
# from telebot.types import InputMediaPhoto

app = Flask(__name__)
sslify = SSLify(app)
token = misc.token
URL = 'https://api.telegram.org/bot' + token + '/'
bot = telebot.TeleBot(token)
def write_json(data, filename='answer.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def send_message(chat_id, text='bla-bla-bla'):
    url = URL + 'sendMessage'
    answer = {'chat_id':chat_id, 'text':text}
    r = requests.post(url, json=answer)
    return r.json()

def get_html(url):
	r = requests.get(url)
	return r.text

def get_photo(html):
	re_links = []
	ret_links = []
	tt = '1280x960'
	ii = 0
	soup = BeautifulSoup(html, 'lxml')
	html_text = soup.get_text()
	text_galery = html_text.split('''galleries":[{''') #разбили текст страницы на две части. Во второй части остались ссылки на картинки, а в первой ссылки на "похожие квартиры"
	text1=text_galery[1]
	text = text1.split('''"url":''')
	for i in text:
		link = i.split('"}')
		if tt in link[0]:
			fix_link = link[0]
			fix_link = fix_link[1:]
			re_links.append(fix_link)

	for line in re_links:
		print(line)
		url = str(line)
		ii=ii+1
		r = requests.get(url, stream=True)
		try:
			with open('c:\\Py\\project\\photo\\'+str(ii)+'.jpg', 'bw') as f:

				for chunk in r.iter_content(8192):
					f.write(chunk)

			img = Image.open('c:\\Py\\project\\photo\\'+str(ii)+'.jpg')
			border = (0, 60, 0, 0)
			img = ImageOps.crop(img, border)
			img.save('c:\\Py\\project\\photo\\'+str(ii)+'.jpg')
		except OSError:
			print('Error')

def get_data(html):
    soup = BeautifulSoup(html, 'lxml')
    adress = soup.find('p', class_='location__text___bhjoZ').text
    # print(adress)
    info = soup.find('h5', class_='description__title___2N9Wk').text
    # print(info)
    price = soup.find('div', class_='information__price___2Lpc0').text
    mes = adress + '.  ' + info + '. ' + price
    return mes


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        r = request.get_json()
        write_json(r)
        chat_id = r['message']['chat']['id']
        update_id = r['update_id']
        message = r['message']['text']
        if 'https://www.domofond.ru/' in message:

            try:
                send_message(chat_id, get_data(get_html(message)))
            except:
                try:
                    send_message(chat_id, get_data(get_html(message)))
                except:
                    print('Unable to download data')
            try:
                get_photo(get_html(message))
                list = os.listdir('c:\\Py\\project\\photo')
                number_files = len(list)
                media_group = []
                for i in range(number_files-1):
                    # media_group.append(open("C:\\Py\\project\\photo\\"+str(i+1)+".jpg", 'rb'))
                    # bot.send_media_group(chat_id, media_group)
                    photo = open("C:\\Py\\project\\photo\\"+str(i+1)+".jpg", 'rb')
                    bot.send_photo(chat_id, photo)
                photo.close()
            except:
                send_message(chat_id, 'Чет, корявая ссылка!')
            try:
                folder = "C:\\Py\\project\\photo\\"
                shutil.rmtree(folder, ignore_errors=False, onerror=None)
                os.makedirs(folder)
            except:
                print('Oops')
            return '<h1>Working</h1>'

    return  '<h1>Welcome</h1>'



if __name__ == '__main__':
    app.run()
