from git import Repo
from uuid import uuid4
import click
from tfs import Tfs
from feature_status import FeatureStatus

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
		for feature_status in self.__get_feature_status():
			print(feature_status)
		# Listar todas as branches, e ver o status dela, que pode ser:
		# 1 - Criada mas nao existe no servidor ainda
		# 2 - Existe no servidor mais ainda nao tem pull request
		# 3 - Pull request em analise
		# 4 - Pull request mergeada

		# Feature	-	Branch status	-	Code review status
		# branch1	-	Only local
		# branch3	-	On remote		-	Reviewing
		# branch2	-	On remote		-	Completed

		print("LIST")

	def finish_feature(self, feature_name):
		# Deletar a branch no local
		# Deve verificar se a branch foi submetida ao servidor, se não, deve alertar o usuário e pedir confirmacao
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

	def __get_feature_status(self):

		fetch_infos = self.repo.remotes[0].fetch()
		fetch_flag = {}
		for fetch_info in fetch_infos:
			status = FeatureStatus.COULDNT_DEFINE
			if (fetch_info.flags % 64) == 0:
				status = FeatureStatus.BEHIND
			elif (fetch_info.flags % 4) == 0:
				status = FeatureStatus.UPTODATE
			elif (fetch_info.flags % 16) == 0:
				status = FeatureStatus.AHEAD
			elif (fetch_info.flags % 2) == 0:
				status = FeatureStatus.LOCAL
			fetch_flag[fetch_info.ref.name.split('/')[-1]] = status
		pull_request_status = Tfs.get_pull_request_status('TesteDoTFSCR')

		print(fetch_flag)

		list_of_feature_status = {}
		for head in self.repo.heads:
			list_of_feature_status[head.name] = dict(branch_status=fetch_flag[head.name], pull_request_status=pull_request_status[head.name])

		return list_of_feature_status