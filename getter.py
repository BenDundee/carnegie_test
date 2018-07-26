#!
import requests as req
import logging as lg


class Getter(object):
    """ Object that gets a chunk of a downloadable file

    """

    def __init__(self, url, chunk_size, byte_start, verbosity):
        self.logger = lg.getLogger(__name__)