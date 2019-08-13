---
short-description: Detailed instructions for installing hotdoc
...

# Installing

If there is a wheel for your platform (currently only on linux) you can simply do:

    python3 -m pip install hotdoc

# From source

## System-wide dependencies

### lxml

Hotdoc uses lxml, which depends on libxml2 and libxslt.

### pyyaml

Hotdoc uses pyyaml to parse yaml ‘front-matter’ metadata in markdown pages, it depends on libyaml.

### flex

flex is an optional dependency, which enables the C and GI extensions. See [][Build options] for more info.

### clang and llvm-config

Clang and llvm-config are runtime dependencies for the C extension. 

### glib and json-glib

The search extension is implemented in C, and index creation depends on [glib](https://developer.gnome.org/glib/) and [json-glib](https://developer.gnome.org/json-glib/).

### npm

The default theme requires `npm` to be built.

### Command-line install

On Fedora you can install all these dependencies with:

```
dnf install python3-devel libxml2-devel libxslt-devel cmake libyaml-devel clang-devel llvm-devel glib2-devel json-glib-devel flex npm
```

And on ubuntu / debian:

```
apt-get install python3-dev libxml2-dev libxslt1-dev cmake libyaml-dev libclang-dev llvm-dev libglib2.0-dev libjson-glib-dev flex nodejs
```

We'll be happy to merge updates to this list if you have successfully built hotdoc on another platform.

## Creating a virtualenv

It is highly recommended to use a virtual env to try out any new python project, and hotdoc is no exception. You can however skip this step if you really do not
mind installing hotdoc system-wide.

> Assuming [pip](https://pip.pypa.io/en/stable/) is installed

```
python3 -m pip install virtualenv
python3 -m venv hotdoc_env
. hotdoc_env/bin/activate
```

You are now in a virtual environment, to exit it you may call `deactivate`, to enter it again simply call `. hotdoc_env/bin/activate` from the directory in which the environment was created.

## Build in development mode

```
meson build/ -Dprefix=$(python3 -c "import sys; print(sys.prefix)") -Dlibdir=lib
ninja -C build develop
```

## Build options

See options running:

    meson configure

To pass extra meson options when building with pip, you should set the `MESON_ARGS` environment variable,
like:

  MESON_ARGS="-Dc-extension=enabled` pip install .

This awkward way of passing options is due to current limitation in pip pep517 implementation.