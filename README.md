# check-license
Extract licenses of dependent packages from a repo with NPM or PIP and generate a bill-of-material.json file semi-automatically.

# Usage

1. Run `Python generate_bill_of_materials.py` under a project with `requirements.txt` and `package.json`.
2. Follow the instructions. If you messed it up, close the program, open `bill_of_materials.config.json` to edit the wrong configuration. 
3. The result will be stored in the `bill_of_materials1.json` in case you don't want to really mess up the original `bill_of_materials.json`. It's your responsibility to check and rename.

# Fields in Config

### never_license_mapping

These licenses will never be automatically mapped to desired license. Whenever these are encountered, you need to check the licenses manually following the link or search it.

### license_mapping

These licenses in key fields will be converted to the ones in value fields. This is handy because:
e.g. 
apache2 or apache license 2.0 or apache-2 or apache-2.0 should be mapped to Apache License, version 2.0

### known_project_licenses

These projects are manually searched and mapped. Whenever these projects are encountered, they will be automatically mapped to the license in the value fields.
