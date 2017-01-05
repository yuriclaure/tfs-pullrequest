import click
import sys
import git
from utils import Utils
from error import Error

class RepositoryUtils:

	def __init__(self, repo):
		self.repo = repo
		self.git = repo.git

	def assert_is_not_dirty(self):
		Error.abort_if(self.repo.is_dirty(), "You have uncommited changes, please commit or stash them before continuing")

	def assert_feature_does_not_exists(self, feature):
		Error.abort_if(self.feature_exists(feature), "feature name " + feature + " already assigned to another feature")

	def assert_feature_exists(self, feature):
		Error.abort_if(not self.feature_exists(feature), "Couldn't find feature with feature name " + feature)

	def feature_exists(self, feature):
		for head in self.repo.heads:
			if head.name == feature:
				return True
		return False

	def has_unpushed_commits(self, feature_name):
		try:
			unpushed_commits = self.git.cherry("origin/" + feature_name, feature_name)
			return unpushed_commits != ""
		except git.exc.GitCommandError:
			return True

	def current_feature_name(self):
		return self.repo.head.ref.name

	def current_repo_name(self):
		remoteUrl = self.git.config("remote.origin.url")
		remoteUrl = remoteUrl[:-1] if remoteUrl.endswith("/") else remoteUrl
		return remoteUrl.split("/")[-1].lower()

	def obtain_pull_request_title_from_last_commit(self):
		title = self.repo.head.commit.message[:-1]

		Utils.print_encoded("Pull request title: " + click.style(title, bold=True) + " (obtained from last commit message)")
		Utils.print_encoded("Press (enter) to accept or type new title: ", nl=False)
		new_title = sys.stdin.readline()

		if ord(new_title[0]) == 10:
			return title
		else:
			return new_title[:-1].encode("ISO-8859-1").decode("UTF-8")


