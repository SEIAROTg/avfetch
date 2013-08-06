# -*- coding: utf-8 -*-

import types
import core

enginedir = 'engine'

def get_engine(avitem):
    if avitem.has_key('engine'):
        engine = engines[avitem['engine']]
        media_id = get_id(avitem)
        if media_id:
            return engine
    else:
        for name, engine in engines.iteritems():
            media_id = engine.getIdByUrl(avitem['url'])
            if media_id:
                avitem['id'] = media_id
                avitem['engine'] = name
                avitem.pop('url', None)
                return engine
    # ERROR: UNABLE TO DETECT ENGINE

def get_id(avitem):
    if avitem.has_key('id'):
        return avitem['id']
    elif avitem.has_key('engine'):
        avitem['id'] = engines[avitem['engine']].getIdByPage(avitem['url'])
        avitem.pop('url', None)
        return avitem['id']
    else:
        pass # ERROR: UNEXPECTED SITUATION

def list(avitem):
    if type(avitem) is types.ListType:
        for index in range(0, len(avitem)):
            avitem[index:index+1] = list(avitem[index])
        return avitem
    else:
        return get_engine(avitem).list(avitem)

def resolve(avitem):
    if type(avitem) is types.ListType:
        for item in avitem:
            resolve(item)
        return avitem
    else:
        if core.args.restart or not avitem.has_key('files'):
            result = get_engine(avitem).resolve(avitem)
            if result:
                return result
            else:
                list(avitem)
                return resolve(avitem)

def download(avitem):
    if type(avitem) is types.ListType:
        for item in avitem:
            download(item)
        return avitem
    else:
        if not avitem.has_key('files'):
            resolve(avitem)
        result = get_engine(avitem).download(avitem)
        if result:
            return result
        else:
            resolve(avitem)
            return download(avitem)

def default_getIdByPage(avitem):
    return False

def default_list(avitem):
    return [avitem]

def default_resolve(avitem):
# TODO: tabs -> spaces
# TODO: code quality check
    return False

def default_download(avitem):
    return False
    # ERROR: NOT IMPLEMENTATION

import os
def is_engine(src_file):
    return \
		os.path.isfile(enginedir + '/' + src_file) and \
		src_file.endswith('.py') and \
		src_file != '__init__.py'

engines = {}
for src_file in os.listdir(enginedir):
    if is_engine(src_file):
        name = src_file[:-3]
        engines[name] = getattr(__import__(enginedir + '.' + name), name)
        if not callable(getattr(engines[name], 'getIdByPage', None)):
            engines[name].getIdByPage = default_getIdByPage
        if not callable(getattr(engines[name], 'list', None)):
            engines[name].list = default_list
        if not callable(getattr(engines[name], 'resolve', None)):
            engines[name].resolve = default_resolve
        if not callable(getattr(engines[name], 'download', None)):
            engines[name].download = default_download