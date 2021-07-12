import xml.etree.ElementTree as ET

# filepath = 'arXiv_src_manifest.xml'

# read in xml file
data = ET.parse('arXiv_pdf_manifest.xml')

# get the entire etree
files = data.findall('file')

total_count = 0
# for each file listed, get the size and add it to count
for file in files:
    count = file.find('size').text
    count = int(count)
    total_count += 1 # use 1 here instead to just get the total
print total_count
