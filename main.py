from bill_of_materials import BillOfMaterials
from formatter import Formatter
import parsers.npm, parsers.pip

bill_of_materials_path = "bill_of_materials.json"
formatter_path = "formatter.config.json"

if __name__ == '__main__':
    formatter = Formatter(formatter_path)
    bill = BillOfMaterials(bill_of_materials_path, formatter)
    retrievers = [parsers.npm.get, parsers.pip.get]

    for f in retrievers:
        for material in f():
            bill.add(material)
    
    bill.save()
