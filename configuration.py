import requests
from requests_ntlm import HttpNtlmAuth
import os
import click

class Configuration():

	@staticmethod
	def load_from(baseUrl, username, password):

		auth = HttpNtlmAuth("DGTBR\\" + username, password)
		response = requests.get(baseUrl + '/_apis/git/repositories?api-version=2.0', auth=auth)

		while (response.status_code != 200):
			if (response.status_code == 401):
				click.echo("Couldn't authenticate")
				click.echo("Please, inform username and password again\n")

				username = click.prompt("Username")
				password = click.prompt("Password")
			else:
				click.echo("Couldn't reach informed URL")
				click.echo("Please, inform TFS' URL again\n")

				baseUrl = click.prompt("Url (example: http://tfs01:8080/tfs/DefaultCollection/Solucoes)")
			
			auth = HttpNtlmAuth("DGTBR\\" + username, password)
			response = requests.get(baseUrl + '/_apis/git/repositories?api-version=2.0', auth=auth)

		with open(os.path.dirname(os.path.realpath(__file__)) + "/settings.py", 'w') as f:
			f.write("username = '" + username + "'\n")
			f.write("password = '" + password + "'\n\n")

			f.write("repo_id = {}\n")
			for project in response.json()['value']:
				f.write("repo_id['" + project['name'].lower() + "'] = '" + project['id'] + "'\n")