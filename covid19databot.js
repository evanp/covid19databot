// COVID-19 Data copier

let util = require('util')
let fs = require('fs')
let fetch = require('node-fetch')
let readFile = util.promisify(fs.readFile)
let writeFile = util.promisify(fs.writeFile)
let {URLSearchParams, URL} = require('url')

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

let pageToData = function(page) {
    let data = []
    console.log(page)
    let ma = page.match(/{{Medical cases chart\/Row\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|/g)
    if (ma) {
        for (let i = 0; i < ma.length; i++) {
            const m = ma[i]
            const f = m.match(/{{Medical cases chart\/Row\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|/)
            data.push(f[1], f[2], f[3], f[4])
        }
    }
    return data
}

let putData = async function(cc, data) {
    let json = {}
    json.schema = SCHEMA
    json.data = data
    let contents = JSON.stringify(json, null, 2)
    return writeFile(`${cc}.tab.json`, contents, 'utf8')
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