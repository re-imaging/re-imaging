import xml.etree.ElementTree as ET
import glob

total_count = 0
num_xml_files = 0

for filename in glob.glob('*.xml'):
    num_xml_files += 1
    data = ET.parse(filename)
    root = data.getroot()
    for record in root.iter('record'):
        total_count += 1

# filepath = 'arXiv_src_manifest.xml'

# read in xml file
# data = ET.parse('2018-01-31-00000000.xml')

# print the first line to test
# root = data.getroot()
# print root
# ListRecords = root.get

# total_count = 0
# for each file listed, get the size and add it to count
for record in root.iter('record'):
    total_count += 1 # use 1 here instead to just get the total

    # print child.tag, child.attrib
    # # get all records
    # records = data.findall('record')
    # for record in records:
        # count = file.find('size').text
        # count = int(count)
        # total_count += 1 # use 1 here instead to just get the total
print "total number of xml files: "
print num_xml_files
print "total count: "
print total_count
