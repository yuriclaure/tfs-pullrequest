import click
import random
import git
import os
from repository_utils import RepositoryUtils
from repository import Repository
from configuration import Configuration
from utils import Utils
from error import Error

pass_repository = click.make_pass_decorator(Repository)

@click.group()
@click.version_option('1.0', prog_name="Code review")
@click.pass_context
def cr(ctx):
	try:
		if (not Utils.file_exists("settings.py")):
			Utils.print_encoded("Please inform your TFS' information\n")
			ctx.invoke(configure, url=click.prompt("Url"), username=click.prompt("Username"), password=click.prompt("Password"))
			ctx.exit()
		repo = git.Repo('.')
		ctx.obj = Repository(repo, RepositoryUtils(repo))
	except git.exc.InvalidGitRepositoryError:
		Error.abort("You're not on a valid git repository")

@cr.command(short_help="List, create, or finish a feature")
@click.argument("feature_name", required=False)
@click.option("--finish", "-f", is_flag=True, help="Finish feature")
@pass_repository
def feature(repository, feature_name, finish):
	if finish:
		repository.finish_feature(feature_name)
	elif feature_name:
		repository.create_feature(feature_name)
	else:
		repository.list_features()

@cr.command(short_help="Move to another feature")
@click.argument("feature_name", type=click.STRING)
@pass_repository
def move(repository, feature_name):
	repository.move_to_feature(feature_name)

@cr.command(short_help="Creates/updates a pull request for feature")
@click.option("--title", "-t")
@click.option('--hotfix', is_flag=True)
@pass_repository
def review(repository, title, hotfix):
	repository.review_feature(title, hotfix)

@cr.command(short_help="Push changes of a feature to server")
@pass_repository
def share(repository):
	repository.share_feature()

@cr.command(short_help="Pull changes from master into feature")
@pass_repository
def update(repository):
	repository.update_feature()

@cr.command(short_help="Edit installation configuration")
@click.option("--url", prompt=True)
@click.option("--username", "-u", prompt=True)
@click.option("--password", "-p", prompt=True)
def configure(url, username, password):
	Configuration.load_from(url, username, password)

if __name__ == '__main__':
	cr()