# -*- coding: utf-8 -*-
"""doobalueva.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GBGQhT4gl1W5UyVSzG09WYW5Mh39VHxm

### Задача
Написать код, который сможет
1. Получить текст последних 20 постов с стены какого-то сообщества вк
* у каждого поста есть id, записывайте его куда-нибудь
* сохранить текст каждого поста в текстовый документ в папке, название которой совпадает с именем сообщества
2. После этого получить текст комментов к каждому посту
* сохранить текст каждого коммента по пути `id_поста/id_коммента.txt`
3. Сложить всё это в в архив и отправить вам в телеграме.

### Решение

Импортируем нужные модули и создаем переменную с токеном
"""

import requests
import os
import zipfile

TOKEN = "ТУТ ДОЛЖЕН БЫТЬ ТОКЕН"

"""Скачиваем модуль telegram-send и настраиваем"""

!pip install telegram-send
!telegram-send --config channel.conf --configure-channel

"""Вводим короткое имя сообщества, например, sysblok:"""

group_name=input()

"""Начинается самое интересное."""

#Сначала создадим функцию для записи какого-либо текста в какой-либо текстовый файл
def write_text(root,text): 
    text_file=open(root, 'w', encoding='utf-8')
    text_file.write(text)
    text_file.close()

#Получаем id сообщества
group_id = requests.get(
    'https://api.vk.com/method/utils.resolveScreenName',
    params={
        "screen_name": group_name,
        "v":"5.92",
        "access_token": TOKEN
    }
).json()["response"]["object_id"]

#Создаем папочку для постов и архив, куда потом будем складывать всё-всё. 
os.makedirs('Системный Блокъ')
zip_archive = zipfile.ZipFile('result.zip', 'w')

#Получаем список постов 
posts = requests.get(
    'https://api.vk.com/method/wall.get',
    params={
        "domain": group_name,
        "v":"5.94",
        "count": 20,
        "access_token": TOKEN
    }
).json()["response"]['items']


#Начинаем получать тексты постов. Проходим по всем постам
for post in posts:
  #Сначала скачиваем сами тексты постов
  write_text('Системный Блокъ/'+str(post['id'])+".txt",post['text'])

  #Теперь занимаемся коментами
  #Создаем объект-список коментов к посту 
  comments = requests.get(
    'https://api.vk.com/method/wall.getComments',
    params={
        "owner_id": -group_id,
        "v":"5.124",
        "post_id":post['id'],
        "thread_items_count":10,
        "access_token": TOKEN
    }
  ).json()['response']['items']

  #Создаем папочку для коментов к конкретному посту
  os.makedirs(str(post['id']))

  #Сохраняем тексты постов
  for comment in comments:
    if comment['thread']['count']==0: #Если у комента нет треда (ответов на комент), просто сохраняем текст комента
      write_text(str(post['id'])+'/'+str(comment['id'])+'.txt',comment['text'])
    else: #А если тред есть, то сначала сохраняем сам комент...
      write_text(str(post['id'])+'/'+str(comment['id'])+'.txt',comment['text'])
      for item in comment['thread']['items']: #...а затем коменты из треда в виде id-комента_id-комента из треда (максимальная длина треда в ВК апи - 10 коментов)
        write_text(str(post['id'])+'/'+str(comment['id'])+'_'+str(item['id'])+'.txt',item['text'])

  #Рекурсивно архивируем все файлы в папочке и саму папочку. Пустые папки тоже архивируем на всякий случай
  for root, dirs, files in os.walk(str(post['id'])):
    if len(files) > 0:
        for f in files:
            zip_archive.write(os.path.join(root, f))
    else:
        zip_archive.write(root)

#Одну папку, название которой мы знаем, можно заархивировать одной строчкой
!zip -r "result.zip" "Системный Блокъ"

#Архив не забываем закрыть
zip_archive.close()

#Отправляем результаты боту
!telegram-send --config channel.conf --file result.zip --caption "Держи архив"
