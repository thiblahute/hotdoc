ln = '''import sys
import os
sys.path.append(os.path.join('@0@', '../', '..'))
print(sys.path, file=sys.stderr)
from hotdoc.utils.setup_utils import symlink
symlink(sys.argv[1], sys.argv[2])
'''.format(meson.current_source_dir())

foreach dir: ['extensions', 'core', 'utils']
    install_subdir(dir, install_dir: python.get_install_dir(pure: false) / 'hotdoc')
    res = run_command(python, '-c', ln, meson.current_source_dir() / dir, meson.current_build_dir() / dir)
    if res.returncode() != 0
        error('Could not create symlinks:\n @0@'.format(res.stderr()))
    endif
endforeach

foreach f: ['hotdoc_dep_printer.py', '__init__.py', 'run_hotdoc.py', 'VERSION.txt']
    python.install_sources(f, pure: false, subdir: 'hotdoc')
    res = run_command(python, '-c', ln, meson.current_source_dir() / f, meson.current_build_dir() / f)
    if res.returncode() != 0
        error('Could not create symlinks:\n @1@\n@0@'.format(res.stdout(), res.stderr()))
    endif
endforeach

subdir('parsers')