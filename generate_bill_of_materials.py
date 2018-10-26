import json
import os
from subprocess import check_output
from email.parser import Parser

pip_binary = "/Users/sidchen/.pyenv/versions/2.7.12/envs/quay/bin/pip"
npm_licence_checker_binary = "/usr/local/bin/license-checker"
requirements_txt = "/Users/sidchen/Dev/quay/requirements.txt"
package_json_including_folder = "/Users/sidchen/Dev/quay/"

pip_command = "cat %s | grep -v \"^-e\" | awk -F'==' '{print $1}' | xargs %s --disable-pip-version-check show" % (
  requirements_txt, pip_binary)
npm_command = "cd %s && %s --json --excludePrivatePackages" % (package_json_including_folder,
                                                               npm_licence_checker_binary)

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

format_javascript = "Javascript"
format_python = "Python"

template_choice = """
Unknown license '%s',
1. Enter the desired license name shown to user
2. Enter '=' to keep same name
3. Enter 'x' to always manually set the license for this unknown license
4. Leave empty to manually set the license for this specific project
>"""
template_progress = """
Progress: NPM %s, PIP %s
Existing mapping to:
%s
%s Project: '%s', License: '%s'
Link:   '%s'"""
template_map_project_license = "map project '%s' to license '%s'"
template_map_license_license = "map license '%s' to license '%s'"
template_never_map = "never map license '%s'"


def add_bill_of_materials(project_name, project_license, project_format):
  d = {"project": project_name, "format": project_format, "license": project_license}

  for project in bill_of_materials:
    if project == d:
      return

  bill_of_materials.append(d)


def add_known_project(pformat, name, project_license):
  print template_map_project_license % (name, project_license)
  known_project_licenses[pformat + "/" + name] = project_license
  save_config()


def add_license_mapping(source_license, target_license):
  print template_map_license_license % (source_license, target_license)
  license_mapping[source_license] = target_license
  save_config()


def add_never_license_mapping(source_license):
  print template_never_map % (source_license,)
  never_license_mapping.add(source_license)
  save_config()


def save_config():
  with open("bill_of_materials.config.json", "w+") as f:
    json.dump({
      "license_mapping": license_mapping,
      "known_project_licenses": known_project_licenses,
      "never_license_mapping": list(never_license_mapping),
    }, f, indent=4, sort_keys=True)


def open_config():
  try:
    global license_mapping, known_project_licenses, never_license_mapping
    with open(config_file, "r") as f:
      config = json.load(f)
      license_mapping = config.get("license_mapping", {})
      known_project_licenses = config.get("known_project_licenses", {})
      never_license_mapping = set(config.get("never_license_mapping", []))
  except Exception as e:
    print "unable to load configuration, error = \n initialize config to default", e


def map_license_to_specific_project(format_, name_):
  license_ = raw_input("%s has license >" % (name_,))
  if license_ in license_mapping:
    license_ = license_mapping[license_]

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
  print template_progress % (npm_progress, pip_progress, ','.join(existing_target_licenses),
                             format_, name_, license_, link_)

  if license_ in never_license_mapping:
    return map_license_to_specific_project(format_, name_)

  raw = raw_input(template_choice % (license_,))

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
        corrected_licenses.append(map_license(format_javascript, l, name, link))
      corrected_license = " and ".join(corrected_licenses)
      print corrected_license, licenses
    else:
      corrected_license = map_license(format_javascript, licenses, name, link)

    add_bill_of_materials(name, corrected_license, format_javascript)


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
  print "pip: found %d packages" % (len(rawProjects),)
  counter = 0
  for raw_project in rawProjects:
    counter += 1
    pip_progress = (counter, len(rawProjects))
    parsed_project = parser.parsestr(raw_project)
    name, license_, link = parsed_project["name"], parsed_project["license"], parsed_project.get(
      "Home-page", "")
    license_ = map_license(format_python, license_, name, link)
    add_bill_of_materials(name, license_, format_python)

def sort_key(e):
  prefix = "0"
  if e["format"] == "Javascript":
    prefix = "1"
  return prefix + e["project"].lower()

if __name__ == '__main__':
  open_config()
  _get_npm_package_licenses()
  _get_pip_package_licenses()
  with open(bill_of_materials_file_path, "w+") as bill_of_materials_file:
    bill_of_materials.sort(key=sort_key)
    json.dump(bill_of_materials, bill_of_materials_file, indent=4, sort_keys=True)
  print "saved total %d package licenses" % (len(bill_of_materials),)

