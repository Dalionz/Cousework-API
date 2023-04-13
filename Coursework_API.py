import requests
import datetime
from tqdm import tqdm
import time




with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()


class VKUserPhotos:

    URL = 'https://api.vk.com/method/photos.get'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photo(self, owner_id, album_id, extended, count):
        """
        Функция для получения json-файла с информацией о фотографиях
        """
        params_get_photo = {
            'owner_id': owner_id,
            'album_id': album_id,
            'extended': extended,
            'count': count
        }
        res = requests.get(self.URL, params={**self.params, **params_get_photo}).json()
        return res['response']['items']

    def json_for_saved(self, res):
        """
        Функция создает новый словарь, с необходимой нам информацией о фотографиях
        """
        final_json = []
        for i in res:
            my_dict = {}
            for j in i['sizes']:
                if j == i['sizes'][-1]:
                    my_dict['date'] = i['date']
                    my_dict['name'] = f'{i["likes"]["count"]}.jpg'
                    my_dict['url'] = j['url']
                    my_dict['size'] = j['type']
            final_json.append(my_dict)

        return final_json

    def creat_file(self, file, json_file):
        '''
        Функция создает папку на ПК с информацией по скаченным фотографиям
        '''
        self.file = file
        self.json_file = json_file
        with open(f'{self.file}.txt', 'wt') as f:
            f.write(str(json_file))


class YandexDiskUser:

    def __init__(self, token, folder):
        self.token = token
        self.ya_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
        self.folder = folder

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def creat_folder(self):
        URL = 'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = self.get_headers()
        params = {'path': self.folder}
        result = requests.put(URL, params=params, headers=headers).json()


    def get_list_namefiles(self):
        """
        Функция возвращает нам список с названиями файлов, которые уже есть на Яндекс диске
        """
        URL = 'https://cloud-api.yandex.net/v1/disk/resources/files/'
        headers = self.get_headers()
        params = {'path': self.folder}
        list_name = []
        result = requests.get(URL, params=params, headers=headers).json()
        for i in result['items']:
            list_name.append(i['name'])
        return list_name

    def upload_file(self, json_list):
        """
        Функция загружает на ЯД фотографии по URL из полученного json-файла
        показывает прогресс загрузки фотографий на ЯД
        """
        replace = False
        headers = self.get_headers()
        for i in tqdm(json_list):
            list_name = self.get_list_namefiles()
            name_photo = i['name']
            if name_photo in list_name:
                timestamp = i['date']
                value = datetime.datetime.fromtimestamp(timestamp)
                value.strftime('%Y-%m-%d%H.%M.%S')
                value = str(value)
                value = value[0:11]
                i['name'] = f'{value}{i["name"]}'
                params = {
                    'path': f'{self.folder}/{i["name"]}',
                    'url': f'{(i["url"])}',
                    'overwrite': f'{replace}'
                }
                response = requests.post(self.ya_url, params=params, headers=headers)
                time.sleep(3)
            else:
                params = {
                    'path': f'{self.folder}/{i["name"]}',
                    'url': f'{(i["url"])}',
                    'overwrite': f'{replace}'
                }
                response = requests.post(self.ya_url, params=params, headers=headers)
                time.sleep(3)




if __name__ == '__main__':
    vk_client = VKUserPhotos(token, '5.131')
    result = (vk_client.get_photo(
        input('введите id VK: '),
        'profile',
        '1',
        input('Введите количество фотографий для скачивания: ')
    ))
    result = vk_client.json_for_saved(result)
    vk_client.creat_file(input('Введите название файла для сохранения информации: '), result)
    Ynd_disk = YandexDiskUser(input('Введите токен Яндекс Диск: '), input('Введите название папки для фотографий: '))
    Ynd_disk.creat_folder()
    Ynd_disk.upload_file(result)




