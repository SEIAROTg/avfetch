import urllib2

inherit = ['lang', 'path', 'password', 'quality']
defaults = ['engine', 'lang', 'path', 'password', 'quality']

verbose = 0

def apply_default(avitem, default, items=inherit):
    for key, value in default.iteritems():
        if key in items and not avitem.has_key(key):
            avitem[key] = value

def regexps_search(regexps, str):
    import re
    for regexp in regexps:
        match = re.search(regexp, str)
        if match:
            return match.group(1)
    return False

def fetch(url):
    return urllib2.urlopen(url).read()

def fetch_header(url):
    resp = urllib2.urlopen(url)
    return resp.info().dict

def fetch_error(url):
    try:
        urllib2.urlopen(url)
    except urllib2.HTTPError:
        return True
    return False

def title_required(mask):
    i = 0
    inpercent = False
    for c in mask:
        if c == '%':
            if inpercent:
                if this == 'title':
                    return True
                inpercent = False
            else:
                inpercent = True
                this = ''
        else:
            if inpercent:
                this += c
    return False

def getPath(mask, data):
    ret = ''
    i = 0
    inpercent = False
    for c in mask:
        if c == '%':
            if inpercent:
                if this == '':
                    ret += '%'
                elif not data.has_key(this):
                    ret += '%' + this + '%'
                else:
                    ret += data[this]
                inpercent = False
            else:
                inpercent = True
                this = ''
        else:
            if inpercent:
                this += c
            else:
                ret += c
    return ret

def print_job(job):
    import json
    import sys
    if args.format:
        json.dump(job, sys.stdout, ensure_ascii=False, indent=4)
    else:
        json.dump(job, sys.stdout, ensure_ascii=False)

def download(files):
    import os
    import sys
    import threading
    import timeit
    
    CHUNK_SIZE = 0x2000
    CYCLE = 0.5 # second(s)
    
    def report(text=''):
        import pgbar
        pgbar.draw(progress['got_size'], progress['total_size'], text)
    
    def call_report():
        if progress['ts0'] == progress['ts1']:
            speed = 0
        else:
            speed = progress['got_cycle'] / (progress['ts0'] - progress['ts1'])
        progress['ts1'] = progress['ts0']
        if speed == 0:
            s_eta = '       '
        else:
            eta = (progress['total_size'] - progress['got_size']) / speed
            eta_s = eta % 60
            eta /= 60
            eta_m = eta % 60
            eta /= 60
            eta_h = eta
            if eta >= 3600: # one hour
                s_eta = '%2dh %2dm' % (eta_h, eta_m)
            else:
                s_eta = '%2dm %2ds' % (eta_m, eta_s)
            speed_u = 'B'
            if speed > 1000:
                speed_u = 'K'
                speed /= 1024
                if speed > 1000:
                    speed_u = 'M'
                    speed /= 1024
                    if speed > 1000:
                        speed_u = 'G'
                        speed /= 1024
            
            s_speed = '%6.1f%s/s' % (speed, speed_u)
            report(s_eta + ' ' + s_speed)
        
        
        progress['got_cycle'] = 0
        if progress['got_size'] < progress['total_size']:
            timer = threading.Timer(CYCLE, call_report)
            timer.setDaemon(True)
            timer.start()
    
    # get size
    progress = {
        'total_size': 0,
        'got_size': 0,
        'got_cycle': 0
    }
    progress['ts0'] = timeit.default_timer()
    progress['ts1'] = progress['ts0']
    
    for index in range(len(files)):
        if len(files[index]) == 2: # no size information
            resp = urllib2.urlopen(files[index][0])
            size = resp.info().dict.get('content-length', None)
            if size:
                files[index] += (size,)
            else:
                pass # ERROR: NOT IMPLEMENTATION
                # TODO: support downloading files that do not provide size
        progress['total_size'] += files[index][2]
    
    call_report()
    for file in files:
        if os.path.isfile(file[1]):
            file_size = os.path.getsize(file[1])
            progress['got_size'] += file_size
            if file_size < file[2]:
                req = urllib2.Request(file[0])
                req.add_header('Range', 'bytes=%d-' % file_size)
            else:
                continue
        else:
            req = urllib2.Request(file[0])
        resp = urllib2.urlopen(req)
        f = open(file[1], 'ab')
        data = resp.read(CHUNK_SIZE)
        progress['ts0'] = timeit.default_timer()
        while data:
            try:
                f.write(data)
                got = len(data)
                progress['got_cycle'] += got
                progress['got_size'] += got
                data = resp.read(CHUNK_SIZE)
                progress['ts0'] = timeit.default_timer()
            except KeyboardInterrupt:
                sys.exit(0)
        f.close()
    report()