import logging

PATH_PREFIX = './'

LOG_LEVEL = logging.INFO

def setup_log(filename='coletor.log'):
    logging.basicConfig(filename = (PATH_PREFIX + filename), format= '%(asctime)s %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=LOG_LEVEL)

    return logging

logger = setup_log()
