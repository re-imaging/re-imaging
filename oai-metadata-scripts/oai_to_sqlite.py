import xml.etree.ElementTree as ET
import glob
import datetime

import sqlite3

table_name = "metadata"
db_path = "../sqlite/arxiv_db.sqlite3"

count = 0

bVerbose = True
# bVerbose = False

OAI = "{http://www.openarchives.org/OAI/2.0/}"
ARXIV = "{http://arxiv.org/OAI/arXiv/}"

# def data_entry():
#     c = db.cursor()
#     try:
#         c.execute("INSERT INTO {tn} (identifier, created) VALUES ({_id}, {_created})".\
#         format(tn=table_name, _id=identifier, _created=created))
#         # do this after inserting everything
#         db.commit()
#         c.close()
#     except sqlite3.IntegrityError:
#         print('ERROR: ID already exists in PRIMARY KEY column')
#     except Exception as e:
#         raise e

try:
    # maybe find a better way to get filepath of db
    db = sqlite3.connect(db_path)
    # c = db.cursor()
except Exception as e:
    # Roll back any change if something goes wrong
    db.rollback()
    raise e

# to just parse through one file
filenames = ["2018-04-30-00000011.xml"]
for filename in filenames:

# iteratively progress through all files in folder
# for filename in glob.glob('*.xml'):

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
            created = info.find(ARXIV+"created").text
            # created = datetime.datetime.strptime(created, "%Y-%m-%d")
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

            # getting whole string is very messy
            # astr = ET.tostring(authors_element, encoding='utf8', method='xml').decode()
            # print(astr)

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
                print(created)
                print(categories)
                print(authors)
                print(title)
                print(abstract)
                print(lic) # don't use license as it is reserved for Python!

            c = db.cursor()
            c.execute("INSERT INTO {tn} (identifier, created, cat, authors, title, abstract, licence) VALUES ({_id}, {_created}, {_cat}, {_authors}, {_title}, {_abstract}, {_licence})".\
            format(tn=table_name, _id=identifier, _created=created, _cat=categories, _authors=authors, _title=title, _abstract=abstract, _licence=lic))

        except KeyboardInterrupt:
            # quit
            sys.exit()
        # except AttributeError as error:
            # print(error)
            # continue
        finally:
            print("finished")
            print("total count: " + str(count))
# do this after inserting everything
db.commit()
c.close()

db.close()
