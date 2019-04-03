import os
import re

from .constants import *


def reduce(string):
    return re.sub(r'\s+', ' ', string)


def sanitize(string):
    return reduce(string.strip())


def fullname(filename):
    return ''.join((filename, '.', EXT))


def readfile(filename):
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), fullname(filename))
    with open(filepath, 'r') as handle:
        return handle.readlines()


def writefile(filename, content, directory=''):
    OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), OUTPUT_FOLDER, directory)

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    with open(os.path.join(OUTPUT_PATH, filename), 'w+t') as handle:
        handle.write(content)


def sanitize_list(dirty):
    clean = []
    for item in dirty:
        sanitized = sanitize(item)
        if sanitized:
            clean.append(sanitized)
    return clean


def capitalize_word(target):
    _word = ''
    words = target.split('_')
    for word in words:
        _word += word.capitalize()

    return _word


def kabab_word(target):
    target = target.replace('_', '-')
    matches = re.findall(r'([A-Z])', target)
    for match in matches:
        target = target.replace(match, '-%s' % match.lower())

    return target.lower().strip('-')
