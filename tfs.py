import requests
from requests_ntlm import HttpNtlmAuth
from requests.auth import HTTPBasicAuth
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
	def get_projects(baseUrl, username, password, authMethod):
		auth = HTTPBasicAuth(username, password) if authMethod == "basic" else HttpNtlmAuth(username, password)
		return requests.get(baseUrl + '/_apis/git/repositories?api-version=2.0', auth=auth)

	def create_pull_request(self, repository_name, feature_name, title):
		auth = self.__get_auth()
		Error.abort_if(repository_name not in self.settings['repo_id'], "Couldn't find this repository on your TFS")
		fullUrl = self.settings['url'] + "/_apis/git/repositories/" + self.settings['repo_id'][repository_name] + "/pullrequests?api-version=2.0"
		return requests.post(fullUrl, json={"sourceRefName": "refs/heads/" + feature_name, "targetRefName": "refs/heads/master", "title": title}, auth=auth)

	def approve_pull_request(self, repository_name, feature_name):
		Error.abort_if(repository_name not in self.settings['repo_id'], "Couldn't find this repository on your TFS")
		policies = self.__get_active_policies(repository_name)
		self.__deactivate_policies(policies)
		try:
			self.__wait_for_merge_analysis(repository_name, feature_name)
			pull_request = self.__get_pull_requests(repository_name, feature_name, only_active=True)[0]
			Error.abort_if(pull_request['mergeStatus'] != 'succeeded', "Hotfix couldn't be pushed because conflicts were found")
			self.__delete_reviewers(pull_request)
			auth = self.__get_auth()
			fullUrl = self.settings['url'] + "/_apis/git/repositories/" + self.settings['repo_id'][repository_name] + "/pullrequests/" + str(pull_request['pullRequestId']) + "?api-version=2.0"
			response = requests.patch(fullUrl, json={"status": "completed", "lastMergeSourceCommit": pull_request['lastMergeSourceCommit']}, auth=auth)
			self.__wait_for_merge_analysis(repository_name, feature_name)
		finally:
			self.__activate_policies(policies)

	def get_pull_request_details(self, repository_name, features_to_search):
		pull_requests = self.__get_pull_requests(repository_name)
		pull_requests_requested = filter(lambda pull_request: pull_request["sourceRefName"].split("/")[-1] in features_to_search, pull_requests)
		pull_requests_ordered = sorted(pull_requests_requested, key=lambda pr: pr["sourceRefName"])
		pull_requests_grouped = itertools.groupby(pull_requests_ordered, lambda pr: pr["sourceRefName"])
		pull_requests_unique = {key.split("/")[-1] : max(list(group), key=lambda pr: parser.parse(pr["creationDate"])) for key, group in pull_requests_grouped}

		pull_request_details = [self.__assemble_detail(feature_requested, pull_requests_unique) for feature_requested in features_to_search]

		return sorted(pull_request_details, key=lambda prd: (prd[1]["status"].value, prd[0]))

	def has_active_pull_request(self, repository_name, feature_name):
		Error.abort_if(repository_name not in self.settings['repo_id'], "Couldn't find this repository on your TFS")
		return len(self.__get_pull_requests(repository_name, feature_name, only_active=True)) > 0

	def __get_pull_requests(self, repository_name, feature_name=None, only_active=False):
		if repository_name not in self.settings['repo_id']: 
			Alert.show("Couldn't find this repository on your TFS")
			return []
		auth = self.__get_auth()
		baseUrl = self.settings['url']
		repo_id = self.settings['repo_id'][repository_name]

		feature_filter = '&sourceRefName=refs/heads/' + feature_name if feature_name else ""
		pull_requests = requests.get(baseUrl + '/_apis/git/repositories/' + repo_id + '/pullRequests?api-version=2.0&status=active' + feature_filter, auth=auth).json()['value']
		if not only_active:
			pull_requests = pull_requests + requests.get(baseUrl + '/_apis/git/repositories/' + repo_id + '/pullRequests?api-version=2.0&status=completed' + feature_filter, auth=auth).json()['value']
			pull_requests = pull_requests + requests.get(baseUrl + '/_apis/git/repositories/' + repo_id + '/pullRequests?api-version=2.0&status=abandoned' + feature_filter, auth=auth).json()['value']
		return pull_requests

	def __activate_policies(self, policies):
		auth = self.__get_auth()
		for policy in policies:
			fullUrl = self.settings['url'] + '/' + self.settings['project'] + '/_apis/policy/configurations/' + str(policy['id'])  + '?api-version=2.0'
			requests.put(fullUrl, json={"isEnabled": True, "isBlocking": policy['isBlocking'], "type": policy['type'], "settings": policy['settings']}, auth=auth)

	def __deactivate_policies(self, policies):
		auth = self.__get_auth()
		for policy in policies:
			fullUrl = self.settings['url'] + '/' + self.settings['project'] + '/_apis/policy/configurations/' + str(policy['id'])  + '?api-version=2.0'
			requests.put(fullUrl, json={"isEnabled": False, "isBlocking": policy['isBlocking'], "type": policy['type'], "settings": policy['settings']}, auth=auth)

	def __get_active_policies(self, repository_name):
		Error.abort_if(repository_name not in self.settings['repo_id'], "Couldn't find this repository on your TFS")
		auth = self.__get_auth()
		fullUrl = self.settings['url'] + '/' + self.settings['project'] + '/_apis/policy/configurations?api-version=2.0'

		policies = requests.get(fullUrl, auth=auth).json()['value']
		policies_from_repository = filter(lambda policy: policy["settings"]["scope"][0]["repositoryId"] == self.settings['repo_id'][repository_name], policies)
		
		return list(policies_from_repository)

	def __delete_reviewers(self, pull_request):
		auth = self.__get_auth()
		for reviewer in self.__list_reviewers(pull_request):
			fullUrl = self.settings['url'] + "/_apis/git/repositories/" + pull_request["repository"]["id"] + "/pullrequests/" + str(pull_request['pullRequestId']) + "/reviewers/" + str(reviewer["id"]) + "?api-version=2.0"
			requests.delete(fullUrl, auth=auth)

	def __list_reviewers(self, pull_request):
		auth = self.__get_auth()
		fullUrl = self.settings['url'] + "/_apis/git/repositories/" + pull_request["repository"]["id"] + "/pullrequests/" + str(pull_request['pullRequestId']) + "/reviewers?api-version=2.0"
		return requests.get(fullUrl, auth=auth).json()['value']

	def __wait_for_merge_analysis(self, repository_name, feature_name):
		pull_requests = self.__get_pull_requests(repository_name, feature_name, only_active=True)
		while len(pull_requests) > 0 and pull_requests[0]['mergeStatus'] == "queued": 
			pull_requests = self.__get_pull_requests(repository_name, feature_name, only_active=True)

	def __get_auth(self):
		if self.settings['authMethod'] == "basic":
			return HTTPBasicAuth(self.settings['username'], self.settings['password'])
		else:
			return HttpNtlmAuth(self.settings['username'], self.settings['password'])

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