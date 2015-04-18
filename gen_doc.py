# -*- coding: utf-8 -*-
"""
Generate structured json data from online doc

http://docs.ucloud.cn/api/apilist.html
"""

import json
from pyquery import PyQuery

regions = ['cn-north-01', 'cn-north-02', 'cn-north-03', 'cn-east-01', 'cn-south-01', 'hk-01', 'us-west-01']

api_urls = [PyQuery(li)('a').attr('href')
            for li in PyQuery('http://docs.ucloud.cn/api/apilist.html')('.compound > ul ul li')]

api_list = {}
for url in api_urls:
    print(url)
    doc = PyQuery('http://docs.ucloud.cn/api/' + url)

    api = doc('.body > .section h1:first')
    PyQuery(api)('a').remove()

    params = {}
    has_length_col = 'length' in doc('.docutils:first thead').text().lower()
    for i, tr in enumerate(doc('.docutils:first tbody tr')):
        tds = PyQuery(tr)('td')
        if has_length_col:
            del tds[2]
        params[PyQuery(tds[0]).text().replace('\n', ' ')] = {
            'Type': PyQuery(tds[1]).text().replace('\n', ' '),
            'Desc': PyQuery(tds[2]).text().replace('\n', ' '),
            'Required': PyQuery(tds[3]).text().replace('\n', ' ').lower() == 'yes',
            'Order': i,
        }

    api_list[api.text()] = params

api_list['UpdateSecurityGroup']['Rule.n']['Desc'] += ' Proto|Dst_port|Src_ip|Action|Priority'


with open('doc.json', 'w') as f:
    f.write(json.dumps(api_list, indent=4, ensure_ascii=False).encode('utf-8'))
