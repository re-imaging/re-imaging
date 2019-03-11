import xml.etree.ElementTree as ET
import glob
import datetime

count = 0
duplicateCount = 0
deleted = 0

ids = []

# bVerbose = True
bVerbose = False

OAI = "{http://www.openarchives.org/OAI/2.0/}"
ARXIV = "{http://arxiv.org/OAI/arXiv/}"

# inputID = input("Enter an arXiv identifier: ")
# inputID = "1804.04861"
# inputID = "9912209"
# print("searching for " + inputID)

filenames = ["2018-04-30-00000011.xml"]

for filename in glob.glob('*.xml'):
# for filename in filenames:

    data = ET.parse(filename)
    if(bVerbose):
        print("opening file: " + filename)
    root = data.getroot()

    # for identifier in root.iter('arXiv'):
    #     print("found an id")
    #     print(identifier.text)

    for record in root.findall('.ListRecords/record'):
        try:
            # arxiv_id = record.find('header').find('identifier')
            meta = record.find('metadata')
            # info = meta.find(ARXIV+"arXiv")
            # created = info.find(ARXIV+"created").text
            # created = datetime.datetime.strptime(created, "%Y-%m-%d")
            # categories = info.find(ARXIV+"categories").text

            identifier = meta.find(ARXIV+"arXiv/").text

            if(identifier in ids):
                print("identifier already in list! id: " + identifier)
                duplicateCount += 1
            else:
                ids.append(identifier)
                count += 1
                print(count)
                if(count % 10000 == 0):
                    print(ids)

            # print(ARXIV+"arXiv/"+"id")

            # this gets the arXiv element and then gets the text
            # for some reason it grabs the identifier ^_^
            if(bVerbose):
                print(identifier)
                print(created)
                print(categories)

            # if(inputID in identifier):
            #     print("-" * 20)
            #     print("FOUND RECORD:")
            #     print("-" * 20)
            #     # print the important parts of the record
            #     print(identifier)
            #     print(created)
            #     print(categories)
            #     print("-" * 20)
        except KeyboardInterrupt:
            # quit
            sys.exit()
        except:
            deleted += 1
            if(bVerbose):
                print("error! perhaps a record was deleted?")
            continue

print("*" * 20)
print("total number of unique items: " + str(count))
print("*" * 20)
print("total number of deleted items: " + str(deleted))
print("*" * 20)
