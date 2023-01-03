import json

from seleniumwire.request import Response
from seleniumwire.utils import decode


def decode_json_response(response: Response) -> dict:
    byte_decoded = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
    string_decoded = byte_decoded.decode("utf8")
    unparsed_tweets = json.loads(string_decoded)
    return unparsed_tweets
