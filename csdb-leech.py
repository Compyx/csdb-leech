#!/usr/bin/env python3
#
# pip3 install lxml

import sys
import os
import os.path
import xml.etree.ElementTree
import requests

CSDB_WEBSRV = 'http://csdb.dk/webservice'
GROUP_MEGASTYLE = 473
GROUP_FOCUS = 135

"""
https://csdb.dk/webservice/?type=search&stype=release&q=Test&start=0&count=25
"""

def sanitize_filename(arg):
    return arg.replace('/', '_').replace('\\', '_')


def show_usage():
    print("Usage: {} [args]".format(os.path.basename(sys.argv[0])))



def find_group_by_name(group_name, limit=10):
    url = "{}?type=search&stype=group&q={}&start=0&count={}".format(
            CSDB_WEBSRV, group_name, limit)
    page = requests.get(url)
    # print(page.content)

    root = xml.etree.ElementTree.fromstring(page.content)
    # print(root.tag)
    groups = root.findall('CSDbSearchResult/Group')
    for g in groups:
        grp_id = g.findall('ID')[0].text
        grp_name = g.findall('Name')[0].text
        grp_country = g.findall('BaseCountry')[0].text
        print("{:>5} {} ({})".format(grp_id, grp_name, grp_country))


def get_xml_by_group_id(group_id):
    url = "{}/?type=group&id={}&depth=3".format(CSDB_WEBSRV, group_id)
    print("url = {}".format(url))
    page = requests.get(url)

    root = xml.etree.ElementTree.fromstring(page.content)
    print(root.tag)
    group = root.find('Group')
    name = group.find('Name')
    print(name.text)

    proper_name = sanitize_filename(name.text)

    try:
        os.mkdir(proper_name)
    except:
        pass

    os.chdir(proper_name)


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

            if 'download.php' in dl:
                print("Got PHP download link, skipping for now.")
                continue


            print("   Downloading {}".format(dl))
            try:
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

    find_group_by_name('focus')
    sys.exit(0)


    try:
        os.mkdir('temp')
    except:
        pass

    os.chdir('temp')
    get_xml_by_group_id(GROUP_MEGASTYLE)


