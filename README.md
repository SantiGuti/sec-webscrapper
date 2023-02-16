# SEC Webscrapper

The Python program is designed to run on PythonAnywhere.com. Its purpose is to extract data from a personal Google Drive file, which contains a .csv of codes named CIKs. The program then accesses the sec.gov website to download the .xml file required. After downloading the file, the program checks for matches between the CIKs in the .csv file and those found in the .xml file, extracting the relevant information and writing it to an output.csv file. This process is repeated for each .xml file, covering a two-year period, where each .xml represents a quarter of a year.

Upon completion, the program generates two outputs: an .csv file containing all the required data, which is uploaded to Google Drive, and a log of the program's activities.
