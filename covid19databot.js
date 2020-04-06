// COVID-19 Data copier

let util = require('util')
let fs = require('fs')
let fetch = require('node-fetch')
let readFile = util.promisify(fs.readFile)
let writeFile = util.promisify(fs.writeFile)

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
    let escaped = escape(pageName)
    return `https://en.wikipedia.org/w/index.php?action=raw&title=${escaped}`
}

let pageToData = function(page) {
    let data = []
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

let main = async function() {
    let sources = await getSources()
    for (let i = 0; i < sources.length; i++) {
        let source = sources[i]
        let cc = source[0]
        let pageName = source[1]
        console.log(`Getting data for ${cc} from ${pageName}`)
        let pu = pageUrl(pageName)
        console.log(`fetching ${pu}`)
        let res = await fetch(pu)
        let page = await res.text()
        console.log(page.length)
        let data = pageToData(page)
        console.log(data.length)
        let finished = await putData(cc, data)
    }
}

main()