import xml.etree.ElementTree as ET
import glob
import os
import argparse

parser = argparse.ArgumentParser(description='Utility script for finding number of records in Metha OAI metadata')

parser.add_argument('oai_path', help='set folder of OAI xml files')

global args
args = parser.parse_args()

os.chdir(args.oai_path)
print("current working directory:",os.getcwd())

total_count = 0
num_xml_files = 0

for filename in glob.glob('*.xml'):
    num_xml_files += 1
    print(num_xml_files, filename)
    data = ET.parse(filename)
    root = data.getroot()
    for record in root.iter('record'):
        total_count += 1

print("total number of xml files:",num_xml_files)
print ("total number of records:",total_count)
