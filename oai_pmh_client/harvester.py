import re
from typing import Callable, Dict, Optional

import requests

namespaces : Dict[str,str] = {
    "oai-pmh": "http://www.openarchives.org/OAI/2.0/",
    "ead": "urn:isbn:1-931666-22-9",
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace" }

p = re.compile("<resumptionToken>(.*)</resumptionToken>")

def extract_resumption_token(s: str) -> Optional[str]:
    match = re.search(p, s)
    if match:
        return match.group(1)
    else:
        return None

class HttpBadResponse(Exception):

    def __init__(self, status_code: str) -> None:
        Exception.__init__(self, f"Bad HTTP response: {status_code}")


class Harvester:


    def __init__(self, repository_url: str) -> None:
        self._repository_url: str = repository_url

    def extract_all(self, callback: Callable[[str], bool]) -> None:
        exhausted: bool = False
        resumption_token: Optional[str] = None
        while not exhausted:
            url: str = f"{self._repository_url}?verb=ListRecords"
            if resumption_token is None:
                url += "&metadataPrefix=oai_ead&set=collection"
            else:
                url += f"&resumptionToken={resumption_token}"
            r = requests.get(url)
            if r.status_code != 200:
                raise HttpBadResponse(r.status_code)
            resumption_token = extract_resumption_token(r.text)
            stop_requested: bool = callback(r.text) == False
            if stop_requested or resumption_token is None:
                exhausted = True

