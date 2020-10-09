from selenium import webdriver
import json

cd = webdriver.Chrome()

cd.get('https://www.houseplantsexpert.com/a-z-list-of-house-plants.html')
dicionario_plantas = {'flower': [], 'foliage': [], 'succulent': []}

i = 1
while True:
    try:
        planta = cd.find_element_by_xpath('//*[@id="demoOne1"]/li[{}]/a'.format(i)).get_attribute('innerHTML')
        plnata = planta.lstrip().rstrip()
        dicionario_plantas['flower'].append(planta)
        i += 1
    except:
        break

i = 1
while True:
    try:
        planta = cd.find_element_by_xpath('//*[@id="demoOne2"]/li[{}]/a'.format(i)).get_attribute('innerHTML')
        plnata = planta.lstrip().rstrip()
        dicionario_plantas['foliage'].append(planta)
        i += 1
    except:
        break

i = 1
while True:
    try:
        planta = cd.find_element_by_xpath('//*[@id="demoOne3"]/li[{}]/a'.format(i)).get_attribute('innerHTML')
        plnata = planta.lstrip().rstrip()
        dicionario_plantas['succulent'].append(planta)
        i += 1
    except:
        break

with open('house_plants.json', 'w') as outfile:
    json.dump(dicionario_plantas, outfile)

cd.close()
