from yledl.yledl import main as yledl_main
import mock
import json
import logging
import requests
import re
import os
import shlex

BASE_URL = "https://areena.yle.fi/"
YLEDL_PARAMS = os.getenv("YLEDL_PARAMS", "--destdir storage")
logger = logging.getLogger(__name__)


def get_program_id_and_url(url_or_program_id):
    if url_or_program_id.startswith(BASE_URL):
        program_id = url_or_program_id.split("/")[-1]
        url = url_or_program_id
    else:
        program_id = url_or_program_id
        url = BASE_URL + program_id
    return (program_id, url)


def yledl_metadata(url):
    """Use yle-dl to retrieve metadata about the series."""
    metadata = None

    def steal_json(lines):
        nonlocal metadata
        logger.debug("Stealing json")
        metadata = json.loads(lines)

    with mock.patch("yledl.yledl.print_enc", steal_json):
        args = [""]
        args += shlex.split(YLEDL_PARAMS)
        args += ["--showmetadata", url]
        yledl_main(args)

    return metadata


def yledl_download(url: str) -> bool:
    """Use yle-dl to download the episode."""
    assert url.startswith(BASE_URL)
    logger.info(f"Downloading {url}")
    args = [""]
    args += shlex.split(YLEDL_PARAMS)
    args += [url]
    logger.debug(f"yledl parameters: {args}")
    rc = yledl_main(args)
    logger.info(f"Return value: {rc}")
    return rc == 0


def get_title(url):
    r = requests.get(url)
    r.raise_for_status()
    data = r.text
    k = re.search('meta property="og:title" content="(.*?)"', data)
    return k.group(1)
