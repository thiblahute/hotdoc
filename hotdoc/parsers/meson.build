subdir('c_comment_scanner')

python.extension_module('cmark',
    'cmark_module.c',
    'cmark_gtkdoc_extension.c',
    'cmark_gtkdoc_scanner.c',
    'cmark_include_extension.c',
    'cmark_include_scanner.c',
    dependencies: [python.dependency(), cmark_dep, cmarkextension_dep])

glib_dep = dependency('glib-2.0', fallback: ['glib', 'libglib_dep'])
json_glib_dep = dependency('glib-2.0', fallback: ['glib', 'libglib_dep'])
json_dep = dependency('json-glib-1.0',
    fallback : ['json-glib', 'json_glib_dep'])
libxml_dep = dependency('libxml-2.0', fallback: ['libxml2', 'libxml_dep'])

python.extension_module('search',
    'search_module.c',
    'trie.c',
    dependencies: [python.dependency(), glib_dep, json_dep, libxml_dep])

foreach f: ['cmark_utils.py', 'gtk_doc.py', '__init__.py', 'sitemap.py',]
    python.install_sources(f, pure: false, subdir: 'hotdoc/parsers')
    res = run_command(python, '-c', ln, meson.current_source_dir() / f, meson.current_build_dir() / f)
    if res.returncode() != 0
        error('Could not create symlinks:\n @0@'.format(res.stderr()))
    endif
endforeach