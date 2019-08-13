foreach dir: ['extensions', 'core', 'utils', 'tests']
    install_subdir(dir, install_dir: python.get_install_dir(pure: false) / 'hotdoc')
    to_symlink += [[meson.current_source_dir() / dir, meson.current_build_dir() / dir]]
endforeach

foreach f: ['hotdoc_dep_printer.py', '__init__.py', 'run_hotdoc.py', 'VERSION.txt']
    python.install_sources(f, pure: false, subdir: 'hotdoc')
    to_symlink += [[meson.current_source_dir() / f, meson.current_build_dir() / f]]
endforeach

subdir('parsers')