import click
from utils import Utils
from alert import Alert

class Confirmation:

	@staticmethod
	def show_if(condition, message):
		if condition:
			Confirmation.show(message)

	@staticmethod
	def show(message):
		Alert.show(message)
		click.confirm("Do you want to continue?", abort=True)
