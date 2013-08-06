# -*- coding: utf-8 -*-

import re
import core

def getIdByUrl(url):
    regexps = [
        r'^http://v.youku.com/v_show/id_([A-Za-z0-9=]+)',
        r'^http://player.youku.com/player.php/sid/([A-Za-z0-9=]+)'
        r'^http://static.youku.com/.*/v/swf/loader.swf?[\s\S]*VideoIDS=([A-Za-z0-9=]+)'
    ]
    return core.regexps_search(regexps, url)

def getIdByPage(url):
    header = core.fetch_header(url)
    if re.match(r'text/html', header['content-type']):
        page = core.fetch(url).decode('utf-8')
        regexps = [
            r'<head>[\s\S]*?var videoId\s*=\s*\'(.*)\'[\s\S]*?</head>',
            r'<head>[\s\S]*?var videoId2\s*=\s*\'(.*)\'[\s\S]*?</head>'
        ]
        return core.regexps_search(regexps, page)
    else:
        return False

def resolve(avitem):
    import json
    format = {'flv': 'flv', 'mp4': 'mp4', 'hd2': 'flv', '3gphd': 'mp4', '3gp': 'flv', 'hd3': 'flv'}
    quality = {'flv': '0', 'flvhd': '0', 'mp4': '1', 'hd2': '2', '3gphd': '1', '3gp': '0', 'hd3': '3'}
    core.apply_default(avitem, {'quality': ['flv', 'flvhd', 'mp4', 'hd2', 'hd3', '3gphd', '3gp'], 'path': '%title%%part%.%ext%'})
    url_filelist = 'http://v.youku.com/player/getPlayList/VideoIDS/' + avitem['id'] + '/Pf/4?password='
    if avitem.has_key('password'):
        url_filelist += avitem['password']
    filelist = json.loads(core.fetch(url_filelist).decode('utf-8'))['data'][0]
    if filelist.has_key('error_code'):
        return 'ERROR' # !!ERROR!!
    avitem['title'] = filelist['title']
    for seg in avitem['quality']:
        if filelist['segs'].has_key(seg):
            charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/\\:._-1234567890'
            cg = ''
            seed = filelist['seed']
            while len(charset) > 0:
                seed = (211 * seed + 30031) % 65536
                idx = seed * len(charset) / 65536
                cg += charset[idx]
                charset = charset[:idx] + charset[(idx+1):]
            cg_fun = ''
            for i in filelist['streamfileids'][seg].split('*')[:-1]:
                cg_fun += cg[int(i)]
            files = []
            for part in filelist['segs'][seg]:
                f = cg_fun[:8] + '%02X' % int(part['no']) + cg_fun[10:]
                a = part['k']
                if a == "" or a == -1:
                    a = filelist['key2'] + filelist['key1']
                url_part = 'http://f.youku.com/player/getFlvPath/sid/00_00/st/' + format[seg] + '/field/' + f + '?K=' + a + '&hd=' + quality[seg]
                size_part = int(part['size'])
                this = {
                    'url': url_part,
                    'size': size_part,
                    'path': core.getPath(avitem['path'], {
                            'quality': seg,
                            'title': avitem['title'],
                            'id': avitem['id'],
                            'ext': format[seg],
                            'part': '%02X' % int(part['no'])
                    })
                }
                files.append(this)
            if core.fetch_error(files[0]['url']):
                core.output('warning: resolved url not vaild. try next format...', 2)
            else:
                avitem['files'] = files
                avitem['path'] = core.getPath(avitem['path'], {
                    'quality': seg,
                    'title': avitem['title'],
                    'id': avitem['id'],
                    'ext': format[seg],
                    'part': ''
                })
                break
    if not avitem.has_key('files'):
        core.output('error: failed resolving url.')
        # !! error !!
    return avitem

def download(avitem):
    files = []
    for file in avitem['files']:
        files.append((file['url'], file['path'], file['size']))
    core.download(files)
    return avitem
