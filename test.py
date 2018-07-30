#!
from decimal import Decimal
import logging as lg
import os

from multi_get import run


URL ="http://10b74590.bwtest-aws.pravala.com/384MB.jar"
OUT_FILE="out.jar"
LOCATION = os.path.dirname(os.path.realpath(__file__))


class Tester(object):

    def __init__(self, test_name, out=OUT_FILE, chunk_size=1.0, chunks=None,
                 threads=1, url=URL, size_limit=4.0, path=LOCATION):
        """ Class that provides CL arguments.

        :param test_name: Name of test
        :param out:
        :param chunk_size:
        :param chunks:
        :param threads:
        :param url:
        :param size_limit:
        :param path:
        """
        self.test_name = test_name
        self.out = out
        self.chunk_size = chunk_size
        self.chunks = chunks
        self.threads = threads
        self.url = url
        self.size_limit = size_limit
        self.path = path

        self.logger = lg.getLogger(__name__)
        self.log_test()

    def log_test(self):

        ln = "=" * 80
        pretty_log = [
            ""
            , ln
            , "Running {0}".format(self.test_name)
            , "\t * chunk_size = {0}".format(self.chunk_size)
            , "\t * chunks = {0}".format(self.chunks)
            , "\t * threads = {0}".format(self.threads)
            , "\t * size_limit = {0}".format(self.size_limit)
            , ln
        ]
        self.logger.info('\n'.join(pretty_log))

    def test_ok(self):
        pretty_log = [
            ""
            , "{0} passed!".format(self.test_name)
            , "=" * 80
            , "=" * 80
            , ""
        ]
        self.logger.info('\n'.join(pretty_log))

    def validate_download(self):
        """ Verifies that the downloaded file is the correct size, and matches correcct file byte for byte

        """
        out = os.path.join(self.path, self.out)
        correct = os.path.join(self.path, "test.jar")

        byte_length = round(Decimal(self.size_limit * 1000000))
        with open(out, "rb") as f:
            downloaded_file = bytearray(f.read())
        with open(correct, "rb") as f:
            correct_file = bytearray(f.read())[:byte_length]

        self.logger.info("The downloaded file length was {0} bytes".format(len(downloaded_file)))
        self.logger.info("The correct file length was {0} bytes".format(len(correct_file)))
        try:
            assert correct_file == downloaded_file
            self.logger.info("The downloaded file matches the correct file byte for byte")
            self.test_ok()
        except AssertionError:
            raise Exception("Error in downloaded file...")


def run_tests():

    _logger = lg.getLogger(__name__)

    if True:
        test_1 = Tester("Test 1: Basic requirements")
        run(test_1)
        test_1.validate_download()

    if True:
        test_2 = Tester("Test 2: Multiple threads", threads=3)
        run(test_2)
        test_2.validate_download()

    if True:
        test_3 = Tester("Test 3: Odd file size", size_limit=4.1, threads=3)
        run(test_3)
        test_3.validate_download()

    if True:
        test_4 = Tester("Test 4: Odd file size, w/ chunks", size_limit=4.1, chunks=7, chunk_size=None, threads=5)
        run(test_4)
        test_4.validate_download()

    if True:
        test_5 = Tester("Test 5: Odd file size, w/ chunks (#2)", size_limit=3.9, chunks=5, chunk_size=None, threads=5)
        run(test_5)
        test_5.validate_download()


if __name__ == "__main__":

    # Configure logging
    lg.basicConfig()
    logger = lg.getLogger()
    logger.setLevel(lg.INFO)
    logger.handlers = []
    fmt = lg.Formatter("%(asctime)s - %(name)s - %(lineno)d -  %(levelname)s - %(message)s")

    # Set logging level
    strm_hndlr = lg.StreamHandler()
    strm_hndlr.setFormatter(fmt)
    logger.addHandler(strm_hndlr)

    logger.info("Running tests...")
    run_tests()
