import json

from configuracoes.parser import parser
from configuracoes.settings_log import logger
from project_libs.backends import search_and_download

# OUTPUT_DIR = "/run/user/1000/gvfs/smb-share:server=192.168.15.20,share=plants-images"
OUTPUT_DIR = r'output'

if __name__ == '__main__':
    # from multiprocessing import Pool
    from pebble import ProcessPool
    
    args = parser.parse_args()

    with open(args.filename, 'r') as file:
        arvore_busca = json.load(file)  

    for categoria in arvore_busca.keys():
        PATH_CTG = args.OUTPUT_DIR + '/' + categoria
        for busca in arvore_busca[categoria]:
            print(f'INICIANDO BUSCA POR {PATH_CTG}-{busca}')
            logger.info(f'INICIANDO BUSCA POR {PATH_CTG}-{busca}')
            search_and_download(search_term=busca, target_path=PATH_CTG, number_images=args.NUMBER_IMAGES, pool=ProcessPool)
