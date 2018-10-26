import json
import os
from subprocess import check_output
from email.parser import Parser

pip_command = "cat requirements.txt | grep -v \"^-e\" | awk -F'==' '{print $1}' | xargs pip --disable-pip-version-check show"
npm_command = "license-checker --json --excludePrivatePackages"

npm_debug_file = "npm-debug.json"
pip_debug_file = "pip-debug.txt"

config_file = "bill_of_materials.config.json"
bill_of_materials_file_path = "bill-of-materials1.json"

bill_of_materials = []
known_project_licenses = {}
license_mapping = {}
never_license_mapping = set()
npm_progress = (0, 0)
pip_progress = (0, 0)


def add_bill_of_materials(project_name, project_license, project_format):
  d = {"project": project_name, "license": project_license, "format": project_format}

  for project in bill_of_materials:
    if project == d:
      return

  bill_of_materials.append(d)


def add_known_project(pformat, name, project_license):
  print "map project '%s' to license '%s'" % (name, project_license)
  known_project_licenses[pformat + "/" + name] = project_license
  save_config()


def add_license_mapping(source_license, target_license):
  print "map license '%s' to '%s'" % (source_license, target_license)
  license_mapping[source_license] = target_license
  save_config()


def add_never_license_mapping(source_license):
  print "never map license '%s'" % (source_license,)
  never_license_mapping.add(source_license)
  save_config()


def save_config():
  with open("bill_of_materials.config.json", "w+") as f:
    json.dump({
      "license_mapping": license_mapping,
      "known_project_licenses": known_project_licenses,
      "never_license_mapping": list(never_license_mapping),
    }, f)


def open_config():
  try:
    global license_mapping, known_project_licenses, never_license_mapping
    with open(config_file, "r") as f:
      config = json.load(f)
      license_mapping = config.get("license_mapping", {})
      known_project_licenses = config.get("known_project_licenses", {})
      never_license_mapping = set(config.get("never_license_mapping", []))
  except Exception:
    pass


def map_license_to_specific_project(format_, name_):
  license_ = raw_input("%s has license >" % (name_,))
  add_known_project(format_, name_, license_)
  return license_


def get_known_project(format_, name_):
  return known_project_licenses.get(format_ + "/" + name_, None)


def map_license(format_, license_, name_, link_):
  license_ = license_.lower()

  if license_ in license_mapping:
    return license_mapping[license_]

  known_license = get_known_project(format_, name_)
  if known_license:
    return known_license

  existing_target_licenses = list(set(license_mapping.values()))
  print """
Progress: NPM %s, PIP %s
Existing mapping to:
%s
%s Project: '%s', License: '%s'
Link:   '%s'""" % (npm_progress, pip_progress, ','.join(existing_target_licenses), format_, name_,
                   license_, link_)

  if license_ in never_license_mapping:
    return map_license_to_specific_project(format_, name_)

  raw = raw_input("""
Unknown license '%s',
1. Enter the desired license name shown to user
2. Enter '=' to keep same name
3. Enter 'x' to always manually set the license for this unknown license
4. Leave empty to manually set the license for this specific project
>""" % (license_,))

  if raw == "x":
    add_never_license_mapping(license_)

  if raw == "" or raw == "x":
    return map_license_to_specific_project(format_, name_)

  if raw == "=":
    raw = license_

  add_license_mapping(license_, raw)
  return raw


def _get_npm_package_licenses():
  global npm_progress
  # precondition: license-checker is installed and in shell PATH
  # current directory is root directory
  output = check_output(npm_command, shell=True, env=os.environ)
  with open(npm_debug_file, "w+") as f:
    f.write(output)

  jsDict = json.loads(output)
  print "npm: found %d packages" % (len(jsDict),)
  counter = 0
  for name, details in jsDict.iteritems():
    counter += 1
    npm_progress = (counter, len(jsDict))
    name = ''.join(name.split("@")[:-1])  # remove version
    licenses = details["licenses"]
    link = details.get("repository", details.get("url", ""))
    corrected_license = ""

    if isinstance(licenses, list):
      corrected_licenses = []
      for l in licenses:
        corrected_licenses.append(map_license("Javascript", l, name, link))
      corrected_license = " and ".join(corrected_license)
    else:
      corrected_license = map_license("Javascript", licenses, name, link)

    add_bill_of_materials(name, corrected_license, "JavaScript")


def _get_pip_package_licenses():
  global pip_progress
  # precondition:
  # PIP is referring to the current repo's Python libraries.
  # Current directory must be the same directory as the project root directory.
  output = check_output("which pip", shell=True, env=os.environ)
  raw_input("Ensure the PIP path is correct: %s\nPress Enter to continue\n" % (output,))

  output = check_output(pip_command, shell=True, env=os.environ)
  with open(pip_debug_file, "w+") as f:
    f.write(output)

  rawProjects = output.split("---\n")
  parser = Parser()
  print "pip: found %d packages"%(len(rawProjects),)
  counter = 0
  for raw_project in rawProjects:
    counter += 1
    pip_progress = (counter, len(rawProjects))
    parsed_project = parser.parsestr(raw_project)
    name, license_, link = parsed_project["name"], parsed_project["license"], parsed_project.get(
      "Home-page", "")
    license_ = map_license("Python", license_, name, link)
    add_bill_of_materials(name, license_, "Python")


if __name__ == '__main__':
  open_config()
  _get_npm_package_licenses()
  _get_pip_package_licenses()
  with open(bill_of_materials_file_path, "w+") as bill_of_materials_file:
    json.dump(bill_of_materials, bill_of_materials_file)
  print "saved total %d package licenses"%(len(bill_of_materials),)
