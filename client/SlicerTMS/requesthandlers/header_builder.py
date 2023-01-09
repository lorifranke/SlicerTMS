from typing import Union
from tornado.web import RequestHandler


# this is how the original SlicerHTTPServer formats the header, but converted to tornado
# TODO is there something special we have to do for HTTPS?
def header_builder(response_body: Union[bytes, str], content_type: Union[bytes, str], request_handler: RequestHandler):
    if response_body:
        request_handler.set_status(200)
        request_handler.set_header("Access-Control-Allow-Origin", "*")
        request_handler.set_header("Content-Type", content_type)
        request_handler.set_header("Content-Length", len(response_body))
        request_handler.set_header("Cache-Control", "no-cache")
    else:
        request_handler.set_status(404)
