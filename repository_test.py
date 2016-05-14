import unittest
import click
from repository import Repository
from unittest.mock import *

class RepositoryTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.git = Mock()
        head1 = Mock()
        head1.name = "name_of_branch1"
        list_of_branches = [head1]
        self.git.heads = list_of_branches
        self.git.heads.master = Mock()
        self.feature_name = "an_awesome_feature"

        self.repository = Repository(self.git)

    def test_that_it_should_fail_when_branch_already_exists(self):
        head1 = Mock()
        head1.name = self.feature_name
        list_of_branches = [head1]
        self.git.heads = list_of_branches

        with self.assertRaises(click.UsageError) as context:
            self.repository.create_feature(self.feature_name)

        self.assertEqual("Branch name an_awesome_feature already assigned to another feature", context.exception.message)

    def test_that_it_should_move_to_master_before_creating_new_branch(self):
        #nao sei como fazer
        pass

    def test_that_it_should_create_new_branch(self):
        self.git.create_head = MagicMock()

        self.repository.create_feature(self.feature_name)

        self.git.create_head.assert_called_with(self.feature_name)


if __name__ == '__main__':
    unittest.main()
