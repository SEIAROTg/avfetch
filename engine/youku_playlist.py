# -*- coding: utf-8 -*-

import re
import core

def getIdByUrl(url):
    return core.regexps_search([r'^http://www.youku.com/playlist_show/id_(\d+)'], url)

def __getId_page(url):
    page = core.fetch(url).decode('utf-8')
    return core.regexps_search([r'http://v.youku.com/v_show/id_[A-Za-z0-9=]+\.html\?f=(\d+)'], page)

def list(avitem):
    url_playlist = 'http://www.youku.com/playlist_show/id_' + avitem['id'] + '_ascending_1_mode_1'
    ret = []
    while url_playlist:
        page_playlist = core.fetch(url_playlist).decode('utf-8')
        div_list = re.search(r'<div class="pack_list">([\s\S]*?)</div>', page_playlist).group(1)
        matches = re.finditer(r'<a([\s\S]*?)>[\s\S]*?</a>', div_list)
        for match in matches:
            attr = match.group(1)
            if attr.find('target="video"') != -1:
                title = re.search(r'title="([\s\S]*?)"', attr).group(1)
                url = re.search(r'href="([\s\S]*?)"', attr).group(1)
                this = {'title': title, 'url': url}
                core.apply_default(this, avitem)
                ret.append(this)
        div_pages = re.search(r'<div class="page f_r">([\s\S]*?)</div>', page_playlist).group(1)
        url_playlist = core.regexps_search([ur'<a href="(.+)"  title=\'下一页\'>&gt;&gt;</a>'], div_pages)
    return ret