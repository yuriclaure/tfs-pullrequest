from git import Repo
import click

class Checks:

	def __init__(self, repo):
		self.repo = repo
		self.git = repo.git

	def assert_is_not_dirty(self):
		if self.repo.is_dirty():
			raise click.UsageError("You have uncommited changes, please commit or stash them before continuing")

	def assert_branch_does_not_exists(self, branch):
		if self.branch_exists(branch):
			raise click.UsageError("Branch name " + branch + " already assigned to another feature")

	def assert_branch_exists(self, branch):
		if not self.branch_exists(branch):
			raise click.UsageError("Couldn't find feature with branch name " + branch)

	def current_branch_name(self):
		return self.repo.head.ref.name

	def branch_exists(self, branch):
		for head in self.repo.heads:
			if head.name == branch:
				return True
		return False

	def convert_to_string_separated_by_underscore(self, string):
		return string.lower().replace(" ", "_")
