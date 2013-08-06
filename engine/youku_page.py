# -*- coding: utf-8 -*-

import re
import core

def getIdByUrl(url):
    return core.regexps_search([r'^http://www.youku.com/show_page/id_([a-z0-9]+)'], url)

def getIdByPage(url):
    page = core.fetch(url).decode('utf-8')
    return core.regexps_search([r'<head>[\s\S]*window.g_config={\s*id:\'([a-z0-9]+)\'[\s\S]*</head>'], page)
    
def list(avitem):
    url_page = 'http://www.youku.com/show_page/id_' + avitem['id']
    page_page = core.fetch(url_page).decode('utf-8')
    ul_reloads = re.search(r'<ul id="zySeriesTab">([\s\S]*?)</ul>', page_page).group(1)
    reloads = re.finditer(r'<li data="(.*?)"[\s\S]*?>', ul_reloads)
    ret = []
    for reload in reloads:
        url_episodes = 'http://www.youku.com/show_episode/id_' + avitem['id'] + '?divid=' + reload.group(1)
        page_episodes = core.fetch(url_episodes).decode('utf-8')
        episodes = re.finditer(r'<ul[\s\S]*?>\s*?<li[\s\S]*?>[\s\S]*?<a([\s\S]*?charset=".*?"[\s\S]*?)>[\s\S]*?</a>[\s\S]*?</li>', page_episodes)
        for episode in episodes:
            attrs = episode.group(1)
            title_episode = re.search(r'title="([\s\S]*?)"', attrs).group(1)
            this = {'title': title_episode}
            core.apply_default(this, avitem)
            url_episode = re.search(r'href="(.+?)"', attrs).group(1)
            this['url'] = url_episode
            ret.append(this)
    return ret