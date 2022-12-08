from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread
import pytest
from oai_pmh_client.harvester import extract_resumption_token, Harvester, HttpBadResponse

BAD_HTTP_RESPONSE: str = """HTTP/1.1 404
Content-Length: 0
"""

class UnhappyHttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        self.wfile.write(BAD_HTTP_RESPONSE.encode())


class HttpServer(Thread):

    def __init__(self, port: int, request_handler_class) -> None:
        self._server = TCPServer(("", port), request_handler_class)
        Thread.__init__(self)

    def run(self):
        self._server.serve_forever()

    def stop(self):
        self._server.shutdown()


def test_extract_resumption_token():
    s: str = "Archives</corpname>\n  </controlaccess>\n <dsc/>\n</record><resumptionToken>eyJtZXRhZGF0YV9wcmVmDgyOH0=</resumptionToken>blahblah"
    assert "eyJtZXRhZGF0YV9wcmVmDgyOH0=" == extract_resumption_token(s)


def test_bad_url() -> None:
    PORT: int = 8091
    server: HttpServer = HttpServer(PORT, UnhappyHttpRequestHandler)
    server.start()
    try:
        with pytest.raises(HttpBadResponse):
            harvester: Harvester = Harvester(f"http://localhost:{str(PORT)}")
            def callback(s: str) -> bool:
                return False
            harvester.extract_all(callback)
    finally:
        server.stop()
        server.join()
