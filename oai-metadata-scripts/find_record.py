import xml.etree.ElementTree as ET
import glob
import datetime
import argparse

parser = argparse.ArgumentParser(description='Utility script for finding a specific article record in OAI metadata')

# also useful for parsing over large numbers of items and checking for data integrity

parser.add_argument('oai_path', help='set folder of OAI xml files')
parser.add_argument("--input_id", type=str, help="arXiv identifier to search for")
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')

global args
args = parser.parse_args()

count = 0
deleted = 0

OAI = "{http://www.openarchives.org/OAI/2.0/}"
ARXIV = "{http://arxiv.org/OAI/arXiv/}"

if args.input_id is None:
    inputID = input("Enter an arXiv identifier: ")
else:
    inputID = args.input_id

print("searching for " + inputID)

for filename in glob.glob(args.oai_path + '*.xml'):
    data = ET.parse(filename)
    if(args.verbose):
        print("opening file: " + filename)
    root = data.getroot()

    for record in root.findall('.ListRecords/record'):
        try:
            # arxiv_id = record.find('header').find('identifier')
            meta = record.find('metadata')
            info = meta.find(ARXIV+"arXiv")
            created = info.find(ARXIV+"created").text
            created = datetime.datetime.strptime(created, "%Y-%m-%d")
            categories = info.find(ARXIV+"categories").text

            identifier = meta.find(ARXIV+"arXiv/").text

            # this gets the arXiv element and then gets the text
            # for some reason it grabs the identifier ^_^
            if(args.verbose):
                print(identifier)
                print(created)
                print(categories)

            if(inputID in identifier):
                print("*" * 20)
                print("FOUND RECORD:")
                print("-" * 20)
                # print the important parts of the record
                print(identifier)
                print(created)
                print(categories)
                print(filename)
                # print("-" * 20)
        except KeyboardInterrupt:
            # quit
            sys.exit()
        except:
            deleted += 1
            if(args.verbose):
                print("error! perhaps a record was deleted?")
            continue

print("*" * 20)
print("total number of erroneous (possible deleted) items: " + str(deleted))
