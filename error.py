import click
from utils import Utils

class Error(click.ClickException):

	@staticmethod
	def abort_if(condition, message):
		if condition:
			Error.abort(message)

	@staticmethod
	def abort(message):
		raise Error(message)

	def show(self):
		Utils.print_encoded("\n" + click.style("Error: ", bold=True, fg='red') + click.style(self.message, bold=True))