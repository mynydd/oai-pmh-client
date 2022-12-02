from pathlib import Path
from typing import Dict, List
from xml.etree.ElementTree import Element

from lxml import etree

from oai_pmh_client.harvester import Harvester

xpath_namespaces : Dict[str,str] = {
    "oai-pmh": "http://www.openarchives.org/OAI/2.0/",
    "ead": "urn:isbn:1-931666-22-9",
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace" }

def find(e: Element, xpath: str) -> List[Element]:
    return e.findall(xpath, namespaces=xpath_namespaces)

def describes_single_item(resource: Element) -> bool:
    elements: List[Element] = find(resource, "./ead:archdesc")
    assert 1 == len(elements)
    level: str = elements[0].get("level")
    return "item" == level

def record_id(oai_pmh_response_record: Element) -> str:
    elements: List[Element] = find(oai_pmh_response_record, "./oai-pmh:header/oai-pmh:identifier")
    assert 1 == len(elements)
    full_path: str = "".join(elements[0].itertext())
    return full_path[full_path.rfind("/") + 1:]

XPATH_OAI_PMH_RESPONSE_RECORD: str = ".//oai-pmh:record"
XPATH_ASPACE_RESOURCE: str = ".//ead:ead"

EAD_FILE_DIR: str = "./ead_files"

def write_ead_file(ead: Element, resource_id: str) -> None:
    with open(Path(EAD_FILE_DIR, f"{resource_id}.xml"), mode="w", encoding="utf-8") as f:
        f.write(etree.tostring(ead, encoding="unicode", pretty_print=True))

def test_extract_all():
    harvester: Harvester = Harvester("https://archives-qa.bodleian.ox.ac.uk/oai")
    callback_count: int = 0
    def callback(oai_pmh_response: Element) -> bool:
        for record in find(oai_pmh_response, XPATH_OAI_PMH_RESPONSE_RECORD):
            for resource in find(record, XPATH_ASPACE_RESOURCE):
                if describes_single_item(resource):
                    write_ead_file(resource, record_id(record))
        nonlocal callback_count
        callback_count += 1
        return callback_count < 10
    harvester.extract_all(callback, predefined_set="item")
    assert callback_count > 0
