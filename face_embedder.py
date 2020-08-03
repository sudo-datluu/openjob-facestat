import requests
import traceback
from utils import *

class FaceEmbedder(object):
	"""docstring for FaceEmbedder"""
	def __init__(self, url_api='http://10.2.50.234:1611/facenet'):
		self.url_api = url_api

	'''
	r = requests.post("http://localhost:3000/facenet", files={'file': open("./face_api/src/sample.jpg", 'rb')})
	'''
	def local_embedder(self, local_link):
		file_local = open(local_link, 'rb')
		data_parse = {
			'file': file_local
		}
		
		data_res = requests.post(self.url_api, files=data_parse)

		try:
			data_res =  data_res.json()
			data_res['error_message'] = 'no error'
		except Exception as e:
			data_res = {
				"error_message": data_res.content.decode('utf-8')
			}
		
		return data_res

	def internet_embedder(self, img_url_link): 
		r = requests.get(img_url_link, allow_redirects=True)
		filename = get_filename(img_url_link)
		extension_img = get_extension_from_name(filename)

		temp_img_location = 'temporary_save_region/temp.' + extension_img
		open(temp_img_location, 'wb').write(r.content)

		data_res = self.local_embedder(temp_img_location)
		return data_res
