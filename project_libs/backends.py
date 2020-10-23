import hashlib
import io
import logging as log
import os
import re
import time
import pickle

import requests
from PIL import Image

log.basicConfig(filename='coletor.log',level=log.DEBUG)

# from project_libs.browsers import ChromeBrowser as webdriver
from selenium import webdriver

from multiprocessing import Pool


def fetch_image_urls(query:str, max_links_to_fetch:int, wd, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, 1000000000);")
        time.sleep(sleep_between_interactions*1)
        
        load_more_button = wd.find_element_by_css_selector(".mye4qd")
        if load_more_button:
            wd.execute_script("document.querySelector('.mye4qd').click();")
            time.sleep(sleep_between_interactions)
            log.info("Buscando novas imagens")


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
            break
        image_count = number_results

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

    return list_links


def parse_source_img(url_to_parse: str):
    res = requests.request("GET", url_to_parse)
    srcs = [m.start() + 5 for m in re.finditer('src="http', str(res.content))]
    return str(res.content)[srcs[0]:srcs[0] + str(res.content)[srcs[0]:].find('"')]

def persist_image(folder_path:str, url_to_parse:str):
    
    try:
        url = parse_source_img(url_to_parse)
    except:
        log.error(url_to_parse)
        return None

    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


def search_and_download(search_term:str, target_path='./images', number_images=5):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    try:
        list_links = pickle.load(open(target_folder + '.pkl', 'rb'))
    except:
        with webdriver.Chrome() as wd:
            list_links = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=1)
    
    with open(target_folder + '.pkl', 'wb') as file:
        pickle.dump(list_links, file)

    with Pool(20) as p:
       p.starmap(persist_image, zip([target_folder for _ in list_links], list_links))
    # for link in list_links:
    #     persist_image(target_folder, link)

