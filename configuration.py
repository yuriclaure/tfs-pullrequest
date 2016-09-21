import os
import yaml
import click
import requests
from tfs import Tfs
from requests_ntlm import HttpNtlmAuth

class Configuration():
	file_path = os.path.join(click.get_app_dir("Codereview"), "settings.yaml")

	@staticmethod
	def load():
		if not Configuration.exists(): return {}
		stream = open(Configuration.file_path, 'r')
		return yaml.load(stream)

	@staticmethod
	def save_from(baseUrl, username, password):
		baseUrl = baseUrl[:-1] if baseUrl.endswith("/") else baseUrl
		authMethod = "basic" if baseUrl.split('/')[2].endswith("visualstudio.com") else "ntlm"
		response = Tfs.get_projects(baseUrl, username, password, authMethod)

		while (response.status_code != 200):
			if (response.status_code == 401):
				username, password = Configuration.__prompt_user_info()
			else:
				baseUrl = Configuration.__prompt_tfs_url()
			response = Tfs.get_projects(baseUrl, username, password, authMethod)

		Configuration.__write_settings_file(baseUrl, username, password, authMethod, response.json())
		click.echo("\nNew settings loaded successfully")

	@staticmethod
	def exists():
		return os.path.isfile(Configuration.file_path)

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
	def __write_settings_file(url, username, password, authMethod, json):
		data = {}
		data['url'] = url.replace("/" + url.split('/')[-1], "")
		data['project'] = url.split('/')[-1]
		data['authMethod'] = authMethod
		data['username'] = username
		data['password'] = password
		data['repo_id'] = {}
		for project in json['value']:
			data['repo_id'][project['name'].lower()] = project['id']

		if not os.path.exists(click.get_app_dir("Codereview")):
			os.makedirs(click.get_app_dir("Codereview"))
		stream = open(Configuration.file_path, 'w')
		yaml.dump(data, stream)
