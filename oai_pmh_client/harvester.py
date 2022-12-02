from typing import Callable, Dict, Optional
from xml.etree.ElementTree import Element

from sickle import Sickle
from sickle.iterator import OAIResponseIterator
from sickle.response import OAIResponse

class Harvester:

    def __init__(self, repository_url: str) -> None:
        self._sickle: Sickle = Sickle(repository_url, iterator=OAIResponseIterator)

    def extract_all(self, callback: Callable[[Element], bool], predefined_set: Optional[str] = None) -> None:
        extra_args: Dict[str, Any] = {}
        if predefined_set is not None:
            extra_args["set"] = predefined_set
        for response in self._sickle.ListRecords(metadataPrefix="oai_ead", **extra_args):
            if not callback(response.xml):
                break

