#!/usr/bin/env python -u

import sys
import os
import io
import re
import unicodedata
import hashlib
import requests
import hydrus
import hydrus.utils
from lxml import html
import json
import codecs
from collections import OrderedDict
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

#User Variables
#Edit these as necessary
hydrus_api_url = "http://127.0.0.1:45869/"
hydrus_api_key = ""
hydrus_tag_service = "public tag repository"
e621_username = ""
e621_api_key = ""
hash_file = "hashes.txt"

try:
	hash_input = open(hash_file, "r+")
except FileNotFoundError:
	print("Hash file not found!\n", hash_file, "\nTerminating...")
	sys.exit(4)


hydrus_permissions = [hydrus.Permission.SearchFiles, hydrus.Permission.AddTags]

client = hydrus.Client(hydrus_api_key, hydrus_api_url)

try:
	p = hydrus.utils.verify_permissions(client, hydrus_permissions)
except:
	print("Hydrus-API encountered a server error.\nHydrus API key may be malformed.")
	sys.exit(1)
else:
	if not hydrus.utils.verify_permissions(client, hydrus_permissions):
		print("The Hydrus API key does not grant all required permissions:", hydrus_permissions)
		sys.exit(2)

headers = {
    'User-Agent': 'TagParser/0.05 by GanBat',
}

#Here's the parsing stuff.
#If you want to parse anything other than these three sites, add the url and format defs here.
def parse_booru(h, b):
    if b == "rule34.xxx":
        url = str("https://rule34.xxx/index.php?md5="+h+"&page=post&s=list")
        format = "gelbooru02"
    if b == "gelbooru":
        url = str("https://gelbooru.com/index.php?md5="+h+"&page=post&s=list")
        format = "gelbooru025"
    if b == "e621":
        url = str("https://e621.net/posts.json/?md5="+h+"&login="+e621_username+"&api_key="+e621_api_key)
        format = "e621"
    print("Loading url: "+url, flush=True)
    page = requests.get(url, headers=headers)
    if page.status_code != 200:
        print("status code: "+str(r.status_code), flush=True)
        pass
    taglist = list()
    if format == "gelbooru025":
        root = html.fromstring(page.text)
        for item in root.get_element_by_id("tag-list").xpath("./li"):
            if "tag-type-artist" in item.classes:
                print("Creator tag found")
                taglist.append("creator:"+item[1].text_content())
            elif "tag-type-copyright" in item.classes:
                print("Series tag found")
                taglist.append("series:"+item[1].text_content())
            elif "tag-type-character" in item.classes:
                print("Character tag found")
                taglist.append("character:"+item[1].text_content())
            elif "tag-type-metadata" in item.classes:
                print("Meta tag found")
                taglist.append("meta:"+item[1].text_content())
            elif "tag-type-general" in item.classes:
                taglist.append(item[1].text_content())
            else:
                pass
    if format == "gelbooru02":
        root = html.fromstring(page.text)
        print(root.get_element_by_id("tag-sidebar"))
        for item in root.get_element_by_id("tag-sidebar").find_class("tag"):
            if "tag-type-artist" in item.classes:
                print("Creator tag found")
                taglist.append("creator:"+item[0].text_content())
            elif "tag-type-copyright" in item.classes:
                print("Series tag found")
                taglist.append("series:"+item[0].text_content())
            elif "tag-type-character" in item.classes:
                print("Character tag found")
                taglist.append("character:"+item[0].text_content())
            elif "tag-type-metadata" in item.classes:
                print("Meta tag found")
                taglist.append("meta:"+item[0].text_content())
            elif "tag-type-general" in item.classes:
                taglist.append(item[0].text_content())
            else:
                pass
    if format == "e621":
        results = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(page.text)
        for tags in results['post']['tags']['general']:
            taglist.append(re.sub(r"_", " ", tags))
        for tags in results['post']['tags']['species']:
            taglist.append("species:"+re.sub(r"_", " ", tags))
        for tags in results['post']['tags']['character']:
            taglist.append("character:"+re.sub(r"_", " ", tags))
        for tags in results['post']['tags']['copyright']:
            taglist.append("series:"+re.sub(r"_", " ", tags))
        for tags in results['post']['tags']['artist']:
            taglist.append("creator:"+re.sub(r"_", " ", tags))
        for tags in results['post']['tags']['lore']:
            taglist.append(re.sub(r"_", " ", tags))
        for tags in results['post']['tags']['meta']:
            taglist.append("meta:"+re.sub(r"_", " ", tags))
    return taglist

all_hashes=hash_input.read().splitlines()
#print(str(all_hashes))
metadata = client.file_metadata(hashes=all_hashes)
for metadatum in metadata:
    #print(str(metadatum['hash'].splitlines()))
    print()
    file_id = metadatum['file_id']
    print("File ID: "+str(file_id))
    #file = open(client.get_file(file_id=file_id).content, 'rb')
    md5 = hashlib.md5(client.get_file(file_id=file_id).content).hexdigest()
    print("File MD5: "+str(md5))
    for tag in metadatum['service_names_to_statuses_to_display_tags']['my tags']['0']:
        boorutags = re.findall(r'^booru:(.+$)', tag)
        for tag in boorutags:
            if tag == "sankaku channel":
                #Sankaku's bullshit makes parsing it too much trouble.
                continue
            print("Booru:"+tag)
            taglist = parse_booru(md5, tag)
            print(str(taglist))
            client.add_tags(hashes=metadatum['hash'].splitlines(), service_to_tags={hydrus_tag_service: taglist})
        
    