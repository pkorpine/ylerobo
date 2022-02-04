from yledl.yledl import main as yledl_main
import mock
import json
import logging
import requests
import re

logger = logging.getLogger(__name__)


def yledl_metadata(url):
    """Use yle-dl to retrieve metadata about the series."""
    metadata = None

    def steal_json(lines):
        nonlocal metadata
        logger.debug("Stealing json")
        metadata = json.loads(lines)

    with mock.patch("yledl.yledl.print_enc", steal_json):
        yledl_main(["", "--showmetadata", url])

    return metadata


def yledl_download(url):
    """Use yle-dl to download the episode."""
    logger.info(f"Downloading {url}")
    rc = yledl_main(["", "--destdir", "storage", url])
    logger.info(f"Return value: {rc}")
    return rc == 0


def get_title(url):
    r = requests.get(url)
    r.raise_for_status()
    data = r.text
    k = re.search('meta property="og:title" content="(.*?)"', data)
    return k.group(1)
