# -*- coding: utf-8 -*-
"""
Generate structured json data from online doc

http://docs.ucloud.cn/api/apilist.html
"""

import json
from pyquery import PyQuery

api_urls = [PyQuery(li)('a').attr('href')
            for li in PyQuery('http://docs.ucloud.cn/api/apilist.html')('.compound > ul ul li')]

api_list = {}
for url in api_urls:
    print(url)
    doc = PyQuery('http://docs.ucloud.cn/api/' + url)

    api = doc('.body > .section h1:first')
    PyQuery(api)('a').remove()

    params = []
    for tr in doc('[valign="top"]:first tr'):
        tds = PyQuery(tr)('td')
        params.append({
            'Name': PyQuery(tds[0]).text().replace('\n', ' '),
            'Type': PyQuery(tds[1]).text().replace('\n', ' '),
            'Desc': PyQuery(tds[2]).text().replace('\n', ' '),
            'Required': PyQuery(tds[3]).text().replace('\n', ' ').lower() == 'yes',
        })

    api_list[api.text()] = params


with open('doc.json', 'w') as f:
    f.write(json.dumps(api_list, indent=4, ensure_ascii=False).encode('utf-8'))
