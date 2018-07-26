#!
import requests as req
import logging as lg
import threading as th


class ChunkHandler(object):

    def __init__(self, url, file, size, chunk_spec, threads):
        """

        :param url: URL to download from
        :type url: str
        :param file: location to store results
        :type file: str
        :param size: Size of file to download
        :type size: float
        :param chunk_spec: Specification for chunking -- has either total chunks or chunk size specified
        :type chunk_spec: dict
        :param threads:
        """
        self.logger = lg.getLogger(__name__)
        self.logger.info("Initializing chunk handler")

        self.url = url
        self.file = file
        self.size = size * 1000000  # Convert to bytes
        self.threads = threads

        # Deconstruct chunk spec
        if chunk_spec["chunk_size"] is not None:
            self.chunk_size = int(chunk_spec["chunk_size"] * 1000000)  # convert to bytes
            self.number_of_chunks = int(self.size // self.chunk_size)
        else:
            self.number_of_chunks = chunk_spec["chunks"]
            self.chunk_size = int(self.size // self.number_of_chunks)

        self.chunks = []
        self.__build_chunks()

        self.logger.debug("Handler initialized, details to follow...")
        self.logger.debug("\t* Downloading from: {0}".format(self.url))
        self.logger.debug("\t* Downloading to: {0}".format(self.file))
        self.logger.debug("\t* Total size of download: {0} bytes".format(self.size))
        self.logger.debug("\t* Total chunks to download: {0}".format(self.number_of_chunks))
        self.logger.debug("\t* Chunk size, in bytes (except last chunk): {0}".format(self.chunk_size))
        self.logger.debug("\t* Last chunk size, in bytes: {0}".format(self.chunks[-1].size))

    def __build_chunks(self):

        # Get chunks needed
        start_byte = 0
        end_byte = self.chunk_size - 1
        while end_byte < self.size:

            self.logger.debug("Adding chunk to download bytes {0} - {1}".format(start_byte, end_byte))
            self.chunks.append(Chunk(self.url, start_byte, end_byte))

            # Byte math...
            start_byte = end_byte + 1
            end_byte = end_byte + self.chunk_size
            if end_byte > self.size:
                end_byte = self.size

    def __get_several_chunks(self, chunks):
        pass

    def run(self):

        # Chunks per thread
        cpt = self.number_of_chunks // self.threads
        chunk_plan = [self.chunks[i:i + cpt] for i in range(0, self.number_of_chunks, cpt)]
        get_several_chunks = lambda ch: [c.get() for c in ch]

        for cp in chunk_plan:
            t = th.Thread(target=get_several_chunks, args=(cp,))
            t.start()
            t.join()

    def write(self):

        with open(self.file, "wb") as f:
            for c in self.chunks:
                f.write(c.content)


class Chunk(object):
    """ Object that gets a chunk of a downloadable file

    """

    def __init__(self, url, start_byte, end_byte):
        """

        :param url: url to download
        :type url: str
        :param get_header: HTTP header
        :type get_header: dict
        :rtype: Getter
        """
        self.logger = lg.getLogger(__name__)

        self.url = url
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.header = {
            "Range": "bytes={0}-{1}".format(start_byte, end_byte)
        }

        # for storing results later
        self.content = None

        # Great success!
        self.logger.debug(
            "Chunk from {0} initialized with start byte = {1}, end byte = {2}".format(
                self.url, self.start_byte, self.end_byte
            )
        )

    @property
    def size(self):
        return self.end_byte - self.start_byte + 1

    def get(self):
        self.logger.debug("Getting chunk, start byte = {0}, end byte = {1}".format(self.start_byte, self.end_byte))
        self.content = req.get(self.url, headers=self.header).content
