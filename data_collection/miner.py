#!/usr/bin/env python3

import sqlite3
import os
import sys
import requests

urls = []

client_id = ""
client_secret = ""
CREATE_STRING = "CREATE TABLE IF NOT EXISTS repos (id NUM, repo_name TEXT, tar_path TEXT, language TEXT, forks NUM, subscribers NUM, watchers NUM, has_docs NUM, has_uml NUM);"

# ?client_id=8b58a63cd6de300b1d1c&client_secret=f38de56b58bf9e1b43539becc779105c70ee7fd6

def get_keys():
    with open("../client_id.txt") as f:
        global client_id
        client_id = f.readline()
    with open("../client_secret.txt") as f:
        global client_secret
        client_secret = f.readline()

def auth(url):
    return url+"?client_id="+client_id+"&client_secret="+client_secret

def get_js(url):
    url=auth(url)
    resp = requests.get(url, timeout=15)
    return resp.json()

if __name__ == "__main__":
    get_keys()
    with sqlite3.connect("../repos.db") as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_STRING)
        if os.path.isfile("start_file"):
            with open("start_file", "r") as f:
                start = int(f.readline())
        else:
            start = 0
        next = start
        try:
            while True:
                try:
                    print("Getting list from " + str(next))
                    url = auth("https://api.github.com/repositories") + "&since={}".format(next)
                    resp = requests.get(url)
                    js = resp.json()
                    for item in js:
                        if not item['fork']:
                            item_url = auth(item['url'])
                            #print(item_url)
                            repo_js = get_js(item_url)
                            next = item['id']
                            repo_name = item['full_name']
                            tar_path = item['archive_url'].replace("{archive_format}{/ref}", "tarball/master")
                            language = repo_js['language']
                            #contributors = len(get_js(repo_js['contributors_url']))
                            forks = max(repo_js['forks_count'], repo_js['forks'])
                            subscribers = repo_js['subscribers_count']
                            watchers = max(repo_js['watchers_count'], repo_js['watchers'], repo_js['stargazers_count'])
                            try:
                                print("Inserting ID {}".format(next))
                                cursor.execute("INSERT INTO repos VALUES (?,?,?,?,?,?,?,?,?)", [next,repo_name,tar_path,language,forks,subscribers,watchers,0,0])
                                conn.commit()
                            except Exception as e:
                                print(e)
                    next=js[-1:][0]['id']
                except Exception as e:
                    print("Error, skipping forward!")
                    next += 1
                    pass
        except KeyboardInterrupt as e:
            print("Ctrl + C was pressed")
        finally:
            with open("start_file", "w+") as f:
                f.write(str(next))
