import click
import random
from uuid import uuid4

#TODO: returns the current feature id
def current_feature_id():
	return 1

#TODO: check occupied ids and return one that is not
def get_next_available_feature_id():
	return random.randint(1, 500)

#TODO: returns wheter the feature_id exists
def feature_id_exists(feature_id):
	return False

def assert_feature_id_does_not_exists(feature_id):
	if feature_id_exists(feature_id):
		raise click.BadParameter('Identificador da feature informado ja pertence a outra feature')

def assert_feature_id_exists(feature_id):
	if not feature_id_exists(feature_id):
		raise click.BadParameter('Identificador da feature nao pode ser encontrado')

def assert_feature_id_does_not_exists_click(ctx, param, value):
	assert_feature_id_does_not_exists(value)
	return value

def assert_feature_id_exists_click(ctx, param, value):
	assert_feature_id_exists(value)
	return value

def list_features(ctx, param, value):
	if not value or ctx.resilient_parsing:
		return
	click.echo('Lista de features')
	ctx.exit()


@click.group()
def cr():
	pass

@cr.command(short_help="Criar uma feature")
@click.argument("title")
@click.option("--list", "-l", is_flag=True, callback=list_features, is_eager=True, expose_value=False, help='Lista as features existentes')
@click.option("--branch-name", '-b', default=str(uuid4()), help='Escolha o nome da branch.')
@click.option("--feature-id", '-f', default=get_next_available_feature_id(), help='Escolha o identificador da feature', type=click.INT, callback=assert_feature_id_does_not_exists_click)
def feature(title, branch_name, feature_id):
	print(title, branch_name, feature_id)
	pass
	#current_branch = repo.head
	#nova_branch = repo.create_head(branch_name)
	#current_branch.reset(commit="origin/master", working_tree=True)
	
	#TODO: salvar title da pull request pra usar quando for mandar pro servidor
	#repo.head.reference = nova_branch

@cr.command(short_help="Finalizar uma feature")
@click.option("--feature_id", '-f', default=current_feature_id(), callback=assert_feature_id_exists_click, type=click.INT, help="Escolha a feature para finalizar")
def finish(feature_id):
	print(feature_id)
	pass

@cr.command(short_help="Mover para uma feature ja iniciada")
@click.argument("feature_id", type=click.INT)
def move(feature_id):
	assert_feature_id_exists(feature_id)
	print(feature_id)
	pass

@cr.command(short_help="Enviar as alteracoes da feature atual criando ou atualizando um pull request")
@click.option('--hotfix', is_flag=True)
def push(hotfix):
	print(hotfix)
	pass