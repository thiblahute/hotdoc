#!/usr/bin/env python3

import os
import shutil
import argparse

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('site_package')
    PARSER.add_argument('builddir')
    PARSER.add_argument('bindir')
    PARSER.add_argument('hotdoc')

    OPTIONS = PARSER.parse_args()
    with open(os.path.join(OPTIONS.site_package, 'hotdoc.egg-link'), 'w') as f:
        f.write(OPTIONS.builddir + '\n')

    with open(os.path.join(OPTIONS.site_package, 'easy-install.pth'), 'a') as f:
        f.write(OPTIONS.builddir + '\n')

    print('Copying %s to %s' % (OPTIONS.hotdoc, os.path.join(OPTIONS.bindir, 'hotdoc')))
    shutil.copy(OPTIONS.hotdoc, os.path.join(OPTIONS.bindir, 'hotdoc'))
