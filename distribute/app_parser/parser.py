from .ipa_parser import IpaParser
from .apk_parser import ApkParser

def parse(fd, ext, os=None, platform=None):
    parser_list = [IpaParser, ApkParser]
    for p in parser_list:
        if p.can_parse(ext, os, platform):
            return p(fd)
    return None
    