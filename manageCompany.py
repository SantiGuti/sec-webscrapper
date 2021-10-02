class manageCompany:

    def __init__(self):
        # Change this value to filter another form type
        self.form_type_filter = "13F-HR"

        self.form_types = []
        self.company_names = []
        self.CIKs = []
        self.date_filed = []
        self.file_names = []

    def loadValues(self, path):
        file = open(path, "r")
        content = file.read()
        content_list = content.split('\n')
        file.close()

        for i in range(10, len(content_list)):
            line = content_list[i]

            current_line_form_type = (line[62:74]).strip()
            if current_line_form_type == self.form_type_filter:

                # Each value in the forms.txt table has a maximum number of characters.
                # I use that rule to take each value and then use strip() to erase the blanks
                current_line_company_name = (line[0:62]).strip()
                current_line_CIK = (line[74:86]).strip()
                current_line_date_filed = (line[86:98]).strip()
                current_line_file_name = line[98:len(line)].strip()

                self.form_types.append(current_line_form_type)
                self.company_names.append(current_line_company_name)
                self.CIKs.append(current_line_CIK)
                self.date_filed.append(current_line_date_filed)
                self.file_names.append(current_line_file_name)
