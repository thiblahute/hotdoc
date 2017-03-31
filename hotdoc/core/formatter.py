# -*- coding: utf-8 -*-
#
# Copyright © 2015,2016 Mathieu Duponchelle <mathieu.duponchelle@opencreed.com>
# Copyright © 2015,2016 Collabora Ltd
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

"""
The base formatter module.

By design, hotdoc only supports html output.
"""

import os
import html
import re
import urllib.parse
import shutil

from collections import defaultdict, namedtuple

from lxml import etree
import lxml.html

# pylint: disable=import-error
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.ext.code import CodeExtension
from wheezy.template.loader import FileLoader
from schema import Schema, Optional

from hotdoc.core.tree import Page
from hotdoc.core.symbols import\
    (FunctionSymbol, CallbackSymbol, ParameterSymbol,
     ReturnItemSymbol, FieldSymbol, QualifiedSymbol,
     FunctionMacroSymbol, ConstantSymbol, ExportedVariableSymbol,
     StructSymbol, EnumSymbol, AliasSymbol, SignalSymbol, PropertySymbol,
     VFunctionSymbol, ClassSymbol, InterfaceSymbol)
from hotdoc.core.links import Link
from hotdoc.parsers.gtk_doc import GtkDocStringFormatter
from hotdoc.utils.utils import (
    OrderedSet, id_from_text, recursive_overwrite, symlink)
from hotdoc.core.exceptions import HotdocException
from hotdoc.utils.loggable import Logger, warn, debug
from hotdoc.utils.configurable import Configurable
from hotdoc.utils.signals import Signal


Page.meta_schema[Optional('extra', default=defaultdict())] = \
    Schema({str: object})


class FormatterBadLinkException(HotdocException):
    """
    Raised when a produced html page contains an empty local link
    to nowhere.
    """
    pass


Logger.register_warning_code('bad-local-link', FormatterBadLinkException,
                             domain='html-formatter')
Logger.register_warning_code('no-image-src', FormatterBadLinkException,
                             domain='html-formatter')
Logger.register_warning_code('bad-image-src', FormatterBadLinkException,
                             domain='html-formatter')


HERE = os.path.dirname(__file__)


# pylint: disable=too-few-public-methods
class TocSection(object):
    """
    Banana banana
    """

    def __init__(self, summaries, name):
        self.summaries = summaries
        self.name = name
        self.id_ = ''.join(name.split())


# pylint: disable=too-few-public-methods
class SymbolDescriptions(object):
    """
    Banana banana
    """

    def __init__(self, descriptions, name):
        self.descriptions = descriptions
        self.name = name


