#!/usr/bin/env python3
#
# swiftbuild
#
# A simple tool to build (or test) one or more Swift projects using a single
# command.
#
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse
import pathlib
import os
import subprocess

def swiftbuild(test, run, packages, swiftc_options):
    # Process the package directories.

    results = ()
    num_packages_found = 0
    for dir in packages:
        if dir.exists() and dir.is_dir():
            path = dir.expanduser().resolve()
            output, is_package = build_package(test, run, path, swiftc_options)
            if is_package:
                num_packages_found = num_packages_found + 1
                results = results + ((path, output),)
#            else:
#                print(f"Directory {path} is not a Swift project. Skipping.")

    # Display a table of build results.

    if num_packages_found != 0:
        print("{0: <65} {1}".format("Example", "Status"))
        print("-"*65, "-"*6)

    fails = 0
    for result in results:
        outcome_str = "OK"
        (path, value) = result

        if value != 0:
            fails = fails + 1
            outcome_str = "Fail"

        num_parts = len(path.parts)
        parent = path.parts[num_parts - 2] if num_parts > 1 else ""
        short_path = f"{parent}{os.sep}{path.name}"

        short_path = str(short_path)
        short_path_len = len(short_path)
        if short_path_len > 64:
            short_path = f"...{short_path[-61:]}"
        print("{0:.<65} {1}".format(f"{short_path} ", outcome_str))

    print(f"\nBuilt {num_packages_found} project(s) with {fails} failure(s).")
    print_configuration(test, swiftc_options)

def print_configuration(test, swiftc_options):
    # print(f"Built project(s) {with_tests}")
    print("Build configuration:")
    count = len(swiftc_options)

    if test:
        print("    Tests enabled")

    if count > 0:
        for opt in swiftc_options:
            print(f"    {opt}")
    elif not test:
        print("    None")

# Build one package, given a specific directory. Build and test
# if the `test` argument is True.
#
# Returns the returncode from the `swift` command.
def build_package(test, run, package, swiftc_options):
    packagefile_path = package / "Package.swift"
    if not packagefile_path.is_file():
        is_package = False

        return 1, is_package

    if test == True:
        build_command = "test"
        command_gerund = "testing"
    elif run == True:
        build_command = "run"
        command_gerund = "running"
    else:
        build_command = "build"
        command_gerund = "building"

    command_parts = ["swift", build_command]

    for opt in swiftc_options:
        command_parts = command_parts + ["-Xswiftc", opt]

    print(f"Now {command_gerund} project in {package}...")
    # print(command_parts)

    results = subprocess.run(command_parts, cwd=package)
    print("="*72, "\n")
    return results.returncode, True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build (and optionally test) one or more Swift projects.")
    parser.add_argument("-r", "--run", action="store_true", help="build and run each project", dest="run")
    parser.add_argument("-t", "--test", action="store_true", help="run tests on projects after building them")
    parser.add_argument("-p", "--parseable", action="store_true", help="enable parseable output", dest="parseable")
    parser.add_argument("-w", "--hide-warnings", action="store_true", help="hide build warnings", dest="hide_warnings")
    parser.add_argument("packages", metavar="PACKAGE_DIR", type=pathlib.Path, nargs="*", default="*", help="Directory of a project to build.")

    args = parser.parse_args()

    # Build swiftc command line option list

    swiftc_options = []

    if args.hide_warnings:
        swiftc_options.append("-suppress-warnings")
    if args.parseable:
        swiftc_options.append("-parseable-output")

    swiftbuild(args.test, args.run, args.packages, swiftc_options)
