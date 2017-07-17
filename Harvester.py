# THIS PYTHON SCRIPT PARSES THROUGH AN XML DOCUMENT INPUT OF ITEMS IN THE SCHOLARS GEOPORTAL AND RETURNS A CSV FILE
# CONTAINING SELECTED METADATA. THIS CSV FILE IS LATER USED TO POPULATE STATIC WEBPAGES TO BE GOOGLE INDEXED, MAKING
# THE GEOPORTAL ITEMS MORE DISCOVERABLE. THE SELECTED METADATA INCLUDE THE FIELDS: IDENTIFIER, TITLE, PRODUCER,
# ABSTRACT, PUBLICATION YEARS, GEOPORTAL PERMALINK, LINK TO THE ITEM'S THUMBNAIL IMAGE, AVAILABLE FORMATS, AND USERS
# WITH VIEW PERMISSION TO EACH ITEM.

# Note: - Currently, the script works only with Python 3.5.2 or newer, due to version-unique libraries and commands.
#       - The xml.etree.ElementTree module implements an API for parsing XML data. Its documentation may be found at
#         https://docs.python.org/3/library/xml.etree.elementtree.html.

import sys
import csv
from urllib import request
import xml.etree.ElementTree as ET

# DOWNLOADING THE XML FILE FROM SCHOLAR GEOPORTAL'S URL TO USER ACCESSIBLE CONTENT.

# Defining the URL to user accessible content as provided by Scholars GeoPortal.
URL = "http://geo2.scholarsportal.info/proxy.html?http:__giseditor.scholarsportal.info/search/index.html?limit=entitled&env=production&q=*&i=1000&fm=xml"

# Creating a function that retrieves the content from the URL above.
def get(URL):
    with request.urlopen(URL) as content:
        return content.read()

# Downloading the XML document into C:\Home\GeoPortal.
with open ('Content.xml', 'wb') as xmlfile:
    xmlfile.write(get(URL))

# IMPORTING THE XML DATA BY READING FROM Content.xml.

# Here, .getroot() obtains the top element of the XML file. In this case, the top element is response, which
# contains the total list of results provided by the XML document.
xmldata = ET.parse('Content.xml')
response = xmldata.getroot()

# DETERMINING PUBLICLY AVAILABLE ITEMS.
publicids = []

# WRITING THE DESIRED FIELDS OF METADATA TO Harvested.csv.

# Opening the output file the condensed metadata will be written and appended to, then defining a writer object
# responsible for converting the input data into delimited strings for the output file.
outfile = open('Harvest.csv', 'wt')
outfile = open('Harvest.csv', 'a')
writer = csv.writer(outfile, dialect = 'excel', lineterminator = '\n')

# Writing desired metadata from the XML file to the output file.
for result in response.findall('result'):

    line = [] # This is the empty list to which information will be appended to within an item's row.
    line.append(result.find('id').text)         # Appending the item identifier.
    line.append(result.find('title').text)      # Appending the title.
    line.append(result.find('producer').text)   # Appending the producer.
    line.append(result.find('abstract').text)   # Appending the abstract.

    # Obtaining the earliest publication year available.
    earliestdate = result[7][0].text
    earliestyear = earliestdate[:4]

    # Obtaining the most recent publication year available.
    # Capturing the instance where result[8] is 'revision-date'.
    if result[8].text is not None:
        
        latestdate = result[8].text
        latestyear = latestdate[:4]

    # Capturing the instance where result[8][0] is 'date', within 'publish-date'.
    elif len(result[8][0].text) == 10:
        
        latestdate = result[8][0].text
        latestyear = latestdate[:4]

    # Capturing the instance where result[8][0] is 'boundingbox'.
    # In this case, there is only one publication, and one publication date.
    else:
        
        latestyear = earliestyear

    # Obtaining and appending the range of years for available publications.
    publicationrange = earliestyear + ' - ' + latestyear

    # Creating each item's permalink.
    permalink = "http://geo.scholarsportal.info/#r/details/_uri@=" + result.find('id').text
    formats = "Various geospatial formats available."

    # Obtaining information on users with view permission for each item.
    # Currently, Scholars GeoPortal has noted that all items within the OpenContent and DLI collections are open.
    if result.find('collections').text == "OpenContent":

        permission = "Open to the public."

    elif result.find('collections').text == "DLI":

        permission = "Open to the public."

    else:

        permission = "Available to McMaster Staff, Faculty, and Students. Login required for off-campus access."
        
    line.append(publicationrange)               # Appending the range of publication years.
    line.append(permalink)                      # Appending the permalink.
    line.append(result.find('thumbnail').text)  # Appending the thumbnail link.
    line.append(formats)                        # Appending the format information.
    line.append(permission)                     # Appending the users with view permission.

    # Writing the row of metadata for each item into the CSV file.
    writer.writerow(line)

outfile.close()

print ("Success. Your harvested metadata has been written to", outfile.name)
