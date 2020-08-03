import re
import json 
import requests



def post_new_data(fe, oc, face_id_list=['11', '19', '22', '23', '26', '28', '29', '3', '30', '5', '7', '9', '6', '20', '27', '4', '31']):
    URL_IMG_SOURCE = 'http://10.2.50.231:2810/img/facelog-data/data-nonpublic'
    maximum_img = 40

    for face_id in face_id_list:
        for img_num in range(1, maximum_img):
            data_with_face_id = {
                'face_id': face_id
            }
            oc.post_new_face_img(
                img_url=f'{URL_IMG_SOURCE}/{face_id}/{img_num}.jpg', 
                data_with_face_id=data_with_face_id

            )


def get_filename(url_link):
    return url_link.split('/')[-1]

def get_extension_from_name(filename):
    if not filename:
        return None
    return filename.split(".")[-1]

def index_employees(fe, oc):
    with open('secret_region/employees.json', 'r') as read_file:
        data_employees = json.load(read_file)
    for id_emp, emp_name in enumerate(data_employees['names']):
        data_request = {
            "name": emp_name
        }
        data_request = json.dumps(data_request)
        url_request = f'{oc.url}infore-employees/_doc/{id_emp}'
        response = requests.put(url_request, headers=oc.headers, data=data_request, verify=False, auth=oc.auth)
