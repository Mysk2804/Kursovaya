import json
import requests
import os
from loguru import logger

logger.add("debug.log", format="{time}{message}", level="DEBUG")

class VKphotos():
    def __init__(self, vktoken, vkname, ydtoken):
        self.token = vktoken
        self.vkname = vkname
        self.ydtoken = ydtoken

    def _get_photos(self):
        list_json = []
        likes_url = {}
        url = "https://api.vk.com/method/photos.getAll/"
        params = {
            "user_ids": self.vkname,
            "access_token": self.token,
            "v": "5.131",
            "extended": "1"
        }
        res = requests.get(url, params=params)
        lol = res.json()
        # pprint(lol)
        for items in lol['response']['items']:
            like_photo = int(items['likes']['count'])
            max_height = 0
            max_heinght_photos = [] #URL Фотографий для скачивания
            item_type = []
            for size in items['sizes']:
                if int(size['height']) > max_height:
                    max_height = size['height']
                    max_heinght_photos = size['url']
                    item_type = size['type']
                else:
                    pass
            if like_photo in likes_url.keys():
                likes_url[items['date']] = max_heinght_photos, item_type
                list_json.append({"file_name": items['date'], "size": item_type})
            else:
                likes_url[like_photo] = max_heinght_photos, item_type
                list_json.append({"file_name": like_photo, "size": item_type})
        with open("size_json.txt", "w") as file_json:
            json.dump(list_json, file_json)
        return likes_url


    def save_photos(self):
        if not os.path.isdir("Папка загрузки"):
            os.mkdir("Папка загрузки")
        else:
            pass
        item = self._get_photos()
        for name, url in item.items():
            response = requests.get(url[0])
            filename = str(name) + ".jpg"
            new_file = os.path.join(os.getcwd(), "Папка загрузки", filename)
            with open(new_file, "wb") as imgfile:
                imgfile.write(response.content)
                logger.debug(f"Фотография c именем : {filename} скачена на компьютер")


    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.ydtoken)
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


    def upload(self, count_photo = 5):
        i = 0
        file = os.listdir('Папка загрузки')
        self._new_papka()
        files_add = {}
        # print(file)
        for names in file:
            files = os.path.getsize(os.getcwd() + "/Папка загрузки/" + names)
            if files in files_add:
                files_add[files + 1] = names
            else:
                files_add[files] = names
        # print(files_add)
        for size, name in sorted(files_add.items(), reverse=True):
            if i < count_photo:
                i += 1
                text_file = os.path.join(os.getcwd(), 'Папка загрузки', name)
                # print(text_file)
                href = self._upload_pro(file="Папка загрузки/"+name).get("href", "")
                resource = requests.put(href, data=open(text_file, 'rb'))
                resource.raise_for_status()
                logger.debug(f"Фотография c именем : {name} выгружена на Yandex Disk")
        return


if __name__ == "__main__":
    vkname = "begemot_korovin"
    VKtoken = ""
    YDtoken = ""
    foto = VKphotos(VKtoken, vkname, YDtoken)
    count_photo = 7 #количество загружаемых фото на YD
    foto.save_photos()