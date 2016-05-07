from git import Repo
from uuid import uuid4
import sys
import click

repo = Repo('.')

@click.group()
def cr():
	pass

@cr.command(short_help="Criar uma feature")
@click.argument("title")
@click.option("--branch-name", '-b', default=str(uuid4()), help='Escolha o nome da branch.')
def create(title, branch_name):
	print(title)
	print(branch_name)
	branch_atual = repo.head
	nova_branch = repo.create_head(branch_name)
	branch_atual.reset(commit="origin/master", working_tree=True)
	
	#TODO: salvar title da pull request pra usar quando for mandar pro servidor
	repo.head.reference = nova_branch

if __name__ == '__main__':
	cr()