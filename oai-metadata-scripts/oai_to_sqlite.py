import xml.etree.ElementTree as ET
import glob
import datetime
import os
import sys
import sqlite3

table_name = "metadata"
oai_path = "/home/rte/data/oai-metadata/"
db_path = "/home/rte/data/db/arxiv_db.sqlite3"

count = 0

bVerbose = True
# bVerbose = False

OAI = "{http://www.openarchives.org/OAI/2.0/}"
ARXIV = "{http://arxiv.org/OAI/arXiv/}"

db = sqlite3.connect(db_path)

# to just parse through one file
filenames = [oai_path + "2018-04-30-00000011.xml"]
# for filename in filenames:

# iteratively progress through all files in folder
for filename in glob.glob(oai_path + '*.xml'):

    data = ET.parse(filename)
    if(bVerbose):
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
            # date = ""
            date = info.find(ARXIV+"created").text
            # date = datetime.datetime.strptime(date, "%Y-%m-%d")
            categories = info.find(ARXIV+"categories").text
            title = info.find(ARXIV+"title").text
            abstract = info.find(ARXIV+"abstract").text

            license_node = info.find(ARXIV+"license")

            if license_node is not None:
                lic = license_node.text
                # print("license_node not None")
            else:
                lic = ""

            # attempt to get authors, not working, needs work
            authors = []
            authors_element = info.find(ARXIV+"authors")

            # create a variable to store all authors names
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

                # for fn in authors_element.find(ARXIV+"forenames"):
                    # aname += fn
                    # print(fn)
                # + author.find(ARXIV+"forenames").text
                # print(aname)

                anames += aname
                # for child in author:
                    # print(child.tag, child.attrib)
                # authors.append(author.find("keyname").text)
                # authors.append(author.find("forenames").text)

            authors.append(anames)

            count += 1

            if(bVerbose):
                print("-" * 20)
                print(identifier)
                print(date)
                print(categories)
                print(authors)
                print(title)
                print(abstract)
                print(lic) # don't use license as it is reserved for Python!

            c = db.cursor()

            # c.execute("INSERT INTO {tn} (identifier, created, cat, authors, title, abstract, licence) \
            # VALUES ({_id}, {_created}, {_cat}, {_authors}, {_title}, {_abstract}, {_licence})".\
            # format(tn=table_name, _id=identifier, _created=created, _cat=categories,\
            # _authors=authors, _title=title, _abstract=abstract, _licence=lic))

            print(table_name)
            print(identifier)
            print(date)
            print(authors)
            authors = "" + str(authors)
            print(authors)
            print(title)

            c.execute("INSERT INTO metadata (identifier, created, cat, authors, title, abstract, licence) \
            VALUES (?, ?, ?, ?, ?, ?, ?)", \
            (identifier, date, categories, authors, title, abstract, lic))
            # , authors, title, abstract, licence
            # , '{3}', '{4}', '{5}', '{6}'
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
