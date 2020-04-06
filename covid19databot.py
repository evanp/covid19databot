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

WORLD_MAP_TEMPLATE = "File:BlankMap-World.svg"
WORLD_MAP_FILE = "BlankMap-World.svg"

WORLD_CASE_DATA_URL_TEMPLATE = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/%s.csv"

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
    'US': 'US'}

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
    print(country_data)
    createWorldCaseDataMap(country_data)
    uploadWorldCaseDataMap()

def downloadWorldMapTemplate():
    site = pywikibot.Site('commons', 'commons')
    image = pywikibot.FilePage(site, WORLD_MAP_TEMPLATE)
    image.download(WORLD_MAP_FILE)

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
        if not row['FIPS'] and not row['Admin2'] and not row['Province_State']:
            iso = nameToISO(row['Country_Region'])
            countries[iso] = {'confirmed': int(row['Confirmed']), 'deaths': int(row['Deaths']), 'recovered': int(row['Recovered'])}
    return countries

def nameToISO(name):
    return ISO_CODES.get(name)

def createWorldCaseDataMap(country_data):
    pass

def uploadWorldCaseDataMap():
    pass

def worldCaseDataUrl(date):
    return WORLD_CASE_DATA_URL_TEMPLATE % (date.strftime('%m-%d-%Y'),)

if __name__ == "__main__":
    main()
