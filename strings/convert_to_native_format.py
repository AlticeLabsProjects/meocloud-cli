#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

APP_NAME = 'MEO Cloud'

class ParserError(Exception):
    pass

def fill_app_name(line):
    return line.replace('APP_NAME', APP_NAME)

def string_to_darwin(line):
    return line.replace('%S', '%@') + ';'

def string_to_win32(line):
    strings_found = 0
    line_len = len(line)
    fmt_strs_found = 0
    newline = ''
    for i, char in enumerate(line):
        if char == '%' and i < line_len - 1 and line[i + 1] == 'S':
            fmt_strs_found += 1
            newline += '%' + str(fmt_strs_found)
        elif char == 'S' and i > 0 and line[i - 1] == '%':
            continue
        else:
            newline += char
    return newline

def string_to_linux(line):
    assert '=' in line
    key, _, value = line.partition('=')
    key = key.strip(' ')[1:-1]
    value = value.strip(' ')[1:-1]
    # escape '
    value = value.replace("'", "\\'")
    # unescape "
    value = value.replace('\\"', '"')
    value = value.replace('{', '{{')
    value = value.replace('}', '}}')
    value_parts = []
    for i, part in enumerate(value.split('%S')):
        value_parts.append(part)
        value_parts.append('{' + str(i) + '}')
    value = ''.join(value_parts[:-1])
    return "        '{0}': '{1}',".format(key, value)

def parse(infile, outfile, platform):
    for line in infile:
        # Remove newline
        line = line.strip('\n')

        if not line:
            outfile.write('\n')
            continue
        # Ignore comments
        if line.startswith('#'):
            continue
        line = fill_app_name(line)
        for stage in conversion_pipeline[platform]:
            line = stage(line)
        outfile.write(line + '\n')

conversion_pipeline = {
    'darwin': [string_to_darwin],
    'win32': [string_to_win32],
    'linux2': [string_to_linux],
    'linux': [string_to_linux],
}

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: {0} <infile> <outfile> [platform]'.format(sys.argv[0]))
        sys.exit(1)

    try:
        infile = open(sys.argv[1], 'r')
    except OSError as oerr:
        print('Could not open input file: {0}'.format(oerr))
        sys.exit(1)

    try:
        outfile = open(sys.argv[2], 'w')
    except OSError as oerr:
        print('Could not open output file: {1}'.format(oerr))
        sys.exit(1)

    if len(sys.argv) == 4:
        platform = sys.argv[3]
    else:
        platform = sys.platform

    parse(infile, outfile, platform)

    print('All done. Have a nice day')

