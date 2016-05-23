import requests
from requests_ntlm import HttpNtlmAuth

class Tfs():

	@staticmethod
	def call():
		url = 'http://tfs.digithobrasil.net:8080/tfs/DigithoBrasil/Solu%C3%A7%C3%B5es%20em%20Software/_apis/git/repositories?api-version={version}'
		output = requests.get(url, auth=HttpNtlmAuth('DGTBR\\yuriclaure',''))
		print(output.content)

Tfs.call()