import requests
import time
from tqdm import tqdm, tqdm_gui, trange
from datetime import datetime
import json


class V_Kontakte:
    def __init__(self, vk_token, album_id, owner_id):
        self.album_id = album_id
        self.owner_id = owner_id
        self.vk_token = vk_token
        self.photo_url_list = []
        self.file_information_file = []
        self.base_vk_URL = 'https://api.vk.com/method/photos.get'
        self.vk_params = {'owner_id': self.owner_id, 'album_id': self.album_id, 'extended': '1', 'photo_sizes': '1',
                          'access_token': vk_token, 'v': '5.131'}

    def receive_a_request(self):
        "Запрос на получение фото"
        response = requests.get(self.base_vk_URL, params=self.vk_params)
        self.data = response.json()

    def photo_search(self):
        " Создание списка url"
        list_sizes_photo = []
        for respons, item in self.data.items():
            for i in item['items']:
                list_sizes_photo.extend(i['sizes'])
            for sizes in tqdm(list_sizes_photo, leave=False, desc='Photo search: ', bar_format='{desc}{percentage}%'):
                time.sleep(0.001)
                if sizes['type'] == 'z':
                    self.photo_url_list.append(sizes['url'])
            return self.photo_url_list

    def file_information(self):
        "Создание информации по сохраненным фото и преобразование формата даты"
        list_likes = []
        list_date = []
        list_size = []
        some_list_likes = []
        for response, items in self.data.items():
            for items in items['items']:
                list_likes.append(items['likes']['count'])
                unique_likes = set(list_likes)
                d = int(items['date'])
                datetime.fromtimestamp(items['date'])
                data = (datetime.fromtimestamp(items['date']))
                list_date.append(data)
                for size in items['sizes']:
                    if size['type'] == 'z':
                        list_size.append(size['type'])
        for unique in unique_likes:
            count = 0
            for likes, size in zip(list_likes, list_size):
                if unique == likes:
                    count += 1
                    if count > 1 and likes not in some_list_likes:
                        some_list_likes.append(likes)
        for likes, date, size in zip(list_likes, list_date, list_size):
            if likes in some_list_likes:
                dict_file_name = {"file_name": f"{likes}.jpg {date}", "size": size}
            else:
                dict_file_name = {"file_name": f"{likes}.jpg", "size": size}
            self.file_information_file.append(dict_file_name)
        return self.file_information_file


class Yndex_Disk(V_Kontakte):

    def __init__(self, yd_token, album_id, owner_id):
        super().__init__(yd_token, album_id, owner_id)
        self.photo_url_list = []
        self.file_information_file = []
        self.yd_token = yd_token
        self.yd_headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.yd_token}'}
        self.base_vk_URL = 'https://api.vk.com/method/photos.get'
        self.base_yd_url = "https://cloud-api.yandex.net"
        self.vk_params = {'owner_id': self.owner_id, 'album_id': self.album_id, 'extended': '1', 'photo_sizes': '1',
                          'access_token': vk_token, 'v': '5.131'}

    def create_folder(self, yd_path):
        "Создание папки на яндекс диске"
        yd_URL = f"{self.base_yd_url}/v1/disk/resources"
        requests.put(f'{yd_URL}?path={yd_path}', headers=self.yd_headers)

    def upload_to_yd(self, path):
        "Загрузка фото на яндекс диск"
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        for photo in tqdm(self.photo_url_list, desc='Yandex photo upload: '):
            params = {"path": path, "url": photo}
            response = requests.post(upload_url, headers=self.yd_headers, params=params)

    def file_recording_yd(self):
        "Запись файла с информацией по фото"
        with open('File information.json', 'w', newline="") as file:
            json.dump(self.file_information_file, file, indent=2)


if __name__ == '__main__':
    yd_token = ''

    vk_token = ''

    yd = Yndex_Disk(yd_token, input('Enter the album id,profile,saved or wall: '), input('Enter owner id: '))
    yd.receive_a_request()
    yd.photo_search()
    yd.file_information()
    yd.create_folder('backup_folder')
    yd.upload_to_yd('backup_folder/photo')
    yd.file_recording_yd()
   