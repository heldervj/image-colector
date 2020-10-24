"""
Arquivo responsável por armazenar o parse do coletor de Imagens
"""

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-n', '--num-img', type=int, default=1000, dest="NUMBER_IMAGES", help="Numero max de imagens a ser buscada por pesquisa no google")
parser.add_argument('-f', '--file-base', type=str, default="house_plants.json", dest='filename', help="Nome do arquivo json contendo arvore de pesquisa")
parser.add_argument('-o', '--output', type=str, default=r"D:\plants-images'", dest='OUTPUT_DIR', help="Nome do diretorio onde as imagens serão salvas")

