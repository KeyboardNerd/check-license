import json
from bill_of_materials import Material

template_choice = """
Unknown license '%s',
1. Enter the desired license name shown to user
2. Enter '=' to keep same name
3. Enter 'x' to always manually set the license for this unknown license
4. Leave empty to manually set the license for this specific project
>"""
template_progress = """
Existing mapping to:
%s"""
template_map_project_license = "map project '%s' to license '%s'"
template_map_license_license = "map license '%s' to license '%s'"
template_never_map = "never map license '%s'"


class Formatter(object):
    def __init__(self, state_path):
        self.state = FormatterState(
            state_path)  # state of config will be updated.

    def format(self, material):
        if isinstance(material.licenses, list):
            licenses = []
            for l in material.licenses:
                licenses.append(self.format_license(l, material))
            formatted_license = " and ".join(licenses)
        else:
            formatted_license = self.format_license(material.licenses,
                                                    material)

        return Material(material.name, formatted_license, material.format,
                        material.link)

    def prompt_map_license_license(self, license_, material):
        print self.state.current_state()
        raw = raw_input(template_choice % (license_, ))
        if raw == "x":
            self.state.add_never_license_mapping(license_)

        if raw == "" or raw == "x":
            return self.prompt_add_known_project(material)

        if raw == "=":
            raw = license_

        self.state.add_license_mapping(license_, raw)
        return raw

    def prompt_add_known_project(self, material):
        license_ = raw_input("%s Project '%s' (%s) has license >" %
                             (material.format, material.name, material.link))
        mapped_license = self.state.get_license(license_)
        if mapped_license:
            license_ = mapped_license

        self.state.add_known_project(material, license_)
        return license_

    def format_license(self, license_, material):
        mapped_license = self.state.get_license(license_)
        if mapped_license:
            return mapped_license

        known_license = self.state.get_known_license(material)
        if known_license:
            return known_license

        if self.state.is_always_manual(license_):
            print "always manually look up project license for '%s'"%(license_)
            return self.prompt_add_known_project(material)

        return self.prompt_map_license_license(license_, material)

def lowercased_keys(d):
    # sanitize the keys to lower cased
    d_ = {}
    for k, v in d.iteritems():
        d_[k.lower()] = v
    return d_

def lowercased_set(d):
    d_ = set()
    for k in d:
        d_.add(k.lower())
    return d_

class FormatterState(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.known_project_licenses = {}
        self.license_mapping = {}
        self.never_license_mapping = set()
        self.load()

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                config = json.load(f)
                self.license_mapping = lowercased_keys(config.get("license_mapping", {}))
                self.known_project_licenses = lowercased_keys(config.get(
                    "known_project_licenses", {}))
                self.never_license_mapping = lowercased_set(set(
                    config.get("never_license_mapping", [])))
        except Exception as e:
            print "unable to load configuration, error = \n initialize config to default", e

    def save(self):
        with open(self.file_path, "w+") as f:
            json.dump(
                {
                    "license_mapping": self.license_mapping,
                    "known_project_licenses": self.known_project_licenses,
                    "never_license_mapping": list(self.never_license_mapping),
                },
                f,
                indent=4,
                sort_keys=True)

    def add_known_project(self, material, license_):
        print template_map_project_license % (material.name, license_)
        self.known_project_licenses[material.format.lower() + "/" +
                                    material.name.lower()] = license_
        self.save()

    def add_license_mapping(self, source_license, target_license):
        print template_map_license_license % (source_license, target_license)
        self.license_mapping[source_license.lower()] = target_license
        self.save()

    def add_never_license_mapping(self, source_license):
        print template_never_map % (source_license, )
        self.never_license_mapping.add(source_license.lower())
        self.save()

    def get_known_license(self, material):
        return self.known_project_licenses.get(material.format.lower() + "/" +
                                               material.name.lower())

    def get_license(self, license_):
        return self.license_mapping.get(license_.lower())

    def is_always_manual(self, license_):
        return license_.lower() in self.never_license_mapping

    def current_state(self):
        return template_progress % ('\n'.join(
            list(set(self.license_mapping.values()))))
