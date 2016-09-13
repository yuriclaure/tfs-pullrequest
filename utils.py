import os
import click
import sys
import unicodedata

class Utils:

	@staticmethod
	def print_encoded(string):
		if (sys.stdout.encoding == "cp1252"):
			click.echo(string.encode("UTF-8").decode("ISO-8859-1"))
		else:
			click.echo(string)

	@staticmethod
	def create_branch_name_from_title(string):
		nkfd_form = unicodedata.normalize('NFKD', string)
		string_without_accents = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
		return string_without_accents.lower().replace(" ", "_")

	@staticmethod
	def file_exists(filename):
		return os.path.isfile(os.path.dirname(os.path.realpath(__file__)) + "/" + filename)