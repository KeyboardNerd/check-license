import json
from collections import namedtuple

bill_of_materials_file_path = "bill-of-materials.json"

class Material(object):
    def __init__(self, name, licenses, format_, link):
        self.name = name
        self.licenses = licenses
        self.format = format_
        self.link = link

    def __str__(self):
        return "Project: '%s', License: '%s', Link:   '%s'"%(self.name, self.licenses, self.link)
    
    def __repr__(self):
        return self.__str__()

class BillOfMaterials(object):
    def __init__(self, file_path, formatter):
        self.file_path = file_path
        self.bill_of_materials = []
        self.formatter = formatter

    def add(self, material):
        material = self.formatter.format(material)
        d = {
            "project": material.name,
            "format": material.format,
            "license": material.licenses,
        }

        if d in self.bill_of_materials:
            return

        self.bill_of_materials.append(d)

    @staticmethod
    def sort_key(e):
        prefix = "0"
        if e["format"] == "Javascript":
            prefix = "1"
        return prefix + e["project"].lower()

    def save(self):
        with open(bill_of_materials_file_path, "w+") as bill_of_materials_file:
            self.bill_of_materials.sort(key=BillOfMaterials.sort_key)
            json.dump(
                self.bill_of_materials,
                bill_of_materials_file,
                indent=4,
                sort_keys=True)
        print "saved total %d package licenses" % (len(self.bill_of_materials), )
