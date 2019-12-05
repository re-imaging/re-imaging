import xml.etree.ElementTree as ET
import glob
import datetime
import argparse
import sys

parser = argparse.ArgumentParser(description='Utility script for checking if there are duplicate records in Metha OAI metadata',
                                    epilog="Can take some time for large numbers of records")

parser.add_argument('oai_path', help='set folder of OAI xml files')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
parser.add_argument('-d', '--debug', action='store_true', help='debug output, prints all identifiers')

global args
args = parser.parse_args()

def main():
    count = 0
    duplicateCount = 0
    deleted = 0

    ids = []

    OAI = "{http://www.openarchives.org/OAI/2.0/}"
    ARXIV = "{http://arxiv.org/OAI/arXiv/}"

    for filename in glob.glob(args.oai_path + '*.xml'):

        data = ET.parse(filename)
        if(args.verbose):
            print("opening file: " + filename)
        root = data.getroot()

        for record in root.findall('.ListRecords/record'):
            try:
                # arxiv_id = record.find('header').find('identifier')
                meta = record.find('metadata')
                if(args.debug):
                    info = meta.find(ARXIV+"arXiv")
                    created = info.find(ARXIV+"created").text
                    # created = datetime.datetime.strptime(created, "%Y-%m-%d")
                    categories = info.find(ARXIV+"categories").text

                identifier = meta.find(ARXIV+"arXiv/").text

                # check to see if identifier has already been added to list
                if(identifier in ids):
                    print("identifier already in list! id: " + identifier)
                    duplicateCount += 1
                else:
                    ids.append(identifier)
                    count += 1
                    if(args.debug):
                        print(count)
                    if(count % 10000 == 0):
                        print(count, "records checked")
                        if(args.verbose):
                            print(ids[count-10000:count])

                # this gets the arXiv element and then gets the text
                # for some reason it grabs the identifier ^_^
                if(args.debug):
                    print(identifier)
                    print(created)
                    print(categories)

            except KeyboardInterrupt:
                print("~~~~~ interrupted, exiting ~~~~~")
                print("*" * 20)
                print("--- totals so far:")
                printFinalResults(count, deleted, duplicateCount)
                # print, then quit
                sys.exit()
            except:
                deleted += 1
                if(args.verbose):
                    print("error! perhaps a record was deleted?")
                continue
    print("*" * 20)
    print("--- final totals:")
    printFinalResults(count, deleted, duplicateCount)

def printFinalResults(count, deleted, duplicateCount):
    print("total number of unique items: " + str(count))
    print("*" * 20)
    print("total number of deleted items: " + str(deleted))
    print("*" * 20)
    print("total number of duplicate items: " + str(duplicateCount))
    print("*" * 20)

if __name__ == "__main__":
    main()
