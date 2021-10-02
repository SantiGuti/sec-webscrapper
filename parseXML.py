from bs4 import BeautifulSoup


class parseXML:

    def __init__(self):
        self.name_of_issuer = []
        self.value = []
        self.ssh_prnamt = []
        self.ssh_prnamt_type = []
        self.soup = BeautifulSoup

    def parse(self, content):
        # The .xml given by the forms.txt table is not well formed.
        # I use the BeatifulSoap library to "clean" the .xml and
        # be able to find the information more easily
        self.soup = BeautifulSoup(content, "lxml-xml")

    def loadValues(self):
        self.name_of_issuer = (self.soup.find_all("nameOfIssuer"))
        self.value = (self.soup.find_all("value"))
        self.ssh_prnamt = (self.soup.find_all("sshPrnamt"))
        self.ssh_prnamt_type = (self.soup.find_all("sshPrnamtType"))

        self.cleanValues()

    def cleanValues(self):
        # The value I have now contains the tag used by the .xml.
        # Passing the value to string removes that label
        for i in range(0, len(self.name_of_issuer)):
            self.name_of_issuer[i] = self.name_of_issuer[i].string
            self.value[i] = self.value[i].string
            self.ssh_prnamt[i] = self.ssh_prnamt[i].string
            self.ssh_prnamt_type[i] = self.ssh_prnamt_type[i].string
