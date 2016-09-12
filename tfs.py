import requests
from requests_ntlm import HttpNtlmAuth
import os

class Tfs():

	baseUrl = 'http://tfs.digithobrasil.net:8080/tfs/DigithoBrasil'
	auth = HttpNtlmAuth('DGTBR\\yuriclaure','')

	@staticmethod
	def get_pull_request_status(repository_name, feature_name = 'all'):
		response = requests.get(Tfs.baseUrl + '/_apis/git/repositories/' + settings.repo_id[repository_name] +'/pullRequests?api-version=2.0', auth=Tfs.auth)
		list_of_pull_requests = response.json()["value"]
		pull_request_status = {}
		for pull_request in list_of_pull_requests:
			pull_request_status[pull_request["sourceRefName"].split('/')[-1]] = pull_request["status"]

		if feature_name == 'all':
			return pull_request_status
		else:
			return pull_request_status[feature_name] if feature_name in pull_request_status else None

		#/_apis/git/repositories?api-version=2.0
		#http://tfs.digithobrasil.net:8080/tfs/DigithoBrasil/_apis/projects?api-version=1.0