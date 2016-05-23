from git import Repo
from uuid import uuid4
import click

class Repository:

	def __init__(self, repo):
		self.repo = repo
		self.git = repo.git

	def create_feature(self, feature_name):
		self.__assert_branch_does_not_exists(feature_name)
		self.git.checkout('master')
		self.git.branch(feature_name)
		self.repo.head.reset(commit="origin/master", working_tree=True)
		self.git.checkout(feature_name)
		click.echo("New feature created successfully")

	def list_features(self):
		print("LIST")

	def finish_feature(self, feature_name):
		if not feature_name: 
			feature_name = self.__current_branch_name()
		print("FINISH FEATURE " + str(feature_name))

	def move_to_feature(self, feature_name):
		self.__assert_branch_exists(feature_name)
		print("MOVING TO FEATURE " + str(feature_name))

	def review_feature(self, title, hotfix):
		print("REVIEW FEATURE " + str(title) + " ON BRANCH " + self.__current_branch_name() + (" AS HOTFIX" if hotfix else ""))

	def share_feature(self, feature_name):
		if not feature_name: 
			feature_name = self.__current_branch_name()
		print("SHARE FEATURE " + str(feature_name))

	def update_feature(self, feature_name):
		if not feature_name: 
			feature_name = self.__current_branch_name()
		print("UPDATE FEATURE " + str(feature_name))

	def __assert_branch_does_not_exists(self, value):
		if self.__branch_exists(value):
			raise click.UsageError("Branch name " + value + " already assigned to another feature")
		return value

	def __assert_branch_exists(self, value):
		if not self.__branch_exists(value):
			raise click.UsageError("Couldn't find feature with branch name " + value)
		return value

	def __current_branch_name(self):
		return "master"

	def __branch_exists(self, feature_name):
		for head in self.repo.heads:
			if head.name == feature_name:
				return True
		return False
