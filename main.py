import click
import random
from repository import Repository
from git import Repo

def has_pull_request():
	return True

pass_repository = click.make_pass_decorator(Repository)

@click.group()
@click.version_option('1.0', prog_name="Code review")
@click.pass_context
def cr(ctx):
	ctx.obj = Repository(Repo('.'))

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
@click.option("--title", "-t", prompt=not has_pull_request())
@click.option('--hotfix', is_flag=True)
@pass_repository
def review(repository, title, hotfix):
	repository.review_feature(title, hotfix)

@cr.command(short_help="Push changes of a feature to server")
@click.argument("feature_name", required=False)
@pass_repository
def share(repository, feature_name):
	repository.share_feature(feature_name)

@cr.command(short_help="Pull changes from master into feature")
@click.argument("feature_name", required=False)
@pass_repository
def update(repository, feature_name):
	repository.update_feature(feature_name)

if __name__ == '__main__':
	cr()