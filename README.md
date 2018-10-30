# Check License

Extract licenses of dependent packages from a repo with NPM or PIP and generate a `bill-of-material.json` file semi-automatically.

## Usage

1. Install npm `license-check`, and PIP, where the packages for a project is installed.
2. Configure `parsers.config.json` with absolute path
3. Run `python main.py`

The manually found licenses and license mappings will be stored in `formatter.config.json`.

## When running the app

### never_license_mapping

These licenses will never be automatically mapped to desired license. Whenever these are encountered, you need to check the licenses manually following the link or search it.

### license_mapping

These licenses in key fields will be converted to the ones in value fields. This is handy because:
e.g.
apache2 or apache license 2.0 or apache-2 or apache-2.0 should be mapped to Apache License, version 2.0

### known_project_licenses

These projects are manually searched and mapped. Whenever these projects are encountered, they will be automatically mapped to the license in the value fields.
