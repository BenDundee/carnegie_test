#!

from argparse import ArgumentParser
import logging as lg
import os
import threading as th

from getter import Getter


verbosity = {
    "info": lg.INFO
    , "debug": lg.DEBUG
}


def run(arguments):
    """ Helper function that serves as the handler for Getter objects

    :param arguments: object containing command line args
    :type arguments: ArgumentParser
    """
    _logger = lg.getLogger(__name__)

    # File location
    loc = os.path.dirname(os.path.realpath(__file__))
    path = arguments.path if arguments.path is not None else loc
    _logger.debug("File will be downloaded to {0}".format(path))




    pass


if __name__ == "__main__":

    lg.basicConfig()
    logger = lg.getLogger()
    fmt = lg.Formatter("%(asctime)s - %(name)s - %(lineno)d -  %(levelname)s - %(message)s")

    # Parse CL...
    parser = ArgumentParser(
        description="Get a file in multiple chunks"
    )
    parser.add_argument(
        "--url"
        , type=str
        , default="http://10b74590.bwtest-aws.pravala.com/384MB.jar"
        , action="store"
        , required=True
        , help="Target file to download"
    )
    parser.add_argument(
        "--threads"
        , type=int
        , default=1
        , action="store"
        , required=False
        , help="Number of threads to download file across"
    )
    parser.add_argument(
        "--size-limit"
        , type=float
        , default=4.0
        , action="store"
        , required=False
        , help="Limit on file download size (in MiB)"
    )
    parser.add_argument(
        "--verbosity"
        , choices=["info", "debug"]
        , default="info"
        , required=False
        , help="Because we log properly, not with print statements"
    )
    parser.add_argument(
        "--path"
        , type=str
        , default=None
        , action="store"
        , required=False
        , help="Path to store downloaded file, if unspecified stores in this directory"
    )

    # Pick one...
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument(
        "--chunks"
        , type=int
        , action="store"
        , help="Number of chunks to download. If specified, chunks are 1MiB in size"
    )
    grp.add_argument(
        "--chunk-size"
        , type=float
        , action="store"
        , help="Size (in MiB) of each chunk"
    )

    # Parse!
    args = parser.parse_args()

    # Set logging level
    logger.setLevel(verbosity[args.verbosity])

    # Run!
    run(args)

