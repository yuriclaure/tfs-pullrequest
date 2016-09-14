import requests
from requests_ntlm import HttpNtlmAuth
from utils import Utils
from enum import Enum
from error import Error
from alert import Alert
import itertools
import click
import sys
import colorama
from dateutil import parser

class Tfs:

	def __init__(self, settings):
		self.settings = settings

	@staticmethod
	def get_projects(baseUrl, username, password):
		auth = HttpNtlmAuth(username, password)
		return requests.get(baseUrl + '/_apis/git/repositories?api-version=2.0', auth=auth)

	def create_pull_request(self, repository_name, feature_name, title):
		auth = self.__get_auth()
		Error.abort_if(repository_name not in self.settings['repo_id'], "Couldn't find this repository on your TFS")
		fullUrl = self.settings['url'] + "/_apis/git/repositories/" + self.settings['repo_id'][repository_name] + "/pullrequests?api-version=2.0"
		return requests.post(fullUrl, json={"sourceRefName": "refs/heads/" + feature_name, "targetRefName": "refs/heads/master", "title": title}, auth=auth)

	def get_pull_request_details(self, repository_name, features_to_search):
		pull_requests = self.__get_pull_requests(repository_name)
		pull_requests_requested = filter(lambda pull_request: pull_request["sourceRefName"].split("/")[-1] in features_to_search, pull_requests)
		pull_requests_ordered = sorted(pull_requests_requested, key=lambda pr: pr["sourceRefName"])
		pull_requests_grouped = itertools.groupby(pull_requests_ordered, lambda pr: pr["sourceRefName"])
		pull_requests_unique = {key.split("/")[-1] : max(list(group), key=lambda pr: parser.parse(pr["creationDate"])) for key, group in pull_requests_grouped}

		pull_request_details = [self.__assemble_detail(feature_requested, pull_requests_unique) for feature_requested in features_to_search]

		return sorted(pull_request_details, key=lambda prd: (prd[1]["status"].value, prd[0]))

	def has_active_pull_request(self, repository_name, feature_name, baseUrl = None, username = None, password = None):
		baseUrl = self.settings['url'] if baseUrl == None else baseUrl
		auth = self.__get_auth(username, password)
		Error.abort_if(repository_name not in self.settings['repo_id'], "Couldn't find this repository on your TFS")
		fullUrl = baseUrl + '/_apis/git/repositories/' + self.settings['repo_id'][repository_name] + '/pullRequests?api-version=2.0&status=active&sourceRefName=refs/heads/' + feature_name
		return requests.get(fullUrl, auth=auth).json()['count'] > 0

	def __get_pull_requests(self, repository_name, baseUrl = None, username = None, password = None):
		baseUrl = self.settings['url'] if baseUrl == None else baseUrl
		auth = self.__get_auth(username, password)
		if repository_name not in self.settings['repo_id']: 
			Alert.show("Couldn't find this repository on your TFS")
			return []
		active_pull_requests = requests.get(baseUrl + '/_apis/git/repositories/' + self.settings['repo_id'][repository_name] + '/pullRequests?api-version=2.0&status=active', auth=auth).json()['value']
		completed_pull_requests = requests.get(baseUrl + '/_apis/git/repositories/' + self.settings['repo_id'][repository_name] + '/pullRequests?api-version=2.0&status=completed', auth=auth).json()['value']
		abandoned_pull_requests = requests.get(baseUrl + '/_apis/git/repositories/' + self.settings['repo_id'][repository_name] + '/pullRequests?api-version=2.0&status=abandoned', auth=auth).json()['value']
		return active_pull_requests + completed_pull_requests + abandoned_pull_requests

	def __get_auth(self, username = None, password = None):
		username = self.settings['username'] if username == None else username
		password = self.settings['password'] if password == None else password
		return HttpNtlmAuth(username, password)

	def __assemble_detail(self, feature_requested, pull_requests_unique):
		if feature_requested not in pull_requests_unique:
			details = {"status": PullRequestStatus.NOT_CREATED, "title":"(not set)"}
		else:
			details = {"status": PullRequestStatus.create_from(pull_requests_unique[feature_requested]["status"]), "title": pull_requests_unique[feature_requested]["title"]}
		return (feature_requested, details)

class PullRequestStatus(Enum):
	ON_REVIEW = 1
	NOT_CREATED = 2
	COMPLETED = 3
	ABANDONED = 4

	@staticmethod
	def create_from(string):
		if string == "active":
			return PullRequestStatus.ON_REVIEW
		elif string == "abandoned":
			return PullRequestStatus.ABANDONED
		elif string == "completed":
			return PullRequestStatus.COMPLETED
		return None

	def describe(self, bold=False):
		if self.value == 1:
			color = "green"
		elif self.value == 2:
			color = "yellow"
		elif self.value == 3:
			color = "white"
		elif self.value == 4:
			color = "white"
		return click.style("[" + self.name.replace("_", " ") + "]", fg=color, bold=bold)