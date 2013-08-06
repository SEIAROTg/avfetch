#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core
import json

if __name__ == '__main__':
    import cmdargs
    core.args = cmdargs.parse()

    core.default = {}
    for key in core.defaults:
        value = getattr(core.args, key, None)
        if value:
            core.default[key] = value

    core.verbose = core.args.verbose

    if core.args.jobfile == None:
        import sys
        job = json.load(sys.stdin)
    elif core.args.jobfile.find('://') == -1: # input job file
        with open(core.args.jobfile, 'r') as f:
            job = json.load(f)
    else: # input URL
        job = [{'url': core.args.jobfile}]
    
    for avitem in job:
        core.apply_default(avitem, core.default, core.defaults)
    
    import engine
    if core.args.action == 'list':
        core.print_job(engine.list(job))
    elif core.args.action == 'resolve':
        core.print_job(engine.resolve(job))
    elif core.args.action == 'download':
        engine.download(job)
        if core.args.combine:
            pass # TODO: combine
