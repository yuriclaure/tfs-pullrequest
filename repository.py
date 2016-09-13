import click
from git import Repo
from utils import Utils
from tfs import *
from tabulate import tabulate

class Repository:

	def __init__(self, repo, checks):
		self.repo = repo
		self.git = repo.git
		self.checks = checks

	def create_feature(self, feature_name):
		self.checks.assert_is_not_dirty()
		self.checks.assert_branch_does_not_exists(feature_name)
		self.git.checkout("-B", feature_name, "master")
		self.git.checkout("master")
		self.repo.head.reset(commit="origin/master", working_tree=True)
		self.git.checkout(feature_name)

		click.echo("New feature created successfully")

	def list_features(self):
		features = [head.name for head in filter(lambda h: h.name != "master", self.repo.heads)]
		pull_request_details = Tfs.get_pull_request_details(self.checks.current_repo_name(), features)

		table_of_features = [["[" + pr_detail[1]["status"].describe() + "]", pr_detail[0], pr_detail[1]["title"]] for pr_detail in pull_request_details]

		Utils.print_encoded(tabulate(table_of_features, headers=["Status", "Branch", "Pull request title"]))		

	def finish_feature(self, feature_name):
		# Deletar a branch no local
		# Deve verificar se a branch foi submetida ao servidor, se não, deve alertar o usuário e pedir confirmacao
		if not feature_name: 
			feature_name = self.checks.current_branch_name()
		print("FINISH FEATURE " + str(feature_name))

	def move_to_feature(self, feature_name):
		self.checks.assert_is_not_dirty()
		self.checks.assert_branch_exists(feature_name)
		click.echo(self.git.checkout(feature_name))

	def review_feature(self, title, hotfix):
		current_branch = self.checks.current_branch_name()
		if current_branch == "master":
			current_branch = Utils.create_branch_name_from_title(title)
			self.create_feature(current_branch)

		self.share_feature(silent=True)
		pull_request_details = Tfs.get_pull_request_details(self.checks.current_repo_name(), [current_branch])
		if pull_request_details[0][1]["status"] != PullRequestStatus.ON_REVIEW:
			response = Tfs.create_pull_request(self.checks.current_repo_name(), current_branch, title)
			if response.status_code == 201:
				click.echo("Pull request successfully created")
			else:
				raise click.ClickException("Request error - HTTP_CODE: " + str(response.status_code) + "\n\n" + response.json()["message"])
		else:
			click.echo("Pull request successfully updated")

	def share_feature(self, silent=False):
		current_branch = self.checks.current_branch_name()
		if current_branch == "master":
			raise click.UsageError("You cannot push changes on master")
		output = self.git.push("--set-upstream", "origin", current_branch)
		if not silent:
			click.echo(output)

	def update_feature(self, silent=False):
		output = self.git.pull("origin", "master")
		if not silent:
			click.echo(output)

