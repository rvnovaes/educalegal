from unicodedata import normalize


def normalize_ascii(txt):
	return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


if __name__ == '__main__':
	from doctest import testmod
	testmod()
