#!/usr/local/bin/python

from argparse import ArgumentParser
import logging as lg
import os

from chunks import ChunkHandler


verbosity = {
    "info": lg.INFO
    , "debug": lg.DEBUG
}


def run(arguments):
    """ Helper function

    :param arguments: object containing command line args
    :type arguments: ArgumentParser
    """
    _logger = lg.getLogger(__name__)

    # File location -- try to make it work for mac and windows
    loc = os.path.dirname(os.path.realpath(__file__))
    path = arguments.path if arguments.path is not None else loc
    fn = arguments.out
    file_location = os.path.join(path, fn)
    _logger.debug("File will be downloaded to {0}".format(file_location))

    # Check: Cannot specify both chunk and chunk size.
    # Only need to check this case, ArgumentParser ensures at least one is present
    try:
        if arguments.chunk_size is not None:
            assert arguments.chunks is None
    except AssertionError:
        raise Exception("Cannot specify both chunks and chunk-size")

    # Check: Cannot specify more threads than chunks
    if arguments.chunks is not None and arguments.chunks < arguments.threads:
        raise Exception("Number of threads must be less than or equal to number of chunks")

    chunk_spec = {
        "chunk_size": arguments.chunk_size
        , "chunks": arguments.chunks
    }

    handler = ChunkHandler(
        url=arguments.url
        , file=file_location
        , size=arguments.size_limit
        , chunk_spec=chunk_spec
        , threads=arguments.threads
    )

    # Lights...camera...
    handler.run()
    handler.write()


if __name__ == "__main__":

    # Parse CL...
    parser = ArgumentParser(
        description="Get a file in multiple chunks"
    )
    parser.add_argument(
        "--url"
        , type=str
        , default="http://10b74590.bwtest-aws.pravala.com/384MB.jar"
        , required=True
        , help="Target file to download"
    )
    parser.add_argument(
        "--size-limit"
        , type=float
        , default=4.0
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
        "--out"
        , type=str
        , default="out.jar"
        , required=False
        , help="Name of downloaded file"
    )
    parser.add_argument(
        "--path"
        , type=str
        , default=None
        , required=False
        , help="Path to store downloaded file, if unspecified stores file in this directory"
    )
    parser.add_argument(
        "--threads"
        , type=int
        , default=1
        , required=False
        , help="Number of threads to download file across. Mult be <= to # of chunks"
    )

    # Pick one...
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument(
        "--chunks"
        , type=int
        , help="Number of chunks to break the file into. Not all chunks are guaranteed to be the same size"
    )
    grp.add_argument(
        "--chunk-size"
        , type=float
        , help="Max size (in MiB) of each chunk, last chunk may be smaller"
    )

    # Parse!
    args = parser.parse_args()

    # Configure logging
    lg.basicConfig()
    logger = lg.getLogger()
    logger.setLevel(verbosity[args.verbosity])
    logger.handlers = []
    fmt = lg.Formatter("%(asctime)s - %(name)s - %(lineno)d -  %(levelname)s - %(message)s")

    # Set logging level
    strm_hndlr = lg.StreamHandler()
    strm_hndlr.setFormatter(fmt)
    logger.addHandler(strm_hndlr)

    # Run!
    run(args)

