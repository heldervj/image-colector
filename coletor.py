from project_libs.backends import search_and_download
import json

NUMBER_IMAGES = 100
TARGET_PATH = r'D:\plants-images'


with open('house_plants.json', 'r') as file:
    house_plants = json.load(file)

for plant_category in house_plants.keys():
    PATH_CTG = TARGET_PATH + '\\' + plant_category
    for plant in house_plants[plant_category]:
        search_and_download(search_term=plant, target_path=PATH_CTG, number_images=NUMBER_IMAGES)