# pylint: disable=too-many-instance-attributes
class Formatter(Configurable):
    """
    Takes care of rendering the documentation symbols and comments into HTML
    pages.
    """
    theme_path = None
    extra_theme_path = None
    add_anchors = False
    number_headings = False

    def __init__(self, extension, searchpath):
        """
        Args:
            extension (`extension.Extension`): The extension instance.
            searchpath (str): Path where templates live.
        """
        Configurable.__init__(self)

        self.extension = extension

        self._symbol_formatters = {
            FunctionSymbol: self._format_function,
            FunctionMacroSymbol: self._format_function_macro,
            CallbackSymbol: self._format_callback,
            ConstantSymbol: self._format_constant,
            ExportedVariableSymbol: self._format_constant,
            AliasSymbol: self._format_alias,
            StructSymbol: self._format_struct,
            EnumSymbol: self._format_enum,
            ParameterSymbol: self._format_parameter_symbol,
            ReturnItemSymbol: self._format_return_item_symbol,
            FieldSymbol: self._format_field_symbol,
            SignalSymbol: self._format_signal_symbol,
            VFunctionSymbol: self._format_vfunction_symbol,
            PropertySymbol: self._format_property_symbol,
            ClassSymbol: self._format_class_symbol,
            InterfaceSymbol: self._format_interface_symbol,
        }

        self._ordering = [InterfaceSymbol, ClassSymbol, FunctionSymbol,
                          FunctionMacroSymbol, SignalSymbol,
                          PropertySymbol, StructSymbol,
                          VFunctionSymbol, EnumSymbol, ConstantSymbol,
                          ExportedVariableSymbol, AliasSymbol, CallbackSymbol]

        self.all_scripts = set()
        self.all_stylesheets = set()
        self._docstring_formatter = self._make_docstring_formatter()
        self._current_page = None
        self.engine = None
        self.extra_assets = None
        self.add_anchors = False
        self.number_headings = False
        self.searchpath = searchpath
        self.writing_page_signal = Signal()
        self.formatting_page_signal = Signal()
        self.get_extra_files_signal = Signal()
        self.formatting_symbol_signal = Signal()
        self.engine = None
        self._order_by_parent = False

    def _make_docstring_formatter(self):  # pylint: disable=no-self-use
        return GtkDocStringFormatter()

    # pylint: disable=no-self-use
    def _get_assets_path(self):
        """
        Banana banana
        """
        return 'assets'

    def format_symbol(self, symbol, link_resolver):
        """
        Format a symbols.Symbol
        """
        if not symbol:
            return ''

        for csym in symbol.get_children_symbols():
            self.format_symbol(csym, link_resolver)

        res = self.formatting_symbol_signal(self, symbol)

        if False in res:
            return False

        symbol.formatted_doc = self.format_comment(symbol.comment,
                                                   link_resolver)
        # pylint: disable=unused-variable
        out, standalone = self._format_symbol(symbol)
        symbol.detailed_description = out

        return symbol.detailed_description

    # pylint: disable=too-many-function-args
    def format_comment(self, comment, link_resolver):
        """Format a comment

        Args:
            comment: hotdoc.core.comment.Comment, the code comment
            to format. Can be None, in which case the empty string will
            be returned.
        Returns:
            str: The formatted comment.
        """
        if comment:
            return self._format_comment(comment, link_resolver)
        return ''

    def __copy_extra_assets(self, output):
        paths = []
        for src in self.extra_assets or []:
            dest = os.path.join(output, os.path.basename(src))

            destdir = os.path.dirname(dest)
            if not os.path.exists(destdir):
                os.makedirs(destdir)

            if os.path.isdir(src):
                recursive_overwrite(src, dest)
            elif os.path.isfile(src):
                shutil.copyfile(src, dest)
            paths.append(dest)

        return paths

    def __copy_assets(self, assets_path):
        if not os.path.exists(assets_path):
            os.mkdir(assets_path)

        extra_files = self._get_extra_files()

        for ex_files in self.get_extra_files_signal(self):
            extra_files.extend(ex_files)

        for src, dest in extra_files:
            dest = os.path.join(assets_path, dest)

            destdir = os.path.dirname(dest)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            if os.path.isfile(src):
                shutil.copy(src, dest)
            elif os.path.isdir(src):
                recursive_overwrite(src, dest)

    def __copy_extra_files(self, root, page_folder):
        self.__copy_assets(os.path.join(root, 'html', 'assets'))
        extra_assets_paths = self.__copy_extra_assets(page_folder)

        root = os.path.join(root, 'html')
        if root != page_folder:
            relpath = os.path.relpath(root, page_folder)
            for path in ['assets'] + extra_assets_paths:
                try:
                    basename = os.path.basename(path)
                    symlink(os.path.join(relpath, basename),
                            os.path.join(page_folder, basename))
                except OSError:
                    pass

    def patch_page(self, page, symbol):
        """
        Subclasses should implement this in order to allow
        live patching of the documentation.
        """
        raise NotImplementedError

    def format_page(self, page):
        """
        Banana banana
        """
        self.formatting_page_signal(self, page)
        return self._format_page(page)

    # pylint: disable=no-self-use
    def __load_theme_templates(self, searchpath, path):
        theme_templates_path = os.path.join(path, 'templates')

        if os.path.exists(theme_templates_path):
            searchpath.insert(0, theme_templates_path)

    # pylint: disable=no-self-use
    def __init_section_numbers(self, root):
        if not Formatter.number_headings:
            return {}

        targets = []

        ctr = 0
        while len(targets) <= 1:
            ctr += 1
            if ctr > 5:
                return {}

            targets = root.xpath('.//*[self::h%s]' % ctr)

        section_numbers = {}
        for i in range(ctr, 6):
            section_numbers['h%d' % i] = 0

        section_numbers['first'] = ctr

        return section_numbers

    # pylint: disable=no-self-use
    def __update_section_number(self, target, section_numbers):
        if target.tag not in section_numbers:
            return None

        prev = section_numbers.get('prev')
        cur = int(target.tag[1])

        if cur < prev:
            for i in range(cur + 1, 6):
                section_numbers['h%d' % i] = 0

        section_numbers[target.tag] += 1
        section_numbers['prev'] = cur

        section_number = u''
        for i in range(section_numbers['first'], cur + 1):
            if section_number:
                section_number += '.'
            section_number += str(section_numbers['h%d' % i])

        return section_number

    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def write_page(self, page, build_root, output):
        """
        Banana banana
        """
        root = etree.HTML(str(page.detailed_description))
        id_nodes = {n.attrib['id']: "".join([x for x in n.itertext()])
                    for n in root.xpath('.//*[@id]')}

        section_numbers = self.__init_section_numbers(root)

        targets = root.xpath(
            './/*[self::h1 or self::h2 or self::h3 or '
            'self::h4 or self::h5 or self::img]')

        for target in targets:
            section_number = self.__update_section_number(
                target, section_numbers)

            if 'id' in target.attrib:
                continue

            if target.tag == 'img':
                text = target.attrib.get('alt')
            else:
                text = "".join([x for x in target.itertext()])

            if not text:
                continue

            id_ = id_from_text(text)
            ref_id = id_
            index = 1

            while id_ in id_nodes:
                id_ = '%s%s' % (ref_id, index)
                index += 1

            if section_number:
                target.text = '%s %s' % (section_number, target.text or '')

            target.attrib['id'] = id_
            id_nodes[id_] = text

        empty_links = root.xpath('.//a[not(text()) and not(*)]')
        for link in empty_links:
            href = link.attrib.get('href')
            if href and href.startswith('#'):
                title = id_nodes.get(href.strip('#'))
                if title:
                    link.text = title
                else:
                    warn('bad-local-link',
                         "Empty anchor link to %s in %s points nowhere" %
                         (href, page.source_file))
                    link.text = "FIXME broken link to %s" % href

        page.detailed_description = lxml.html.tostring(
            root, doctype="<!DOCTYPE html>", encoding='unicode',
            include_meta_content_type=True)

        full_path = os.path.join(output, self.get_output_folder(page),
                                 page.link.ref)

        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))

        self.writing_page_signal(self, page, full_path)

        with open(full_path, 'w') as _:
            _.write(page.detailed_description)

        self.__copy_extra_files(build_root, os.path.dirname(full_path))

        images = root.xpath('.//img')
        # All required assets should now be in place
        for img in images:
            src = img.attrib.get('src')
            if not src:
                warn('no-image-src',
                     'Empty image source in %s' % page.source_file)
                continue

            comps = urllib.parse.urlparse(src)
            if comps.scheme:
                continue

            path = os.path.abspath(os.path.join(
                os.path.dirname(full_path), src))
            if not os.path.exists(path):
                warn('bad-image-src',
                     ('In %s, a local image refers to an unknown source (%s). '
                      'It should be available in the build folder, at %s') %
                     (page.source_file, src, path))
                continue

        return full_path

    # pylint: disable=no-self-use
    def _get_extension(self):
        return "html"

    def get_output_folder(self, page):
        """
        Banana banana
        """
        if self.extension.project.is_toplevel:
            return ''

        return page.project_name

    def _format_link(self, link, title):
        out = ''
        if not link:
            assert link
            print("Issue here plz check", title)
            return title

        template = self.engine.get_template('link.html')
        out += '%s' % template.render({'link': link,
                                       'link_title': title})
        return out

    def _format_type_tokens(self, type_tokens):
        out = ''
        link_before = False

        for tok in type_tokens:
            if isinstance(tok, Link):
                ref = tok.get_link(self.extension.app.link_resolver)
                if ref:
                    out += self._format_link(ref, tok.title)
                    link_before = True
                else:
                    if link_before:
                        out += ' '
                    out += tok.title
                    link_before = False
            else:
                if link_before:
                    out += ' '
                out += tok
                link_before = False

        return out

    # pylint: disable=unidiomatic-typecheck
    def _format_linked_symbol(self, symbol):
        out = ""

        if isinstance(symbol, QualifiedSymbol):
            out += self._format_type_tokens(symbol.type_tokens)

        # FIXME : ugly
        elif hasattr(symbol, "link") and type(symbol) != FieldSymbol:
            out += self._format_link(
                symbol.link.get_link(self.extension.app.link_resolver),
                symbol.link.title)

        if type(symbol) == ParameterSymbol:
            out += ' ' + symbol.argname

        elif type(symbol) == FieldSymbol and symbol.member_name:
            out += self._format_type_tokens(symbol.qtype.type_tokens)
            template = self.engine.get_template('inline_code.html')
            member_name = template.render({'code': symbol.member_name})
            if symbol.is_function_pointer:
                out = member_name
                out += "()"
            else:
                out += ' ' + member_name

        return out

    def _format_callable_prototype(self, return_value, function_name,
                                   parameters, is_pointer):
        template = self.engine.get_template('callable_prototype.html')

        return template.render({'return_value': return_value,
                                'name': function_name,
                                'parameters': parameters,
                                'is_pointer': is_pointer})

    def __format_parameter_detail(self, name, detail, extra=None):
        extra = extra or {}
        template = self.engine.get_template('parameter_detail.html')
        return template.render({'name': name,
                                'detail': detail,
                                'extra': extra})

    def _format_symbol_descriptions(self, symbols_list):
        detailed_descriptions = []

        for element in symbols_list.symbols:
            if element.skip:
                continue
            if element.detailed_description:
                detailed_descriptions.append(element.detailed_description)

        symbol_type = symbols_list.name
        symbol_descriptions = None
        if detailed_descriptions:
            symbol_descriptions = SymbolDescriptions(
                detailed_descriptions, symbol_type)

        return symbol_descriptions

    def _format_struct(self, struct):
        raw_code = None
        if struct.raw_text is not None:
            raw_code = self._format_raw_code(struct.raw_text)

        members_list = self._format_members_list(struct.members, 'Fields')

        template = self.engine.get_template("struct.html")
        out = template.render({"symbol": struct,
                               "struct": struct,
                               "raw_code": raw_code,
                               "members_list": members_list})
        return (out, False)

    def _format_enum(self, enum):
        for member in enum.members:
            template = self.engine.get_template("enum_member.html")
            member.detailed_description = template.render({
                'link': member.link,
                'detail': member.formatted_doc,
                'value': str(member.enum_value)})

        raw_code = None
        if enum.raw_text is not None:
            raw_code = self._format_raw_code(enum.raw_text)
        members_list = self._format_members_list(enum.members, 'Members')
        template = self.engine.get_template("enum.html")
        out = template.render({"symbol": enum,
                               "enum": enum,
                               "raw_code": raw_code,
                               "members_list": members_list})
        return (out, False)

    def prepare_page_attributes(self, page):
        """
        Banana banana
        """
        self._current_page = page
        page.output_attrs['html']['scripts'] = OrderedSet()
        page.output_attrs['html']['stylesheets'] = OrderedSet()
        page.output_attrs['html']['extra_html'] = []
        page.output_attrs['html']['extra_footer_html'] = []
        if Formatter.add_anchors:
            page.output_attrs['html']['scripts'].add(
                os.path.join(HERE, 'assets', 'css.escape.js'))

    def __get_symbols_details(self, page, parent_name=None):
        symbols_details = []
        for symbols_type in self._ordering:
            if not self._order_by_parent:
                symbols_list = page.typed_symbols.get(symbols_type)
            else:
                symbols_list = page.by_parent_symbols[parent_name].get(
                    symbols_type)

            if not symbols_list:
                continue

            symbols_descriptions = self._format_symbol_descriptions(
                symbols_list)

            if symbols_descriptions:
                symbols_details.append(symbols_descriptions)
                if parent_name:
                    if len(symbols_list.symbols) == 1:
                        sym = symbols_list.symbols[0]
                        if sym.unique_name == parent_name:
                            symbols_descriptions.name = None

        return symbols_details

    # pylint: disable=too-many-locals
    def _format_page(self, page):
        symbols_details = []
        by_sections = []
        by_section_symbols = namedtuple('BySectionSymbols',
                                        ['name', 'symbols_details'])

        if not self._order_by_parent:
            symbols_details = self.__get_symbols_details(page)
        else:
            for parent_name in page.by_parent_symbols.keys():
                symbols_details = self.__get_symbols_details(page, parent_name)

                if symbols_details:
                    by_sections.append(by_section_symbols(
                        parent_name if parent_name else "Other symbols",
                        symbols_details))

        template = self.engine.get_template('page.html')

        scripts = []
        stylesheets = []

        if Formatter.extra_theme_path:
            js_dir = os.path.join(Formatter.extra_theme_path, 'js')
            try:
                for _ in os.listdir(js_dir):
                    scripts.append(os.path.join(js_dir, _))
            except OSError:
                pass

            css_dir = os.path.join(Formatter.extra_theme_path, 'css')
            try:
                for _ in os.listdir(css_dir):
                    stylesheets.append(os.path.join(css_dir, _))
            except OSError:
                pass

        scripts.extend(page.output_attrs['html']['scripts'])
        stylesheets.extend(page.output_attrs['html']['stylesheets'])
        scripts_basenames = [os.path.basename(script)
                             for script in scripts]
        stylesheets_basenames = [os.path.basename(stylesheet)
                                 for stylesheet in stylesheets]

        self.all_stylesheets.update(stylesheets)
        self.all_scripts.update(scripts)

        out = template.render(
            {'page': page,
             'source_file': os.path.basename(page.source_file),
             'scripts': scripts_basenames,
             'stylesheets': stylesheets_basenames,
             'assets_path': self._get_assets_path(),
             'extra_html': page.output_attrs['html']['extra_html'],
             'extra_footer_html':
             page.output_attrs['html']['extra_footer_html'],
             'symbols_details': symbols_details,
             'sections_details': by_sections,
             'in_toplevel': self.extension.project.is_toplevel}
        )

        return (out, True)

    def _format_prototype(self, function, is_pointer, title):
        if function.return_value:
            return_value = self._format_linked_symbol(function.return_value[0])
        else:
            return_value = None

        parameters = []
        for param in function.parameters:
            parameters.append(self._format_linked_symbol(param))

        return self._format_callable_prototype(return_value,
                                               title, parameters, is_pointer)

    def _format_raw_code(self, code):
        code = html.escape(code)
        template = self.engine.get_template('raw_code.html')
        return template.render({'code': code})

    def _format_parameter_symbol(self, parameter):
        return (self.__format_parameter_detail(
            parameter.argname,
            parameter.formatted_doc,
            extra=parameter.extension_contents), False)

    def _format_field_symbol(self, field):
        field_id = self._format_linked_symbol(field)
        template = self.engine.get_template('field_detail.html')
        return (template.render({'symbol': field,
                                 'name': field_id,
                                 'detail': field.formatted_doc}), False)

    def _format_return_item_symbol(self, return_item):
        template = self.engine.get_template('return_item.html')
        return_item.formatted_link = self._format_linked_symbol(return_item)
        return (template.render({'return_item': return_item}), False)

    def _format_return_value_symbol(self, return_value):
        template = self.engine.get_template('multi_return_value.html')
        if return_value[0] is None:
            return_value = return_value[1:]
        for rval in return_value:
            rval.extension_attributes['order_by_section'] = \
                self._order_by_parent
        return template.render({'return_items': return_value})

    def _format_callable(self, callable_, callable_type, title,
                         is_pointer=False):
        template = self.engine.get_template('callable.html')

        parameters = [p.detailed_description for p in callable_.parameters if
                      p.detailed_description is not None]

        prototype = self._format_prototype(callable_, is_pointer, title)

        return_value_detail = self._format_return_value_symbol(
            callable_.return_value)

        tags = {}
        if callable_.comment:
            tags = dict(callable_.comment.tags)

        tags.pop('returns', None)
        tags.pop('topic', None)

        out = template.render({'prototype': prototype,
                               'symbol': callable_,
                               'return_value': return_value_detail,
                               'parameters': parameters,
                               'callable_type': callable_type,
                               'tags': tags,
                               'extra': callable_.extension_contents})

        return (out, False)

    def _format_signal_symbol(self, signal):
        title = "%s_callback" % re.sub('-', '_', signal.link.title)
        return self._format_callable(signal, "signal", title)

    def _format_vfunction_symbol(self, vmethod):
        return self._format_callable(vmethod, "virtual method",
                                     vmethod.link.title)

    def _format_property_symbol(self, prop):
        type_link = self._format_linked_symbol(prop.prop_type)
        template = self.engine.get_template('property_prototype.html')
        prototype = template.render({'property_name': prop.link.title,
                                     'property_type': type_link})
        template = self.engine.get_template('property.html')
        res = template.render({'symbol': prop,
                               'prototype': prototype,
                               'property': prop,
                               'extra': prop.extension_contents})
        return (res, False)

    def _format_hierarchy(self, klass):
        hierarchy = []
        children = []
        for _ in klass.hierarchy:
            hierarchy.append(self._format_linked_symbol(_))
        for _ in klass.children.values():
            children.append(self._format_linked_symbol(_))

        if hierarchy or children:
            template = self.engine.get_template("hierarchy.html")
            hierarchy = template.render({'hierarchy': hierarchy,
                                         'children': children,
                                         'klass': klass})
        return hierarchy

    def _format_class_symbol(self, klass):
        hierarchy = self._format_hierarchy(klass)
        template = self.engine.get_template('class.html')
        raw_code = None
        if klass.raw_text is not None:
            raw_code = self._format_raw_code(klass.raw_text)

        for member in klass.members:
            self.format_symbol(member, self.extension.app.link_resolver)

        members_list = self._format_members_list(klass.members, 'Members')

        return (template.render({'symbol': klass,
                                 'klass': klass,
                                 'hierarchy': hierarchy,
                                 'raw_code': raw_code,
                                 'members_list': members_list}),
                False)

    def _format_interface_symbol(self, interface):
        hierarchy = self._format_hierarchy(interface)
        template = self.engine.get_template('interface.html')
        return (template.render({'symbol': interface,
                                 'hierarchy': hierarchy}),
                False)

    def _format_members_list(self, members, member_designation):
        template = self.engine.get_template('member_list.html')
        for member in members:
            member.extension_attributes['order_by_section'] = \
                self._order_by_parent
        return template.render({'members': members,
                                'member_designation': member_designation})

    def _format_function(self, function):
        return self._format_callable(function, "method", function.link.title)

    def _format_callback(self, callback):
        return self._format_callable(callback, "callback",
                                     callback.link.title, is_pointer=True)

    def _format_function_macro(self, function_macro):
        template = self.engine.get_template('callable.html')
        prototype = self._format_raw_code(function_macro.original_text)

        parameters = []
        for _ in function_macro.parameters:
            if not _.detailed_description:
                continue
            parameters.append(_.detailed_description)

        return_value_detail = self._format_return_value_symbol(
            function_macro.return_value)

        out = template.render({'prototype': prototype,
                               'symbol': function_macro,
                               'return_value': return_value_detail,
                               'parameters': parameters,
                               'callable_type': "function macro",
                               'flags': None,
                               'tags': {},
                               'extra': function_macro.extension_contents})

        return (out, False)

    def _format_alias(self, alias):
        template = self.engine.get_template('alias.html')
        aliased_type = self._format_linked_symbol(alias.aliased_type)
        return (template.render({'symbol': alias,
                                 'alias': alias,
                                 'aliased_type': aliased_type}), False)

    def _format_constant(self, constant):
        template = self.engine.get_template('constant.html')
        definition = self._format_raw_code(constant.original_text)
        out = template.render({'symbol': constant,
                               'definition': definition,
                               'constant': constant})
        return (out, False)

    def _format_symbol(self, symbol):
        format_function = self._symbol_formatters.get(type(symbol))
        symbol.extension_attributes['order_by_section'] = self._order_by_parent
        if format_function:
            return format_function(symbol)
        return (None, False)

    def _format_comment(self, comment, link_resolver):
        return self._docstring_formatter.translate_comment(
            comment, link_resolver)

    def __get_theme_files(self, path):
        res = []
        theme_files = os.listdir(path)
        for file_ in theme_files:
            if file_ == 'templates':
                pass
            src = os.path.join(path, file_)
            dest = os.path.basename(src)
            res.append((src, dest))
        return res

    def _get_extra_files(self):
        res = []

        if self.theme_path:
            res.extend(self.__get_theme_files(self.theme_path))
        if self.extra_theme_path:
            res.extend(self.__get_theme_files(self.extra_theme_path))

        for script_path in self.all_scripts:
            dest = os.path.join('js', os.path.basename(script_path))
            res.append((script_path, dest))

        for stylesheet_path in self.all_stylesheets:
            dest = os.path.join('css', os.path.basename(stylesheet_path))
            res.append((stylesheet_path, dest))

        return res

    @staticmethod
    def add_arguments(parser):
        """Banana banana
        """
        group = parser.add_argument_group(
            'Formatter', 'formatter options')
        group.add_argument(
            "--extra-assets",
            help="Extra asset folders to copy in the output",
            action='append', dest='extra_assets', default=[])

        group.add_argument("--html-theme", action="store",
                           dest="html_theme", help="html theme to use",
                           default='default')
        group.add_argument("--html-extra-theme", action="store",
                           dest="html_extra_theme",
                           help="Extra stylesheets and scripts")
        group.add_argument("--html-add-anchors", action="store_true",
                           dest="html_add_anchors",
                           help="Add anchors to html headers",
                           default='default')
        group.add_argument("--html-number-headings", action="store_true",
                           dest="html_number_headings",
                           help="Enable html headings numbering")

    def parse_toplevel_config(self, config):
        """Parse @config to setup @self state."""
        html_theme = config.get('html_theme', 'default')
        if html_theme == 'default':
            default_theme = os.path.join(HERE, os.pardir,
                                         'hotdoc_bootstrap_theme', 'dist')

            html_theme = os.path.abspath(default_theme)
            debug("Using default theme")
        else:
            html_theme = config.get_path('html_theme')
            debug("Using theme located at %s" % html_theme)

        Formatter.theme_path = html_theme

        Formatter.extra_theme_path = config.get_path('html_extra_theme')

    def parse_config(self, config):
        """Banana banana
        """
        self.add_anchors = bool(config.get("html_add_anchors"))
        self.number_headings = bool(config.get("html_number_headings"))

        if self.theme_path:
            self.__load_theme_templates(self.searchpath,
                                        self.theme_path)
        if self.extra_theme_path:
            self.__load_theme_templates(self.searchpath,
                                        self.extra_theme_path)

        self.searchpath.append(os.path.join(HERE, "templates"))
        self.engine = Engine(
            loader=FileLoader(self.searchpath, encoding='UTF-8'),
            extensions=[CoreExtension(), CodeExtension()]
        )

        self._docstring_formatter.parse_config(config)
        self.extra_assets = OrderedSet(config.get_paths('extra_assets'))
