import click
import random
from repository import Repository
import git

def has_pull_request():
	return False

pass_repository = click.make_pass_decorator(Repository)

@click.group()
@click.version_option('1.0', prog_name="Code review")
@click.pass_context
def cr(ctx):
	try:
		ctx.obj = Repository(git.Repo('.'))
	except git.exc.InvalidGitRepositoryError:
		raise click.UsageError("You're not on a valid git repository")

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
@pass_repository
def share(repository):
	repository.share_feature()

@cr.command(short_help="Pull changes from master into feature")
@pass_repository
def update(repository):
	repository.update_feature()

if __name__ == '__main__':
	cr()