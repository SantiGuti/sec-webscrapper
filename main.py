from __future__ import print_function
import random
from urllib.error import HTTPError
import datetime
import os
import time
import urllib
import csv
import requests
from DriveAPI import DriveAPI
from manageCompany import *
from parseXML import parseXML

# Here put the ID of the CIKs.csv file
ID_file_Drive = ""

# Here put the name of the file that has the CIKs
name_file_Drive = "CIKs.csv"

date_logs = time.strftime("%Y%m%d-%H%M%S")


def main():
    GDrive = DriveAPI()
    company_manager = manageCompany()
    keep_working = True
    # company_number is used for the company.txt's URL and to check how many company.txt I have checked
    company_number_loops = 1
    time_sleep_before_downloading = 2

    # Create logs file
    # Create new .csv file and write first line
    logAction("Creating output.csv...")

    output_csv = open('output.csv', 'w')
    writer_csv = csv.writer(output_csv)
    writer_csv.writerow(
        ['"Fund Name"', '"CIK"', '"Filing Date"', '"Filing Count"', '"Issuer"', '"Ticker"', '"Dollar Value"',
         '"Share Count"', '"Share Type"'])
    logAction("File output.csv created, first line written")

    # Download file from GDrive trough ID and file's name
    logAction("Downloading " + name_file_Drive + "...")

    if not downloadCIKs(GDrive):
        exit()

    # Loading CIKs values to array
    CIKs_file = open(name_file_Drive, 'r')
    content_CIKs_file = CIKs_file.read()
    CIKs_to_find = content_CIKs_file.split('\n')
    CIKs_file.close()

    # Used to check how many times i found that CIK
    CIKs_quantity = []
    for i in range(0, len(CIKs_to_find)):
        CIKs_quantity.append(1)
    os.remove(name_file_Drive)
    logAction("CIKs to be found data loaded")

    # Variables used to modify forms.txt's URL to download files older than current year and quarter
    date = datetime.datetime.today()
    quarter_company_url = ((date.month - 1) // 3 + 1)
    year_company_url = date.year

    logAction("Starting loop...")
    while keep_working:

        logAction("Setting URL to download company.txt")
        constant_company_url = "https://www.sec.gov/Archives/edgar/full-index/year/QTR/company.idx"
        company_downloaded = False
        company_url = constant_company_url

        # forms_number = 1 means first time running program, no need to download older company.txt
        if company_number_loops == 1:
            company_url = company_url.replace("year", str(year_company_url))
            company_url = company_url.replace("QTR", "QTR" + str(quarter_company_url))
        else:
            # This mean I already checked all company.txt from that year because I went through the four quarters of the year
            if quarter_company_url - 1 == 0:
                year_company_url -= 1
                quarter_company_url = 4
                company_url = company_url.replace("year", str(year_company_url))
                company_url = company_url.replace("QTR", "QTR" + str(quarter_company_url))
            else:
                # Else just do quarter - 1
                quarter_company_url -= 1
                company_url = company_url.replace("year", str(year_company_url))
                company_url = company_url.replace("QTR", "QTR" + str(quarter_company_url))

        # Now with the URL modified I can download the company.txt that I need
        logAction("Starting process to download company.txt")

        while not company_downloaded:
            try:
                time.sleep(time_sleep_before_downloading)
                urllib.request.urlretrieve(company_url, 'company' + str(year_company_url) + str(quarter_company_url) + '.txt')
                logAction("File company" + str(year_company_url) + str(quarter_company_url) + ".txt Downloaded")
                company_downloaded = True

            except HTTPError as e:

                if e == 403:
                    logAction("sec.gov rejected request. Retrying...")
                    time.sleep(time_sleep_before_downloading)
                    urllib.request.urlretrieve(company_url, 'company' + str(year_company_url) + str(quarter_company_url) + '.txt')

                    logAction("File company" + str(year_company_url) + str(quarter_company_url) + ".txt Downloaded")
                    company_downloaded = True
        # Change value of forms_downloaded so when the keep_working loop resets I can get into the while forms_downloaded loop again
        company_downloaded = False

        # Load values from forms.txt into arrays. If the arrays already have values, I delete them and put the new values
        company_manager.loadValues('company' + str(year_company_url) + str(quarter_company_url) + '.txt')
        logAction("Data from company.txt parsed")

        # Delete forms.txt file because I don't need it anymore
        os.remove('company' + str(year_company_url) + str(quarter_company_url) + '.txt')

        # Program starts looking for CIK matches
        logicPart(CIKs_quantity, CIKs_to_find, company_manager, writer_csv, time_sleep_before_downloading)
        company_number_loops += 1

        if company_number_loops > 8:
            keep_working = False
            logAction("Went through 2 years of company.txt files. Finishing...")

        if all(ele >= 3 for ele in CIKs_quantity):
            keep_working = False
            logAction("All CIKs were found. Finishing...")

    logAction("Uploading output.csv to Drive...")

    checkCIKsnotFound(CIKs_quantity, CIKs_to_find)

    output_csv.close()
    # Upload .csv to GDrive
    uploadOutput(GDrive)


def checkCIKsnotFound(CIKs_quantity, CIKs_to_find):
    CIKs_not_found = []
    CIKs_found_one_time = []
    for i in range(0, len(CIKs_to_find)):
        if CIKs_quantity[i] == 1:
            CIKs_not_found.append(CIKs_to_find[i])
        if CIKs_quantity[i] == 2:
            CIKs_found_one_time.append(CIKs_to_find[i])

    logAction("These CIKs haven't been found: " + str(CIKs_not_found))
    logAction("These CIKs have been found one time only: " + str(CIKs_found_one_time))


def logicPart(CIKs_quantity, CIKs_to_find, company_manager, writer_csv, time_sleep_before_downloading):
    constant_url = "https://www.sec.gov/Archives/"
    parse_xml = parseXML()
    xml_downloaded = False

    # By making a request to sec.gov I make it believe that
    # I am a real web browser, a real user so it does not flag my ip
    user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36 OPR/56.0.3051.52",
                       "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"]

    for i in range(0, len(CIKs_to_find)):

        for j in range(0, len(company_manager.form_types)):

            if CIKs_to_find[i] == company_manager.CIKs[j] and CIKs_quantity[i] <= 2:

                logAction("Two identical CIK value found")
                download_xml = constant_url + company_manager.file_names[j]
                # The sec.gov API says it lets me download 10 files per second, or 1 file every 0.1 seconds
                # But that's not true. That's why the time.sleep() before any request to sec.gov
                logAction("Starting process to download .xml file")
                content_xml = ""
                user_agent = random.choice(user_agent_list)
                headers = {'User-Agent': user_agent}

                while not xml_downloaded:
                    time.sleep(time_sleep_before_downloading)
                    response = requests.get(download_xml, headers=headers)
                    if response.status_code == 200:
                        content_xml = response.text
                        xml_downloaded = True
                        logAction("File .xml downloaded")

                    else:
                        logAction("Error: " + str(response) + ". Retrying...")
                        time.sleep(time_sleep_before_downloading)

                    logAction("sec.gov web took: " + str(response.elapsed.total_seconds()) + " to respond the request " + str(response))

                xml_downloaded = False
                logAction("Parsing .xml file")
                parse_xml.parse(content_xml)
                parse_xml.loadValues()

                logAction("Writing values from .xml to output.csv")
                for k in range(0, len(parse_xml.name_of_issuer)):
                    writer_csv.writerow(['"' + company_manager.company_names[j] + '"',
                                         '"' + str(company_manager.CIKs[j]) + '"',
                                         '"' + str(company_manager.date_filed[j]) + '"',
                                         '"' + str(CIKs_quantity[i]) + '"',
                                         '"' + parse_xml.name_of_issuer[k] + '"',
                                         "", '"' + str(parse_xml.value[k]) + '"',
                                         '"' + str(parse_xml.ssh_prnamt[k]) + '"',
                                         '"' + parse_xml.ssh_prnamt_type[k] + '"'])

                CIKs_quantity[i] = CIKs_quantity[i] + 1


def uploadOutput(GDrive):
    for i in range(0, 5):
        if GDrive.FileUpload("output.csv"):
            logAction("File output.csv uploaded to Drive. Program finished. Goodbye.")
            return True

        else:
            logAction("Something went wrong uploading output.csv to Drive. Retrying...")

    logAction("Can't upload output.csv to Drive. Program finished. Goodbye.")
    return False


def downloadCIKs(GDrive):
    for i in range(0, 5):
        if GDrive.FileDownload(ID_file_Drive, name_file_Drive):
            logAction(name_file_Drive + " Downloaded")
            return True

        else:
            logAction("Something went wrong downloading " + name_file_Drive + " from Drive. Retrying...")

    logAction("Can't download from Drive. Program finished. Goodbye.")
    return False


def logAction(message):
    logs = open("logs " + date_logs + ".txt", "a")
    logs.write("[" + str(datetime.datetime.now()) + "] " + message + "\n")
    logs.close()
    print("[" + str(datetime.datetime.now()) + "] " + message)


if __name__ == "__main__":
    main()
