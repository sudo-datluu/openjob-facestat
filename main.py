from face_embedder import FaceEmbedder as FE 
from odfe_connector import ODFE_Connector 

import json 
import urllib3
import requests

from utils import index_employees, post_new_data
urllib3.disable_warnings()

fe = FE()
oc = ODFE_Connector(fe)

'''Index to employees data'''
# index_employees(fe, oc)

'''Post new labeled data'''
# post_new_data(fe, oc)

def test_search(searching_img_url):
    response = oc.search_img(searching_img_url)
    with open('temporary_save_region/temp_write.json', 'w') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)

# failed_img_test = '10.2.50.231:2810/img/facelog-data/data-nonpublic/29/img_1804.HEIC'

# img_urls = ['http://10.2.50.231:2810/img/Jul-17-2020/1594961892.jpg', 'http://10.2.50.231:2810/img/Jul-17-2020/1594961863.jpg' 'http://10.2.50.231:2810/img/Jul-17-2020/1594961838.jpg']
# for url in img_urls:
#     oc.post_new_face_img(url)


# searching_img_url = 'http://10.2.50.231:2810/img/Jul-17-2020/1594963030.jpg'
# searching_img_url = 'http://10.2.50.231:2810/img/Jul-17-2020/1594961623.jpg'
# test_search(searching_img_url)


# oc_local = ODFE_Connector(fe, url='https://10.2.50.177:9200/')
# face_id = 3 
# img_num = 2
# URL_IMG_SOURCE = 'http://10.2.50.231:2810/img/facelog-data/data-nonpublic'
# data_with_face_id = {
#     'face_id': face_id
# }
# response = oc_local.post_new_face_img(
#     img_url=f'{URL_IMG_SOURCE}/{face_id}/{img_num}.jpg', 
#     data_with_face_id=data_with_face_id
# )