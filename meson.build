project(
    'hotdoc',
    'c',
    version : '0.8.101',
    meson_version : '>= 0.51.0',
    license: 'LGPL2+',
)

python = import('python').find_installation(get_option('python'))

cmake = import('cmake')
sub_proj = cmake.subproject('cmark')
cmark_dep = sub_proj.dependency('libcmark')
cmarkextension_dep = sub_proj.dependency('cmarkextensions')

subdir('hotdoc')
subproject('hotdoc_bootstrap_theme')

cdata = configuration_data()
cdata.set('PYTHON', python.path())
cdata.set('BUILDPATH', meson.current_build_dir())
configure_file(input: 'hotdoc.py.in', output : 'hotdoc.py', configuration : cdata)
