import logging
from os.path import expanduser
from pathlib import Path


def get_and_increase_number() -> str:
    file_path = Path(expanduser("~") + "/booth/" + 'filename.txt')
    content = file_path.read_text()
    if not content:
        logging.debug("Number file " + str(file_path) + " does not exist")
        content = '0'
    number = int(content) + 1
    logging.info("New number is " + str(number))
    file_path.write_text('%d' % number)
    return str(number)