from git import Repo
import click

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
			feature_name = self.checks.current_branch_name()
		print("FINISH FEATURE " + str(feature_name))

	def move_to_feature(self, feature_name):
		self.checks.assert_is_not_dirty()
		self.checks.assert_branch_exists(feature_name)
		print(self.git.checkout(feature_name))

	def review_feature(self, title, hotfix):
		current_branch = self.checks.current_branch_name()
		if (current_branch == "master"):
			self.create_feature(self.checks.convert_to_string_separated_by_underscore(title))
		
		print("REVIEW FEATURE " + str(title) + " ON BRANCH " + self.checks.current_branch_name() + (" AS HOTFIX" if hotfix else ""))

	def share_feature(self):
		current_branch = self.checks.current_branch_name()
		if (current_branch == "master"):
			raise click.UsageError("You cannot push changes on master")
		print(self.git.push("--set-upstream", "origin", current_branch))

	def update_feature(self):
		print(self.git.pull("origin", "master"))

