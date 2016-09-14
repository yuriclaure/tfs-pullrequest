import requests
from requests_ntlm import HttpNtlmAuth
from utils import Utils
from enum import Enum
import itertools
import click
import sys
import colorama
from dateutil import parser
if Utils.file_exists("settings.py"):
	import settings

class Tfs:

	@staticmethod
	def create_pull_request(repository_name, feature_name, title):
		auth = Tfs.__get_auth()
		fullUrl = settings.url + "/_apis/git/repositories/" + settings.repo_id[repository_name] + "/pullrequests?api-version=2.0"
		return requests.post(fullUrl, json={"sourceRefName": "refs/heads/" + feature_name, "targetRefName": "refs/heads/master", "title": title}, auth=auth)

	@staticmethod
	def get_pull_request_details(repository_name, features_to_search):
		pull_requests = Tfs.get_pull_requests(repository_name)
		pull_requests_requested = filter(lambda pull_request: pull_request["sourceRefName"].split("/")[-1] in features_to_search, pull_requests)
		pull_requests_ordered = sorted(pull_requests_requested, key=lambda pr: pr["sourceRefName"])
		pull_requests_grouped = itertools.groupby(pull_requests_ordered, lambda pr: pr["sourceRefName"])
		pull_requests_unique = {key.split("/")[-1] : max(list(group), key=lambda pr: parser.parse(pr["creationDate"])) for key, group in pull_requests_grouped}

		pull_request_details = []
		for feature_requested in features_to_search:
			if feature_requested not in pull_requests_unique:
				pull_request_details.append((feature_requested, {"status": PullRequestStatus.NOT_CREATED, "title":""}))
			elif pull_requests_unique[feature_requested]["status"] == "active":
				pull_request_details.append((feature_requested, {"status": PullRequestStatus.ON_REVIEW, "title": pull_requests_unique[feature_requested]["title"]}))
			elif pull_requests_unique[feature_requested]["status"] == "abandoned":
				pull_request_details.append((feature_requested, {"status": PullRequestStatus.ABANDONED, "title": pull_requests_unique[feature_requested]["title"]}))
			elif pull_requests_unique[feature_requested]["status"] == "completed":
				pull_request_details.append((feature_requested, {"status": PullRequestStatus.COMPLETED, "title": pull_requests_unique[feature_requested]["title"]}))

		return sorted(pull_request_details, key=lambda prd: (prd[1]["status"].value, prd[0]))

	@staticmethod
	def get_pull_requests(repository_name, baseUrl = None, username = None, password = None):
		baseUrl = settings.url if baseUrl == None else baseUrl
		auth = Tfs.__get_auth(username, password)
		if repository_name not in settings.repo_id: 
			print('\033[31m' + 'some red text')
			print('\033[0m')
			print(click.style("ALERT: Couldn't find this repository on your TFS\n", fg='red'))
			return []
		active_pull_requests = requests.get(baseUrl + '/_apis/git/repositories/' + settings.repo_id[repository_name] + '/pullRequests?api-version=2.0&status=active', auth=auth).json()['value']
		completed_pull_requests = requests.get(baseUrl + '/_apis/git/repositories/' + settings.repo_id[repository_name] + '/pullRequests?api-version=2.0&status=completed', auth=auth).json()['value']
		abandoned_pull_requests = requests.get(baseUrl + '/_apis/git/repositories/' + settings.repo_id[repository_name] + '/pullRequests?api-version=2.0&status=abandoned', auth=auth).json()['value']
		return active_pull_requests + completed_pull_requests + abandoned_pull_requests

	@staticmethod
	def get_projects(baseUrl = None, username = None, password = None):
		baseUrl = settings.url if baseUrl == None else baseUrl
		auth = Tfs.__get_auth(username, password)
		return requests.get(baseUrl + '/_apis/git/repositories?api-version=2.0', auth=auth)

	@staticmethod
	def __get_auth(username = None, password = None):
		username = settings.username if username == None else username
		password = settings.password if password == None else password
		return HttpNtlmAuth(username, password)


class PullRequestStatus(Enum):
	ON_REVIEW = 1
	NOT_CREATED = 2
	COMPLETED = 3
	ABANDONED = 4

	def describe(self):
		return self.name.replace("_", " ")