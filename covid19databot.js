// COVID-19 Data copier

let util = require('util')
let fs = require('fs')
let fetch = require('node-fetch')
let readFile = util.promisify(fs.readFile)
let writeFile = util.promisify(fs.writeFile)
let {URLSearchParams, URL} = require('url')
let path = require('path')

const SOURCES_FILE = './Sources.tab.json'
const SCHEMA = {
    "fields": [
        {
            "name": "date",
            "type": "string",
            "title": {
                "en": "Date"
            }
        },
        {
            "name": "deaths",
            "type": "number",
            "title": {
                "en": "Deaths"
            }
        },
        {
            "name": "recoveries",
            "type": "number",
            "title": {
                "en": "Recoveries"
            }
        },
        {
            "name": "cases",
            "type": "number",
            "title": {
                "en": "Active cases"
            }
        }
    ]
}

DATA_DIR = 'data'

let getSources = async function() {
    let contents = await readFile(SOURCES_FILE, 'utf8')
    let data = JSON.parse(contents)
    return data.data
}

let pageUrl = function(pageName) {
    let pu = new URL('https://en.wikipedia.org/w/api.php')
    pu.search = new URLSearchParams({
        'action': 'query',
        'prop': 'revisions',
        'rvslots': '*',
        'rvprop': 'content',
        'formatversion': 2,
        'format': 'json',
        'titles': pageName
    })
    return pu.toString()
}

let toNum = function(str) {
    if (!str) {
        return null
    } else if (str.length == 0) {
        return 0
    } else {
        return parseInt(str)
    }
}

let pageToData = function(page) {
    let data = []
    let m = page.match(/\|data=(.*?)\|/s)
    if (m) {
        let lines = m[1].split('\n')
        for (line of lines) {
            if (line.length > 0) {
                let row = line.split(';')
                data.push([row[0], toNum(row[1]), toNum(row[2]), toNum(row[3])])
            }
        }
    }
    return data
}

let putData = async function(cc, data, dir) {
    let json = {}
    json.schema = SCHEMA
    json.data = data
    let contents = JSON.stringify(json, null, 2)
    return writeFile(path.join(DATA_DIR, `${cc}.tab.json`), contents, 'utf8')
}

let getPage = async function(pageName) {
    let pu = pageUrl(pageName)
    console.log(`fetching ${pu}`)
    let res = await fetch(pu, {headers: {'User-Agent': 'Covid19DataBot/0.1.0'}})
    let json = await res.json()
     return json.query.pages[0].revisions[0].slots.main.content
}

let main = async function() {
    let sources = await getSources()
    for (let i = 0; i < sources.length; i++) {
        let source = sources[i]
        let cc = source[0]
        let pageName = source[1]
        console.log(`Getting data for ${cc} from ${pageName}`)
        try {
            page = await getPage(pageName)
            console.log(page.length)
            let data = pageToData(page)
            console.log(data.length)
            let finished = await putData(cc, data)
        } catch (err) {
            console.error(err)
        }
     }
}

main()