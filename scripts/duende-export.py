#!/usr/bin/env python
# -*- coding: utf8 -*-
"""Script to extract Duende resources from installed applications.

Extract static resources is useful to serve static contents using
a separate web server for example, in production environments.

"""

import argparse
import os
import shutil
import sys

from duende.lib.resource import get_resource_dir

DESCRIPTION = "Extract static resources from Duende apps."


def export_static(app_name, out_dir):
    """Copy static files from application dir to an external dir."""
    #get resource directory from app
    res_dir = get_resource_dir(app_name)
    if not res_dir:
        print '[WAR] Application %s dont have a resources dir, skipping ..' \
              % app_name

        return

    #get app static files directory
    static_dir = os.sep.join([res_dir, 'static', app_name.replace('.', '_')])
    if not os.path.isdir(static_dir):
        print '[WAR] Application %s dont have a static dir, skipping ..' \
              % app_name

        return

    #append app name to destination directory
    out_dir = os.sep.join([out_dir, app_name])
    if os.path.isdir(out_dir):
        msg = 'Destination dir already exist. Delete it ? [y/N]'
        if raw_input(msg).upper() == 'Y':
            #delete existing destination directory
            shutil.rmtree(out_dir)
        else:
            #any other value different than Y stops the script
            print '[OK] Script ended by user'

            sys.exit(0)

    try:
        #recursive copy app static files to destination dir
        shutil.copytree(static_dir, out_dir)
        print '[OK] Static files from %s copied sucessfully' % app_name
    except IOError, err:
        print '[ERR] Unable to copy static files from %s :' % app_name
        print '[ERR] %s' % str(err)

        sys.exit(1)


def get_argument_parser():
    """Get an ArgumentParser to process script arguments."""
    arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
    arg_parser.add_argument('apps', nargs='+',
                            help='List of space separated app names')
    arg_parser.add_argument('-d', '--dir', required=True, dest='out_dir',
                            help='Directory where to copy files')

    return arg_parser


def main():
    arg_parser = get_argument_parser()
    args = arg_parser.parse_args()
    out_dir = os.path.abspath(args.out_dir)
    #create destination dir if it does not exists
    if not os.path.isdir(out_dir):
        print 'Creating directory %s' % out_dir
        os.mkdir(out_dir)

    #extract resources from each app to destination dir
    for app_name in args.apps:
        export_static(app_name, out_dir)


if __name__ == '__main__':
    main()
    sys.exit()
