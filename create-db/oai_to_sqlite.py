import xml.etree.ElementTree as ET
import glob
import datetime
import os
import sys
import sqlite3
import argparse

parser = argparse.ArgumentParser(description='Parse Metha OAI XML files and insert metadata into SQLite database')

parser.add_argument('db_path', help="path to SQLite database")
parser.add_argument('oai_path', help='set folder of OAI xml files')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

global args
args = parser.parse_args()

table_name = "metadata"
oai_path = args.oai_path
db_path = args.db_path

count = 0

OAI = "{http://www.openarchives.org/OAI/2.0/}"
ARXIV = "{http://arxiv.org/OAI/arXiv/}"

db = sqlite3.connect(db_path)

# iteratively progress through all files in folder
# for filename in glob.glob(oai_path + '*.xml'):
files = [os.path.join(oai_path, f) for f in os.listdir(oai_path) if os.path.isfile(os.path.join(oai_path, f)) and ".xml" in f]
# in alpha-numeric order
files.sort()
# print(files)
print("number of files:",len(files))

for filename in files:
    data = ET.parse(filename)
    if(args.verbose):
        print("opening file: " + filename)
    root = data.getroot()

    for record in root.findall('.ListRecords/record'):
        try:
            # arxiv_id = record.find('header').find('identifier')

            meta = record.find('metadata')
            # this gets the arXiv element and then gets the text
            # for some reason it grabs the identifier : /
            id_node = meta.find(ARXIV+"arXiv/")
            if id_node is not None:
                identifier = id_node.text
            else:
                print("CONTINUING PAST RECORD - NO ID")
                continue

            info = meta.find(ARXIV+"arXiv")
            date = info.find(ARXIV+"created").text
            # date = datetime.datetime.strptime(date, "%Y-%m-%d")
            categories = info.find(ARXIV+"categories").text
            title = info.find(ARXIV+"title").text
            abstract = info.find(ARXIV+"abstract").text

            license_node = info.find(ARXIV+"license")

            if license_node is not None:
                lic = license_node.text
            else:
                lic = ""

            authors_list = []
            authors_element = info.find(ARXIV+"authors")

            # create a (string) variable to store all authors names
            # for now, this just writes the whole list of authors as a string
            anames = ""

            for author in authors_element:
                # print(author.find(ARXIV+"keyname").text)
                aname = ""
                kn = author.find(ARXIV+"keyname").text
                fn_node = author.find(ARXIV+"forenames")
                if fn_node is not None:
                    fn = fn_node.text
                else:
                    fn = ""
                aname =  kn + ", " + fn + "; "

                anames += aname

            authors_list.append(anames)

            # convert to string and remove extra characters
            # authors = "" + str(authors)
            authors = (str)(authors_list)[2:-4]

            # optionally clean up abstract by removing first 2 characters (spaces),
            # replacing line breaks with spaces and removing trailing whitespace
            # abstract = abstract[2:].replace("\n"," ").rstrip()

            count += 1

            if(args.verbose):
                print("-" * 20)
                print("identifier:",identifier)
                print("date:",date)
                print("categories:",categories)
                print("authors:",authors)
                print("title:",title)
                print("abstract:",abstract)
                print("licence:",lic) # don't use license as it is reserved for Python!

            c = db.cursor()

            c.execute("INSERT INTO metadata (identifier, created, cat, authors, title, abstract, licence) \
            VALUES (?, ?, ?, ?, ?, ?, ?)", \
            (identifier, date, categories, authors, title, abstract, lic))

            c.close()

        except KeyboardInterrupt:
            db.commit()

            # quit
            sys.exit()

        # except AttributeError as error:
            # print(error)
            # continue

        except Exception as e:
            raise e
        # finally:


# do this after inserting everything
db.commit()
c.close()
db.close()

print("finished")
print("total count: " + str(count))
