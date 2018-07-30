This is, literally, a test.

```
bdundee-mac:carnegie_test bdundee$ python multi_get.py --help
usage: multi_get.py [-h] --url URL [--size-limit SIZE_LIMIT]
                    [--verbosity {info,debug}] [--out OUT] [--path PATH]
                    [--threads THREADS]
                    (--chunks CHUNKS | --chunk-size CHUNK_SIZE)

Get a file in multiple chunks

optional arguments:
  -h, --help            show this help message and exit
  --url URL             Target file to download
  --size-limit SIZE_LIMIT
                        Limit on file download size (in MiB)
  --verbosity {info,debug}
                        Because we log properly, not with print statements
  --out OUT             Name of downloaded file
  --path PATH           Path to store downloaded file, if unspecified stores
                        file in this directory
  --threads THREADS     Number of threads to download file across. Must be <=
                        to # of chunks
  --chunks CHUNKS       Number of chunks to break the file into. Not all
                        chunks are guaranteed to be the same size. If
                        specified, it must be >= number of threads.
  --chunk-size CHUNK_SIZE
                        Max size (in MiB) of each chunk, some chunks may be
                        smaller
```
