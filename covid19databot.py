#! /usr/bin/env python3
# COVID-19 Data Bot source code

#   Copyright 2020 Wikimedia Foundation
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import pywikibot
import datetime
import requests
import logging
import os
import csv
import io
import json
from pywikibot.specialbots import UploadRobot

WORLD_MAP_TEMPLATE = "File:BlankMap-World.svg"
WORLD_MAP_TEMPLATE_FILE = "BlankMap-World.svg"
WORLD_MAP_DATA_FILE = 'Covid19DataBot-Case-Data-World.svg'

WORLD_CASE_DATA_URL_TEMPLATE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv"

CHUNK_SIZE = 1 << 20

COLOUR_CODES = {
    '1-9': 'e0e0e0',
    '10-99': 'ffc0c0',
    '100-999': 'ee7070',
    '1000-9999': 'c80200',
    '10000-99999': '900000',
    '100000+': '510000'
}

with open('iso-codes.json') as iso_codes_file:
    iso_codes_data = iso_codes_file.read()
    ISO_CODES = json.loads(iso_codes_data)
    iso_codes_file.close()

def main():
    "Main function for the COVID-19 data bot"
    setupLogging()
    updateWorldCaseDataMap()

def setupLogging():
    logging.basicConfig(level=logging.WARN)

def updateWorldCaseDataMap():
    "Update the SVG world case data map on Wikimedia Commons"
    downloadWorldMapTemplate()
    data = downloadWorldCaseData()
    country_data = processWorldCaseData(data)
    createWorldCaseDataMap(country_data)
    uploadWorldCaseDataMap()

def downloadWorldMapTemplate():
    site = pywikibot.Site('commons', 'commons')
    image = pywikibot.FilePage(site, WORLD_MAP_TEMPLATE)
    image.download(WORLD_MAP_TEMPLATE_FILE)

def downloadWorldCaseData():
    today = datetime.date.today()
    today_url = worldCaseDataUrl(today)
    logging.debug(today_url)
    r = requests.get(today_url)
    if r.status_code != 200:
        yesterday = today - datetime.timedelta(1)
        yesterday_url = worldCaseDataUrl(yesterday)
        logging.debug(today_url)
        r = requests.get(yesterday_url)
    if r.status_code != 200:
        raise Exception("No data file for %s or %s" % (today.isoformat(), yesterday.isoformat()))
    return r.text

def processWorldCaseData(data):
    f = io.StringIO(data)
    d = csv.DictReader(f)
    countries = {}
    for row in d:
        iso = nameToISO(row['Country_Region'])
        if iso and len(iso) > 0:
            country = countries.get(iso, {'confirmed': 0, 'deaths': 0, 'recovered': 0})
            country['confirmed'] += int(row['Confirmed'])
            country['deaths'] += int(row['Deaths'])
            country['recovered'] += int(row['Recovered'])
            countries[iso] = country
          
    return countries

def nameToISO(name):
    return ISO_CODES.get(name)

def createWorldCaseDataMap(country_data):
    class_members = createClassMembers(country_data)
    css = classMembersToCSS(class_members)
    injectCSS(css)

def createClassMembers(country_data):
    class_members = {
        '1-9': [],
        '10-99': [],
        '100-999': [],
        '1000-9999': [],
        '10000-99999': [],
        '100000+': []
    }

    for code, data in country_data.items():
        cases = data['confirmed']
        key = code.lower()
        if cases >= 100000:
            class_members['100000+'].append(key)
        elif cases <= 99999 and cases >= 10000:
             class_members['10000-99999'].append(key)
        elif cases <= 9999 and cases >= 1000:
             class_members['1000-9999'].append(key)
        elif cases <= 999 and cases >= 100:
             class_members['100-999'].append(key)
        elif cases <= 99 and cases >= 10:
             class_members['10-99'].append(key)
        elif cases <= 9 and cases >= 1:
             class_members['1-9'].append(key)

    return class_members

def classMembersToCSS(class_members):
    css = ''
    for band, members in class_members.items():
        css += classCSS(band, members)
    return css

def classCSS(band, members):
    colour = COLOUR_CODES[band]
    dotted = map(lambda x: "." + x, members)
    css = ", ".join(dotted) + " {\n    fill:#" + colour + ";\n}\n"
    return css

def injectCSS(css):
    data = None
    with open(WORLD_MAP_TEMPLATE_FILE, 'r') as file:
        data = file.read()
    data = data.replace('</style>', css + '\n</style>')
    with open(WORLD_MAP_DATA_FILE, 'w') as file:
        file.write(data)

def uploadWorldCaseDataMap():
    description = '{{cc0}} COVID-19 case data by country'
    bot = UploadRobot(WORLD_MAP_DATA_FILE, description=description, verifyDescription=False, ignoreWarning=True, always=True)
    bot.run()

def worldCaseDataUrl(date):
    return WORLD_CASE_DATA_URL_TEMPLATE % (date.strftime('%m-%d-%Y'),)

if __name__ == "__main__":
    main()
