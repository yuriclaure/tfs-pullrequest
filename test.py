import unittest
from click.testing import CliRunner
from git import Repo
from repository import Repository

class TesteE2E(unittest.TestCase):

	def test_a_pull_request_creation(self):
		pass
		# Estar na branch do com titulo do pull request
		# master estar sem modificação
		# Todos os commits da master foram para a branch atual
		# invocar o tfs para a criação de PR

	@unittest.skip("Not implemented yet")
	def test_that_a_pull_request_is_prohibeted_when_exist_unstaged_modification(self):
		pass



class TestRepository(unittest.TestCase):

	def test_a_feature_creation(self):
		feature_name = "anIncredibleFeature"
		git = Mock()
		git.create_feature = Mock()

		Repository(git).create_feature(feature_name)

		git.create_head.assert_called_with(feature_name)