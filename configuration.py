import requests
from requests_ntlm import HttpNtlmAuth
import os

class Configuration():

	@staticmethod
	def load_configurations_from(baseUrl, username, password):

		auth = HttpNtlmAuth("DGTBR\\" + username, password)
		response = requests.get(baseUrl + '/_apis/git/repositories?api-version=2.0', auth=auth)

		with open(os.path.dirname(os.path.realpath(__file__)) + "/settings.py", 'w') as f:
			f.write("repo_id = {}\n")
			for project in response.json()['value']:
				f.write("repo_id['" + project['name'].lower() + "'] = '" + project['id'] + "'\n")