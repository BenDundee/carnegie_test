#!

BYTE_LENGTH = 4000000

if __name__ == "__main__":

    with open("./out.jar", "rb") as f:
        correct_file = bytearray(f.read())
    with open("./test.jar", "rb") as f:
        downloaded_file = bytearray(f.read())[:BYTE_LENGTH]

    print(len(correct_file))
    print(len(downloaded_file))
    print(correct_file == downloaded_file)
