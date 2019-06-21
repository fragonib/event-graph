import getopt
import os
import subprocess
import sys
from blessings import Terminal

MVN_DEPENDENCY_TREE_COMMAND = ['mvn', 'dependency:tree']

term = Terminal()


def parse_options(args):
    root_dir = None
    marker_file = None
    optlist, args = getopt.getopt(args, 'f:m:d:', '["folder=", "marker=", "dependency="]')
    for o, a in optlist:
        if o in ("-f", "--folder"):
            root_dir = a
        if o in ("-m", "--marker"):
            marker_file = a
        if o in ("-d", "--dependency"):
            dependency_name = a
    return root_dir, marker_file, dependency_name


def find_projects(root_dir, marker_file):
    candidates = []
    for dirName, subdirList, fileList in os.walk(root_dir):
        if marker_file in fileList:
            del subdirList[:]
            candidates.append(dirName)
    return candidates


def launch_maven_dependency(command_folder):
    result = subprocess.run(MVN_DEPENDENCY_TREE_COMMAND, cwd=command_folder, stdout=subprocess.PIPE)
    mvn_output = result.stdout.decode('utf-8')
    return mvn_output


def found_dependencies(mvn_output, dependency_name):
    dependencies = []
    for line in mvn_output.splitlines():

        if line.startswith('[INFO] Building'):
            module = line.split()[2]

        if line.startswith('[INFO] +-') or line.startswith('[INFO] \\-'):
            importer = line.split()[2]

        index = line.find(dependency_name)
        if index != -1:
            target = line[index:]
            dependencies.append((module, importer, target))

    return dependencies


if __name__ == '__main__':

    # Parse CLI options
    root_dir, marker_file, dependency_name = parse_options(sys.argv[1:])
    print(term.blue('Options:'))
    print(term.green('  Root folder: ') + root_dir)
    print(term.green('  Marker file: ') + marker_file)
    print(term.green('  Dependency name: ') + dependency_name)
    print()

    # Find project dirs
    projects_dirs = find_projects(root_dir, marker_file)
    print(term.blue('Found projects:'))
    for project_dir in projects_dirs:
        print('  ' + project_dir)
    print()

    # Check project dependencies
    print(term.blue('Dependencies:'))
    for project_dir in projects_dirs:
        print(term.green('Project: ') + project_dir)
        print()
        mvn_output = launch_maven_dependency(project_dir)
        dependencies = found_dependencies(mvn_output, dependency_name)
        for module, importer, target in dependencies:
            print('  module: {module}\n    - importer: {importer}\n    - target: {target}\n'
                  .format(module=module, importer=importer, target=target))
