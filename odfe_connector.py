import requests
import yaml
import json 

import traceback
from datetime import datetime

class ODFE_Connector(object):
    """docstring for ODFE_Connector"""
    def __init__(self, face_embedder, secret_odfe_file='secret_region/secret_odfe.yml', index='face-infore-data-cosinesimil', url='https://10.2.50.234:9200/'):
        self.url = url
        self.index = index
        self.face_embedder = face_embedder
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.default_date = '2020-07-31T00:00:00'
        with open(secret_odfe_file, "r") as odfe_f:
            try:
                data = yaml.safe_load(odfe_f)
                self.username = data['username']
                self.password = data['password']
                self.auth = (self.username, self.password)
            except yaml.YAMLError as exc: 
                print(exc)

    def write_file_temp(self, objects, file_location):
        with open ('temporary_save_region/temp.json', 'w') as temp_json_f:
            for obj in objects:
                json.dump(obj, temp_json_f)
                temp_json_f.write('\n')

    # Search similar image by url
    def search_img(self, searching_img_url, size = 5, k=5):
        fe_response = self.face_embedder.internet_embedder(searching_img_url)
        if fe_response['error_message'] != 'no error': return fe_response
        face_vector = fe_response['encoding'][0]

        # Prepare headers to search
        data_query = {
            "size": size,
            "query": {
                "knn": {
                    "face_vector": {
                        "vector": face_vector,
                        "k": k
                    }
                }
            }
        }
        data_query = json.dumps(data_query)
        
        response = requests.post(self.url + self.index + '/_search', headers=self.headers, data=data_query, verify=False, auth=self.auth)
        response = response.json()
        response['error_message'] = 'no error'

        return response


    # Check face_img is already exist
    def check_face_exist(self, img_url):
        response = self.search_img(img_url, size=1, k=1)
        if response['error_message'] != 'no error': return True
        try:
            isExist = True if response['hits']['max_score'] >= 1 else False
        except TypeError as e:
            isExist = False
            traceback.print_exc()

        return isExist

    # Post new face_img to opendistro
    def post_new_face_img(self, img_url, file_location='temporary_save_region/temp.json', captured=False, data_with_face_id=None):
        # Request embedding vector
        if self.check_face_exist(img_url): return {"content": "face has already exist or image not found!"}

        fe_response = self.face_embedder.internet_embedder(img_url)
        if fe_response['error_message'] != 'no error': return fe_response

        roi = fe_response['rois'][0]

        #Write content to json 
        data_index = {
            "index": {
                "_index": self.index
            }
        }
        data = {
            "face_vector": fe_response['encoding'][0],
            "face_id": "ABC",
            "face_name": "Visitor",
            "img_url": img_url,
            "region-of-interest": {
                "conf": roi['conf'],
                "width": roi['wh'][0],
                "height": roi['wh'][1],
                "x": roi['xy'][0],
                "y": roi['xy'][1]
            }
        }
        # Post new data_mode  
        if data_with_face_id: 
            # ID mapping to that person has been found
            try:
                face_id = data_with_face_id['face_id']
                
                url_post = self.url + f'infore-employees/_doc/{face_id}'

                # Get face name from id 
                data_response = requests.get(url_post, verify=False, auth=self.auth)
                data['face_name'] = data_response.json()['_source']['name']
                data['face_id'] = face_id
            # Other case
            except Exception as error:
                pass
                traceback.print_exc()

        # Put datetime if capture else set it to default date
        data['date_captured'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S') if captured else self.default_date

        # Write to file temporerally
        objects = (data_index, data)
        self.write_file_temp(objects, file_location)

        # Put to opendistro for elasticsearch
        data_query = open(file_location, 'rb').read()

        request_url = self.url + self.index + '/_bulk'
        response = requests.post(self.url + self.index + '/_bulk', headers=self.headers, data=data_query, verify=False, auth=self.auth)

        return response

    # Query from employees index to find out name
    def find_name_by_faceid(self, face_id):
        url_post = f'{self.url}infore-employees/_doc/{face_id}'
        names_by_id_response = requests.get(url_post, verify=False, auth=self.auth)
        name_by_id = names_by_id_response.json()['_source']['name']

        return name_by_id
    
    # Labeling face image by face id 
    def labeling_faceid(self, face_id, face_img_id):
        try:
            name_by_id = self.find_name_by_faceid(face_id)
        except Exception as e:
            response = {'content': 'face_id is not exist'}
            traceback.print_exc()
            return response

        # Data to query
        data_query = {
            "script": f"ctx._source.face_id={face_id}; ctx._source.face_name='{name_by_id}'"
        }
        data_query = json.dumps(data_query)

        url_post = self.url + self.index + f'/_update/{face_img_id}'
        response = requests.post(url_post, headers=self.headers,  data=data_query, verify=False, auth=self.auth)

        return response

    # Get distinct faces daily
    def get_counting_data(self):
        params = (
            ('format', 'jdbc'),
        )

        # Data to query
        query_command = f'select date_format(date_captured_utc_time, "yyyy-MM-dd") as dc, count(distinct(face_id)) from {self.index} group by dc'
        data_query = {       
            "query": query_command
        }
        data_query = json.dumps(data_query)

        url_post = self.url + self.index + '/_opendistro/_sql'
        response = requests.post(f'{self.url}_opendistro/_sql', 
                                headers=self.headers, 
                                params=params, 
                                data=data_query, 
                                verify=False, 
                                auth=self.auth)

        return response


        