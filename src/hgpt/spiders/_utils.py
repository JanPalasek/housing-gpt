from urllib.parse import urljoin, urlparse


def ensure_full_url(url, base_domain):
    # Parse the URL to check its components
    parsed_url = urlparse(url)
    # Check if the URL is missing the scheme or domain
    if not parsed_url.scheme or not parsed_url.netloc:
        # Construct the full URL using the base domain
        return urljoin(base_domain, url)
    # Return the URL as is if it's already complete
    return url
