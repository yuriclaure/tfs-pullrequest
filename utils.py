import sys
import unicodedata
import colorama

class Utils:

	@staticmethod
	def print_encoded(string, nl=True):
		end = "\n" if nl else ""
		if sys.stdout.encoding == "cp1252":
			print(string.encode("UTF-8").decode("ISO-8859-1"), end=end, flush=True)
		else:
			colorama.init()
			print(string, end=end, flush=True)
			colorama.deinit()

	@staticmethod
	def create_feature_name_from_title(string):
		string = string.replace(".", "_").replace("~", "").replace("^", "").replace(":", "_").replace(" ", "_").replace(",", "_").replace("/", "").replace("\\", "")
		nkfd_form = unicodedata.normalize('NFKD', string)
		string_without_accents = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
		return string_without_accents.lower()

	