import json, os
from subprocess import check_output
from bill_of_materials import Material

npm_licence_checker_binary = "/usr/local/bin/license-checker"
package_json_including_folder = "/Users/sidchen/Dev/quay/"
npm_command = "cd %s && %s --json --excludePrivatePackages" % (
    package_json_including_folder, npm_licence_checker_binary)
npm_debug_file = "npm-debug.json"
format_javascript = "Javascript"


def get():
    output = check_output(npm_command, shell=True, env=os.environ)
    with open(npm_debug_file, "w+") as f:
        f.write(output)

    jsDict = json.loads(output)
    print "npm: found %d packages" % (len(jsDict), )
    for name, details in jsDict.iteritems():
        yield Material(''.join(name.split("@")[:-1]), details["licenses"], format_javascript, details.get("repository", details.get("url", "")))
