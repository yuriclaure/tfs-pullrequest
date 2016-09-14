import click
from utils import Utils

class Alert:

	@staticmethod
	def show_if(condition, message):
		if condition:
			Alert.show(message)

	@staticmethod
	def show(message):
		Utils.print_encoded("\n" + click.style("Alert: ", bold=True, fg='yellow') + click.style(message, bold=True) + "\n")
