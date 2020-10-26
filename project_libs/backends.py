import hashlib
import io
import os
import pickle
import re
import time
from datetime import datetime, timedelta
from concurrent.futures import TimeoutError

from configuracoes.settings_request import TIMEOUT

import requests
from configuracoes.settings_log import logger
from PIL import Image
# from project_libs.browsers import ChromeBrowser as webdriver
from selenium import webdriver


def fetch_image_urls(query:str, max_links_to_fetch:int, wd, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, 1000000000);")
        time.sleep(sleep_between_interactions*1)
        
        load_more_button = wd.find_element_by_css_selector(".mye4qd")
        if load_more_button:
            wd.execute_script("document.querySelector('.mye4qd').click();")
            time.sleep(sleep_between_interactions)
            logger.info(f"{query}: Buscando novas imagens")

    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_count = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)

        # Caso nao tenha novos resultados na pagina e nao atingimos o limite 
        # De imagens
        if image_count==number_results:
            logger.info(f"{query}: Nao ha mais imagens")
            break
        image_count = number_results
    
    else:
        logger.info(f"{query}: Encontrado {max_links_to_fetch} imagens.")
    
    inicio = datetime.now()
    # Obtemos lista de links com imagens
    list_links = wd.execute_script("""
        function img_find() {
        var imgs = document.querySelectorAll(".wXeWr"), imgSrcs = []; 
        for (var i = 0; i < imgs.length; i++) {
            imgs[i].click()
            imgSrcs.push(imgs[i].href);
        };
        return imgSrcs;
        };
        return img_find();
        """)
    final = datetime.now()

    logger.info(f"{query}: Tempo para selecionar todas as imagens: {(final - inicio).seconds}")
    return list_links


def parse_source_img(url_to_parse: str):
    res = requests.request("GET", url_to_parse, timeout=TIMEOUT)
    srcs = [m.start() + 5 for m in re.finditer('src="http', str(res.content))]
    return str(res.content)[srcs[0]:srcs[0] + str(res.content)[srcs[0]:].find('"')]

def persist_image(folder_path:str, url_to_parse:str):
    try:
        url = parse_source_img(url_to_parse)

        try:
            image_content = requests.get(url, timeout=TIMEOUT).content
        except Exception as error:
            logger.error(f'GET IMG: {url} - erro: {error.__str__()}')

        try:
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert('RGB')
            file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
            with open(file_path, 'wb') as f:
                image.save(f, "JPEG", quality=85)
            logger.info(f"SUCCESS - saved {url} - as {file_path}")
        except Exception as error:
            logger.error(f'SAVE: {url} - erro: {error.__str__()}')

    except Exception as error:
        logger.error(f'DIR: {folder_path}: {url_to_parse} - erro: {error.__str__()}')
    


def search_and_download(search_term:str, target_path='./images', number_images=5, pool = None):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    try:
        list_links = pickle.load(open(target_folder + '.pkl', 'rb'))
        logger.info(f"{search_term}: Encontrado em .pkl")
    except:
        logger.info(f"{search_term}: Iniciando Busca no google")
        with webdriver.Chrome() as wd:
            list_links = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=1)

        logger.info(f"{search_term}: Busca no google finalizada com sucesso")

    with open(target_folder + '.pkl', 'wb') as file:
        pickle.dump(list_links, file)

    logger.info(f"{search_term}: Iniciando armazenamento em HD")
    with pool(40) as p:
        # future = p.map(persist_image, args=tuple(zip([target_folder for _ in list_links], list_links)))

        # iterator = future.result()

        # while True:
        #     try:
        #         result = next(iterator)
        #     except StopIteration:
        #         break
        #     except TimeoutError as error:
        #         print("function took longer than %d seconds" % error.args[1])
        #     except ProcessExpired as error:
        #         print("%s. Exit code: %d" % (error, error.exitcode))
        #     except Exception as error:
        #         print("function raised %s" % error)
        #         print(error.traceback)  # Python's traceback of remote process
        p.starmap(persist_image, zip([target_folder for _ in list_links], list_links))
    
    logger.info(f"{search_term}: Armazenamento em HD finalizado com sucesso")
    # for link in list_links:
    #     persist_image(target_folder, link)
