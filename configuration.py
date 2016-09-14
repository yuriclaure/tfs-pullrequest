import os
import click
import requests
from tfs import Tfs
from requests_ntlm import HttpNtlmAuth

class Configuration():

	@staticmethod
	def load_from(baseUrl, username, password):
		baseUrl = baseUrl[:-1] if baseUrl.endswith("/") else baseUrl
		response = Tfs.get_projects(baseUrl, username, password)

		while (response.status_code != 200):
			if (response.status_code == 401):
				username, password = Configuration.__prompt_user_info()
			else:
				baseUrl = Configuration.__prompt_tfs_url()
			response = Tfs.get_projects(baseUrl, username, password)

		Configuration.__write_settings_file(baseUrl, username, password, response.json())
		click.echo("\nNew settings loaded successfully")

	@staticmethod
	def __prompt_user_info():
		click.echo("Couldn't authenticate")
		click.echo("Please, inform username and password again\n")

		return click.prompt("Username"), click.prompt("Password")

	@staticmethod
	def __prompt_tfs_url():
		click.echo("Couldn't reach informed URL")
		click.echo("Please, inform TFS' URL again\n")

		return click.prompt("Url (example: http://tfs01:8080/tfs/DefaultCollection/Solucoes)")

	@staticmethod
	def __write_settings_file(url, username, password, json):
		with open(os.path.dirname(os.path.realpath(__file__)) + "/settings.py", 'w') as f:
			f.write("url = '" + url.replace("/" + url.split('/')[-1], "") + "'\n")
			f.write("username = '" + username + "'\n")
			f.write("password = '" + password + "'\n\n")

			f.write("repo_id = {}\n")
			for project in json['value']:
				f.write("repo_id['" + project['name'].lower() + "'] = '" + project['id'] + "'\n")
