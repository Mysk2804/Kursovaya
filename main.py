from pprint import pprint
import configparser
import requests
from datetime import datetime
import json
from loguru import logger

logger.add("debug.log", format="{time}{message}", level="DEBUG")

config = configparser.ConfigParser()
config.read("YDtoken.ini")
# print(config["Tokens"]["vktoken"])

class VKphotos():
    def __init__(self, token, name, count = 5):
        self.token = token
        self.name = name
        self.count = count

    def _info_vk_profiles(self):
        URL = "https://api.vk.com/method/users.get"
        params = {
            'user_ids': self.name,
            'access_token': self.token,
            'v': '5.131'
        }
        new_url = requests.get(URL, params=params)
        lol = new_url.json()
        # pprint(lol)
        return lol

    def get_vk_photos(self):
        id_profiles = self._info_vk_profiles()
        if id_profiles['response'][0]['is_closed'] == True:
            logger.debug(f"Профиль закрыт")
            return None
        ids = id_profiles['response'][0]['id']
        # print(ids)
        likes_url = {}
        URL = "https://api.vk.com/method/photos.get"
        params = {
            'owner_id': ids,
            'access_token': self.token,
            'v': '5.131',
            'album_id': 'profile',
            'extended': '1'
        }
        new_url = requests.get(URL, params=params)
        lol = new_url.json()
        # pprint(lol)
        for items in lol['response']['items']:
            like_photo = int(items['likes']['count'])
            max_height = 0
            max_heinght_photos = []  # URL Фотографий для скачивания
            item_type = []
            date = datetime.utcfromtimestamp(items['date']).strftime('%Y-%m-%d-%HH-%MM-%SS')
            for size in items['sizes']:
                if int(size['height']) > max_height:
                    max_height = size['height']
                    max_heinght_photos = size['url']
                    item_type = size['type']
                else:
                    pass
            if like_photo in likes_url.keys():
                likes_url[date] = max_height, max_heinght_photos, item_type, date
            else:
                likes_url[like_photo] = max_height, max_heinght_photos, item_type, like_photo
        # pprint(likes_url)
        return likes_url

    def sorted_photo(self):
        i = 0
        list = self.get_vk_photos()
        if list == None:
            # print("Профиль закрыт фотографии не удалось скачать")
            return
        max_height = []
        sort_like_url = {}
        for val in sorted(list.values(), reverse=True):
            if i <= self.count - 1:
                max_height.append(val)
                i += 1
        for item in max_height:
            sort_like_url[item[3]] = item[1], item[2]
        return sort_like_url




class YDphotos():
    def __init__(self, token, json):
        self.token = token
        self.spisok = json
        # pprint(self.spisok)

    def _get_headers(self):
        return {'Content-Type': 'application/json',
                'Authorization': 'OAuth {}'.format(self.token)
                }

    def _upload_pro(self, file):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self._get_headers()
        params = {"path": file, "overwrite": "true"}
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def _new_papka(self):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self._get_headers()
        params = {"path": "Папка загрузки/"}
        pesponse = requests.put(url, headers=headers, params=params)
        return pesponse.json()


    def upload(self):
        if self.spisok == None:
            logger.debug("Профиль закрыт фотографии не удалось скачать")
            return
        else:
            logger.debug("Профиль открыт получаем фотографии")
            upload_query = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            self._new_papka()
            for name, value in self.spisok.items():
                if value[1] == "w":
                    params = {'path': f'Папка загрузки/{name}', 'url': value[0]}
                    requests.post(upload_query, headers=self._get_headers(), params=params)
                    logger.debug(f"Фотография c именем : {name} выгружена на Yandex Disk")
            logger.debug(f"Все фотографии выгружены на Yandex Disk")
            return

def seve_json(text):
    new_json = []
    text_json = text
    for key, val in text_json.items():
        i = {"file_name": key, "size": val[1]}
        new_json.append(i)
    with open("size_json.txt", "w") as file_json:
        json.dump(new_json, file_json)
        logger.debug(f"Файл 'Json' создан на локальном диске")
    pass


if __name__ == '__main__':
    count = int(input('Введите число скачаевыемых фото: '))
    vkphotos = VKphotos(config["Tokens"]["vktoken"], 'the9pasha', count)
    ydphotos = YDphotos(config["Tokens"]["ydtoken"], vkphotos.sorted_photo())
    ydphotos.upload()

