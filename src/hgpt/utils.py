from urllib.parse import urlparse


def get_clean_hostname(url: str) -> str:
    """
    Get clean hostname (no url parameters, no www,...)

    Parameters
    ----------
    url : str
        Url

    Returns
    -------
    str
        Clean hostname.
    """
    hostname = urlparse(url).hostname

    if hostname is None:
        return urlparse(url).path

    if hostname.startswith("www."):
        return hostname[4:]

    return hostname
