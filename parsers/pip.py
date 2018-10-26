import os
from subprocess import check_output
from email.parser import Parser
from bill_of_materials import Material

pip_binary = "/Users/sidchen/.pyenv/versions/2.7.12/envs/quay/bin/pip"
requirements_txt = "/Users/sidchen/Dev/quay/requirements.txt"
pip_command = "cat %s | grep -v \"^-e\" | awk -F'==' '{print $1}' | xargs %s --disable-pip-version-check show" % (
    requirements_txt, pip_binary)
pip_debug_file = "pip-debug.txt"
format_python = "Python"

def get():
    output = check_output(pip_command, shell=True, env=os.environ)
    with open(pip_debug_file, "w+") as f:
        f.write(output)

    rawProjects = output.split("---\n")
    parser = Parser()
    print "pip: found %d packages" % (len(rawProjects), )
    for raw_project in rawProjects:
        parsed_project = parser.parsestr(raw_project)
        yield Material(parsed_project["name"], parsed_project[
            "license"], format_python, parsed_project.get("Home-page", ""))
