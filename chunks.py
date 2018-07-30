#!
from decimal import Decimal
import requests as req
import logging as lg
import threading as th


class ChunkHandler(object):

    def __init__(self, url, file, size, chunk_spec, threads):
        """ A class to handle all the chunks

        Chunks are built under the following guidelines:
            * If the number of chunks is specified, the file is split as evenly as possible across the chunks. If the
                file size cannot be divided equally, one chunk may have a different size. For example, if the target
                file size is 1,000,001 bytes, and 2 chunks are specified, the first chunk will be 500,000 bytes, and
                the second chunk will be 500,001 bytes.
            * If the chunk size is specified, the file is split into equally sized chunks. If the file cannot be split
                equally across chunks, an additional chunk is added with the remainter. For example, if the target
                file size is 1,000,001 bytes, and the chunk size is specified as 500,000 bytes, the file will be downloaded
                in three chunks -- two will have size 500,000 bytes, and the third will have size 1 byte.

        :param url: URL to download from
        :type url: str
        :param file: location to store results
        :type file: str
        :param size: Size of file to download
        :type size: float
        :param chunk_spec: Specification for chunking -- has either total chunks or chunk size specified
        :type chunk_spec: dict
        :param threads: Total number of threads to use in download
        :type threads: int
        """
        self.logger = lg.getLogger(__name__)
        self.logger.info("Initializing chunk handler")

        self.url = url
        self.file = file
        self.size = round(Decimal(size * 1000000))  # Convert to bytes...gotta love floating point arithmetic
        self.threads = threads

        # For handling odd numbers
        self.chunk_correction = None

        # Deconstruct chunk spec
        if chunk_spec["chunk_size"] is not None:
            self.chunk_size = round(Decimal(chunk_spec["chunk_size"] * 1000000))  # convert to bytes
            self.number_of_chunks = self.size // self.chunk_size
            if self.size % self.chunk_size:
                self.number_of_chunks += 1
        else:
            self.number_of_chunks = chunk_spec["chunks"]
            self.chunk_size = round(Decimal(self.size // self.number_of_chunks))

        self.chunks = []
        self.__build_chunks()

        self.logger.info("Handler initialized...")
        self.logger.debug("\t* Downloading from: {0}".format(self.url))
        self.logger.debug("\t* Downloading to: {0}".format(self.file))
        self.logger.debug("\t* Total size of download: {0} bytes".format(self.size))
        self.logger.debug("\t* Total chunks to download: {0}".format(self.number_of_chunks))
        self.logger.debug("\t* Chunk size, in bytes (except last chunk): {0}".format(self.chunk_size))
        self.logger.debug("\t* Last chunk size, in bytes: {0}".format(self.chunks[-1].size))

    def __build_chunks(self):
        """ Initialize chunks. Should only be called in constructor. """

        # Get chunks needed
        start_byte = 0
        end_byte = self.chunk_size - 1
        for i in range(self.number_of_chunks):

            self.logger.debug("Adding chunk to download bytes {0} - {1}".format(start_byte, end_byte))
            self.chunks.append(Chunk(self.url, start_byte, end_byte))

            # Byte math...
            start_byte = end_byte + 1
            end_byte = end_byte + self.chunk_size

            # Before last time through
            if i == self.number_of_chunks - 2:
                end_byte = self.size - 1

    def run(self):
        """ Downloads chunks across specified number of threads.

        This function builds a "chunk plan" -- it decides how to split up chunks across threads. Not all threads will
        download the same number of chunks.
        """

        self.logger.info("Downloading chunks...")

        # Chunks per thread
        cpt = self.number_of_chunks // self.threads
        chunk_plan = [self.chunks[i:i + cpt] for i in range(0, self.threads, cpt)]

        # Some chunks are left over -- distribute these across first few threads
        if self.number_of_chunks % self.threads:
            chunks_already_planned = cpt * self.threads
            for (i, c) in enumerate(range(chunks_already_planned, self.number_of_chunks, 1)):
                chunk_plan[i].append(self.chunks[c])

        for (i, cp) in enumerate(chunk_plan):
            t = th.Thread(target=self.get_several_chunks, args=(cp, i))
            t.start()
            t.join()

        self.logger.info("All chunks successfully downloaded.")

    def get_several_chunks(self, chunks_to_get, thread_name):
        """ Gets a few chunks

        :param chunks_to_get: list of chunks to retreive
        :param thread_name: name of thread
        """
        self.logger.info("Getting {0} chunks on thread {1}. Avg. chunk size = {2}".format(
            len(chunks_to_get)
            , thread_name
            , int(sum(c.size for c in chunks_to_get) / len(chunks_to_get))
        ))
        for chunk in chunks_to_get:
            self.logger.debug("Getting chunk of size {0} on thread {1}".format(chunk.size, thread_name))
            chunk.get()
            self.logger.debug("Chunk of size {0} retrieved on thread {1}".format(chunk.size, thread_name))

    def write(self):
        """ Writes a chunk to file

        TODO: Write chunks to their own file as they're downloaded. This would allow download to resume if it were
        interrupted. Then we'd need a method like construct_final_download_from_parts. As it stands, user will have to
        restart the download from scratch if they lose connectivity. Not an issue for small files.
        """
        self.logger.info("Writing chunks to file {0}".format(self.file))
        with open(self.file, "wb") as f:
            for c in self.chunks:
                f.write(c.content)
        self.logger.info("Chunks successfully written to file.")


class Chunk(object):
    """ A chunk of a downloadable file """

    def __init__(self, url, start_byte, end_byte):
        """ One chunk

        :param url: url to download
        :type url: str
        :param start_byte: byte location to start from
        :type start_byte: int
        :param end_byte: byte location to end (inclusive)
        :type end_byte: int
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
        """ The size of this chunk """
        return self.end_byte - self.start_byte + 1

    def get(self):
        """ GET one chunk """
        self.logger.debug("Getting chunk with start byte = {0} and end byte = {1}".format(self.start_byte, self.end_byte))
        self.content = req.get(self.url, headers=self.header).content
