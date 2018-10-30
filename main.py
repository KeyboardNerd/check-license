import json
from bill_of_materials import BillOfMaterials
from formatter import Formatter

bill_of_materials_path = "bill_of_materials.json"
formatter_path = "formatter.config.json"
parser_config = "parsers.config.json"


def load_parser_config(path):
    ps = []
    with open(path) as f:
        config = json.load(f)
        npm_config = config.get("npm")
        if npm_config:
            import parsers.npm
            ps.append(parsers.npm.get(**npm_config))

        pip_config = config.get("pip")
        if pip_config:
            import parsers.pip
            ps.append(parsers.pip.get(**pip_config))

    return ps


if __name__ == '__main__':
    formatter = Formatter(formatter_path)
    bill = BillOfMaterials(bill_of_materials_path, formatter)
    retrievers = load_parser_config(parser_config)

    for f in retrievers:
        for material in f():
            bill.add(material)

    bill.save()
