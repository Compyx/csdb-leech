#!/usr/bin/env python3
#
# pip3 install lxml

import sys
import os
import os.path
import xml.etree.ElementTree
import requests
import argparse


PRG_VERSION = "0.1"

CSDB_WEBSRV = 'http://csdb.dk/webservice'
GROUP_MEGASTYLE = 473
GROUP_FOCUS = 135

"""
https://csdb.dk/webservice/?type=search&stype=release&q=Test&start=0&count=25
"""

def sanitize_filename(arg):
    return arg.replace('/', '_').replace('\\', '_')


def show_version(args):
    print("{} {}".format(sys.argv[0], PRG_VERSION))


def find_group_by_name(args):
    """
    Look up group ID's by name
    """

    if args.limit <= 0:
        url = "{}?type=search&stype=group&q={}&start=0".format(
            CSDB_WEBSRV, args.group_name)
    else:
        url = "{}?type=search&stype=group&q={}&start=0&count={}".format(
            CSDB_WEBSRV, args.group_name, args.limit)

    page = requests.get(url)
    # print(page.content)

    root = xml.etree.ElementTree.fromstring(page.content)
    # print(root.tag)
    groups = root.findall('CSDbSearchResult/Group')
    for g in groups:
        grp_id = g.findall('ID')[0].text
        grp_name = g.findall('Name')[0].text
        try:
            grp_country = g.findall('BaseCountry')[0].text
        except:
            grp_country = "<missing>"
        print("{:>5} {} ({})".format(grp_id, grp_name, grp_country))


def get_releases_by_group_id(args):
    """
    Download releases by group ID"
    """

    url = "{}/?type=group&id={}&depth=3".format(
            CSDB_WEBSRV, args.releases_by_group)
    print("url = {}".format(url))
    page = requests.get(url)

    root = xml.etree.ElementTree.fromstring(page.content)
    group = root.find('Group')
    name = group.find('Name')

    if args.directory == '.':
        dir_name = sanitize_filename(name.text)
    else:
        dir_name = args.directory

    if args.verbose:
        print("Creating dir '{}'".format(args.directory))
    try:
       os.mkdir(dir_name)
    except:
       pass

    os.chdir(dir_name)


    releases = group.findall("Release")
    for r in releases:
        n = r.find('Release/Name')
        print("  Creating directory '{}'".format(n.text))
        try:
            os.mkdir(sanitize_filename(n.text))
        except:
            pass
        os.chdir(sanitize_filename(n.text))
        for d in r.findall('Release/DownloadLinks/DownloadLink'):
            dl = d.find('Link').text
            ok = d.find("Status").text

            if 'download.php' in dl:
                if args.verbose:
                    print("Got PHP download link, skipping for now.")
                    continue


            print("   Downloading {}".format(dl))
            try:
                if args.verbose:
                    print("    Writing {}".format(os.path.basename(dl)))
                result = requests.get(dl, allow_redirects=True)
                try:
                    f = open(sanitize_filename(os.path.basename(dl)), 'wb')
                    f.write(result.content)
                    f.close()
                except:
                    print("failed to open {}".format(os.path.basename(dl)))
            except:
                continue
        os.chdir('..')



if __name__ == '__main__':
    #   if len(sys.argv) < 2:
    #       show_usage()
    #       sys.exit(1)

    # initialize argument parser
    parser = argparse.ArgumentParser(
            description="Leech files from CSDb")

    # add arguments
    parser.add_argument("-V", "--verbose",
                        help="verbose messages",
                        action="store_true")

    parser.add_argument("-v", "--version",
                        help="show version number",
                        action="store_true")

    parser.add_argument("-d", "--directory",
                        help="set output directory",
                        metavar="PATH",
                        default=".")

    parser.add_argument("--limit",
                        help="set limit on objects returned",
                        type=int,
                        default=-1)

    parser.add_argument("-g", "--group-name",
                        help="list group ID's for NAME",
                        metavar="NAME")

    parser.add_argument("-r", "--releases-by-group",
                        help="download releases for GROUPID",
                        metavar="GROUPID",
                        type=int)

    args = parser.parse_args()

    # print(args)

    if args.version:
        show_version(args)
        sys.exit(0)

    if args.group_name:
        find_group_by_name(args)
        sys.exit(0)


    if args.releases_by_group:
        print("Getting releases for group ID {}".format(
            args.releases_by_group))
        get_releases_by_group_id(args)
        sys.exit(0)

    parser.print_help()
    sys.exit(1)

