from urllib.parse import urlparse


def get_base_domain(referring_url):
    """Returns the scheme + base domain from the referring url

    :parameter
    referring_url(string): Url thar referred the interview.
    E.g.:
    https://app.educalegal.com.br/interview/interview?name=debug

    :returns
    string: The scheme and domain without the url
    E.g:
    https://app.educalegal.com.br
    """
    data = urlparse(referring_url)
    return data.scheme + "://" + data.netloc
