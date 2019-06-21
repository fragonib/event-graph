import getopt
import os
import subprocess
import sys

MVN_DEPENDENCY_TREE_COMMAND = ['mvn', 'dependency:tree']


class ConsoleColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
    print(ConsoleColor.OKBLUE + 'Options:' + ConsoleColor.ENDC)
    print(ConsoleColor.OKGREEN + '  Root folder: ' + ConsoleColor.ENDC + root_dir)
    print(ConsoleColor.OKGREEN + '  Marker file: ' + ConsoleColor.ENDC + marker_file)
    print(ConsoleColor.OKGREEN + '  Dependency name: ' + ConsoleColor.ENDC + dependency_name)
    print()

    # Find project dirs
    projects_dirs = find_projects(root_dir, marker_file)
    print(ConsoleColor.OKBLUE + 'Project dirs:' + ConsoleColor.ENDC)
    for project_dir in projects_dirs:
        print('  ' + project_dir)
    print()

    # Check project dependencies
    print(ConsoleColor.OKBLUE + 'Dependencies:' + ConsoleColor.ENDC)
    for project_dir in projects_dirs:
        print(ConsoleColor.OKGREEN + 'Project: ' + ConsoleColor.ENDC, project_dir)
        print()
        mvn_output = launch_maven_dependency(project_dir)
        dependencies = found_dependencies(mvn_output, dependency_name)
        for module, importer, target in dependencies:
            print('  module: {module}\n    - importer: {importer}\n    - target: {target}\n'
                  .format(module=module, importer=importer, target=target))
