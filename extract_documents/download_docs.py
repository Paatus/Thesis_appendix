#!/usr/bin/env python3
import os
import sqlite3
import subprocess
import urllib.request
import shutil

client_id = ""
client_secret = ""
db_name = "../repos.db"
repo_dir = "repos/"
docs_path = "docs/"

def get_keys():
    with open("client_id.txt") as f:
        global client_id
        client_id = f.readline()
    with open("client_secret.txt") as f:
        global client_secret
        client_secret = f.readline()

def auth(url):
    return url+"?client_id="+client_id+"&client_secret="+client_secret

def get_id(gen):
    for item in gen:
        yield (item,)

if __name__ == "__main__":
    last_id = 0
    try:
        if os.path.isfile("start_file"):
            with open("start_file", "r") as f:
                start = int(f.readline())
        else:
            start = 0
        rows = []
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, tar_path FROM repos WHERE id > ?", (start,))
            rows = cur.fetchall()
        # for each row in database
        for row in rows:
            id = row[0]
            last_id = id
            url = auth(row[1])
            if not os.path.exists(repo_dir):
                os.mkdir(repo_dir)
            dir_path = "{}{}".format(repo_dir, id)
            filename = dir_path + "/master.tar.gz"
            # create folder if it doesn't exists
            if not os.path.exists(dir_path):
                #print("Making directory {}".format(dir_path))
                os.mkdir(dir_path)
            # save tar
            dl_success = True
            print("ID {}".format(id))
            try:
                with urllib.request.urlopen(url, timeout=60*5) as response, open(filename, 'wb') as out_file:
                    data = response.read()
                    out_file.write(data)
            except urllib.error.HTTPError as e:
                print("ID {} Error code {}".format(id, e.code))
                dl_success = False
                pass
            except urllib.error.URLError:
                print("ID {} Timed out.".format(id))
            except Exception as e:
                print("ERROR: {}".format(e))
                pass
            # check if archive contains docs
            if dl_success:
                try:
                    p = subprocess.Popen(['tar','-xvf',filename, '-C', dir_path], stdout=subprocess.PIPE)
                    p2 = subprocess.check_output(['grep -E "*\.pdf|*\.docx|*\.pptx"'], stdin=p.stdout, shell=True)
                # failed to unpack or no files
                except subprocess.CalledProcessError as e:
                    #print("-----------Removing {}------------".format(dir_path))
                    subprocess.run(["rm", "-rf", dir_path])
                    pass
                else:
                    docs_f = p2.decode().strip().split("\n")
                    docs = [x for x in docs_f if x[x.rfind(".")+1:] in ('pdf','docx','pptx')]
                    print("ID {} has {} documents".format(id, len(docs)))
                    for i, doc in enumerate(docs):
                        ending = doc[doc.rfind(".")+1:]
                        if ending in ("pdf","docx","pptx"):
                            f_name = "{}_doc_{}.{}".format(id, i, ending)
                            old_path = "{}/{}".format(dir_path, doc)
                            if not os.path.exists(docs_path):
                                os.mkdir(docs_path)
                            new_path = "{}{}".format(docs_path, f_name)
                            #print("Moving {} to {}".format(old_path, new_path))
                            try:
                                shutil.move(old_path, new_path)
                            except:
                                print("ID {} Error when moving, skipping".format(id))
                                pass
                            else:
                                with sqlite3.connect(db_name) as conn:
                                    cur = conn.cursor()
                                    cur.execute("UPDATE repos SET has_docs = ? WHERE id = ?", (len(docs),id))
            subprocess.run(["rm", "-rf", dir_path])
    except KeyboardInterrupt:
        print("Ctrl + C was pressed")
        with open("start_file", "w+") as f:
            f.write("{}".format(last_id))
    finally:
        print("DONE!")
