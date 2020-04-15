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
from pywikibot.specialbots import UploadRobot

WORLD_MAP_TEMPLATE = "File:BlankMap-World.svg"
WORLD_MAP_TEMPLATE_FILE = "BlankMap-World.svg"
WORLD_MAP_DATA_FILE = 'Covid19DataBot-Case-Data-World.svg'

WORLD_CASE_DATA_URL_TEMPLATE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv"

CHUNK_SIZE = 1 << 20

ISO_CODES = {
    'Afghanistan': 'AF',
    'Albania': 'AL',
    'Algeria': 'DZ', 'Andorra': 'AD',
    'Angola': 'AO',
    'Antigua and Barbuda': 'AG',
    'Argentina': 'AR',
    'Armenia': 'AM',
    'Austria': 'AT',
    'Azerbaijan': 'AZ',
    'Bahamas': 'BS',
    'Bahrain': 'BH',
    'Bangladesh': 'BD',
    'Barbados': 'BB',
    'Belarus': 'BY',
    'Belgium': 'BE',
    'Belize': 'BZ',
    'Benin': 'BJ',
    'Bhutan': 'BT',
    'Bolivia': 'BO',
    'Bosnia and Herzegovina': 'BA',
    'Botswana': 'BW',
    'Brazil': 'BR',
    'Brunei': 'BN',
    'Bulgaria': 'BG',
    'Burkina Faso': 'BF',
    'Burma': 'MM',
    'Burundi': 'BI',
    'Cabo Verde': 'CV',
    'Cambodia': 'KH',
    'Cameroon': 'CM',
    'Central African Republic': 'CF',
    'Chad': 'TD',
    'Chile': 'CL',
    'Colombia': 'CO',
    'Congo (Brazzaville)': 'CG',
    'Congo (Kinshasa)': 'CD',
    'Costa Rica': 'CR', "Cote d'Ivoire": 'CI',
    'Croatia': 'HR',
    'Cuba': 'CU',
    'Cyprus': 'CY',
    'Czechia': 'CZ',
    'Denmark': 'DK',
    'Diamond Princess': '',
    'Djibouti': 'DJ',
    'Dominica': 'DM',
    'Dominican Republic': 'DO',
    'Ecuador': 'EC',
    'Egypt': 'EG',
    'El Salvador': 'SV',
    'Equatorial Guinea': 'GQ',
    'Eritrea': 'ER',
    'Estonia': 'EE',
    'Eswatini': 'SZ',
    'Ethiopia': 'ET',
    'Fiji': 'FJ',
    'Finland': 'FI',
    'France': 'FR',
    'Gabon': 'GA',
    'Gambia': 'GM',
    'Georgia': 'GE',
    'Germany': 'DE',
    'Ghana': 'GH',
    'Greece': 'GR',
    'Grenada': 'GD',
    'Guatemala': 'GT',
    'Guinea': 'GN',
    'Guinea-Bissau': 'GW',
    'Guyana': 'GY',
    'Haiti': 'HT',
    'Holy See': 'VA',
    'Honduras': 'HN',
    'Hungary': 'HU',
    'Iceland': 'IS',
    'India': 'IN',
    'Indonesia': 'ID',
    'Iran': 'IR',
    'Iraq': 'IQ',
    'Ireland': 'IE',
    'Israel': 'IL',
    'Italy': 'IT',
    'Jamaica': 'JM',
    'Japan': 'JP',
    'Jordan': 'JO',
    'Kazakhstan': 'KZ',
    'Kenya': 'KE',
    'Korea, South': 'KR',
    'Kosovo': 'XK',
    'Kuwait': 'KW',
    'Kyrgyzstan': 'KG',
    'Laos': 'LA',
    'Latvia': 'LV',
    'Lebanon': 'LB',
    'Liberia': 'LR',
    'Libya': 'LY',
    'Liechtenstein': 'LI',
    'Lithuania': 'LT',
    'Luxembourg': 'LU',
    'Madagascar': 'MG',
    'Malaysia': 'MY',
    'Maldives': 'MV',
    'Mali': 'ML',
    'Malta': 'MT',
    'Mauritania': 'MR',
    'Mauritius': 'MU',
    'Mexico': 'MX',
    'Moldova': 'MD',
    'Monaco': 'MC',
    'Mongolia': 'MN',
    'Montenegro': 'ME',
    'Morocco': 'MA',
    'Mozambique': 'MZ',
    'MS Zaandam': '',
    'Namibia': 'NA',
    'Nepal': 'NP',
    'Netherlands': 'NL',
    'New Zealand': 'NZ',
    'Nicaragua': 'NI',
    'Niger': 'NE',
    'Nigeria': 'NG',
    'North Macedonia': 'MK',
    'Norway': 'NO',
    'Oman': 'OM',
    'Pakistan': 'PK',
    'Panama': 'PA',
    'Papua New Guinea': 'PG',
    'Paraguay': 'PY',
    'Peru': 'PE',
    'Philippines': 'PH',
    'Poland': 'PL',
    'Portugal': 'PT',
    'Qatar': 'QA',
    'Romania': 'RO',
    'Russia': 'RU',
    'Rwanda': 'RW',
    'Saint Kitts and Nevis': 'KN',
    'Saint Lucia': 'LC',
    'Saint Vincent and the Grenadines': 'VC',
    'San Marino': 'SM',
    'Saudi Arabia': 'SA',
    'Senegal': 'SN',
    'Serbia': 'RS',
    'Seychelles': 'SC',
    'Sierra Leone': 'SL',
    'Singapore': 'SG',
    'Slovakia': 'SK',
    'Slovenia': 'SI',
    'Somalia': 'SO',
    'South Africa': 'ZA',
    'Spain': 'ES',
    'Sri Lanka': 'LK',
    'Sudan': 'SD',
    'Suriname': 'SR',
    'Sweden': 'SE',
    'Switzerland': 'CH',
    'Syria': 'SY',
    'Taiwan*': 'TW',
    'Tanzania': 'TZ',
    'Thailand': 'TH',
    'Timor-Leste': 'TL',
    'Togo': 'TG',
    'Trinidad and Tobago': 'TT',
    'Tunisia': 'TN',
    'Turkey': 'TR',
    'Uganda': 'UG',
    'Ukraine': 'UA',
    'United Arab Emirates': 'AE',
    'United Kingdom': 'GB',
    'Uruguay': 'UY',
    'Uzbekistan': 'UZ',
    'Venezuela': 'VE',
    'Vietnam': 'VN',
    'West Bank and Gaza': 'PS',
    'Western Sahara': 'EH',
    'Zambia': 'ZM',
    'Zimbabwe': 'ZW',
    'Australia': 'AU',
    'Canada': 'CA',
    'China': 'CN',
    'United States': 'US',
    'US': 'US'}

COLOUR_CODES = {
    '1-9': 'e0e0e0',
    '10-99': 'ffc0c0',
    '100-999': 'ee7070',
    '1000-9999': 'c80200',
    '10000-99999': '900000',
    '100000+': '510000'
}

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
