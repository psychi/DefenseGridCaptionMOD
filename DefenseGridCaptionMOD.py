#!/usr/bin/env python
# -*- coding: utf-8 -*-

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
## @file DefenseGridCaptionMOD.py
#  @brief "Defense Grid: The Awakening" caption builder for Python 3.2 or later.
#  @date 2011.10.01
import sys
import os.path
import subprocess
import zipfile
import glob
import struct
import xml.etree.ElementTree
from optparse import OptionParser

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
#------------------------------------------------------------------------------
## @brief main関数
#  @param[in] i_options   option値。
#  @param[in] i_arguments 引数list。
def _main(i_options, i_arguments):

    # option値の整合性を確かめる。
    _is_directory(i_options.input_dir)
    _is_directory(i_options.output_dir)
    if i_options.captions_ods:
        _is_file(i_options.captions_ods)
    else:
        return False

    # "*0000.dgp"を読み込み、package書庫を作る。
    a_packages = PackageArchive()
    for a_path in glob.iglob(os.path.join(i_options.input_dir, '*0000.dgp')):
        a_packages.read(a_path)

    # ods-fileを読み込み、字幕書庫を作る。
    a_captions = _build_caption_archive(i_options.captions_ods)

    # 字幕contentsを書き換える。
    a_chars = set()
    for a_key, a_dict in a_captions.items():
        a_path = a_key + '.txt'
        a_contents = a_packages.get(a_path)
        if a_contents is not None:
            a_contents = _build_caption_contents(a_contents, a_dict, a_chars)
            a_packages.set(a_path, a_contents)

#------------------------------------------------------------------------------
## @brief command-line引数を解析。
#  @return option値と引数listのtuple。
def _parse_arguments(io_parser):
    io_parser.add_option(
        '-c',
        '--captions',
        dest='captions_ods',
        help='set captions ods-file path name')
    io_parser.add_option(
        '-i',
        '--input_dir',
        dest='input_dir',
        help='set the directory path name to input dgp-files')
    io_parser.add_option(
        '-o',
        '--output_dir',
        dest='output_dir',
        help='set the directory path name to output dgp-files')
    return io_parser.parse_args()

#------------------------------------------------------------------------------
## @brief ods-fileを読み込んで、字幕書庫を構築。
#  @param[in] i_ods_path 読み込むods-fileのpath名。
#  @return ods-fileから構築した字幕書庫。
def _build_caption_archive(i_ods_path):

    # ods-fileから'content.xml'を取り出す。
    a_zip = zipfile.ZipFile(i_ods_path, 'r')
    a_content = a_zip.read('content.xml')
    a_zip.close()
    a_content = xml.etree.ElementTree.ElementTree(
        xml.etree.ElementTree.fromstring(a_content.decode('utf-8')))

    # 'content.xml'からtable要素を取り出し、字幕辞書を作る。
    a_captions = {}
    a_body = a_content.find(_ns0('body'))
    a_spreadsheet = a_body.find(_ns0('spreadsheet'))
    for a_table in a_spreadsheet.findall(_table_ns('table')):
        a_name = a_table.attrib.get(_table_ns('name'))
        a_captions[a_name] = _build_caption_dict(a_table)
    return a_captions

#------------------------------------------------------------------------------
def _build_caption_dict(i_table_xml):
    a_dict = {}
    for a_row in i_table_xml.findall(_table_ns('table-row'))[1:]:
        a_cells = a_row.findall(_table_ns('table-cell'))
        if 3 <= len(a_cells):
            a_key = _get_table_cell_value(a_cells[0])
            if a_key and '#' != a_key[0]:
                a_text = _get_table_cell_value(a_cells[2])
                if a_text:
                    a_dict[a_key] = a_text
    return a_dict

#------------------------------------------------------------------------------
def _get_table_cell_value(i_cell_xml):
    a_type = i_cell_xml.attrib.get(_ns0('value-type'))
    if 'string' == a_type:
        a_value = i_cell_xml.find(
            '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
        if a_value is not None:
            return a_value.text

#------------------------------------------------------------------------------
## @brief 字幕文字列を書き換えた字幕contentsを作る。
#  @param[in] i_contents   元となる字幕contents
#  @param[in] i_captions   字幕辞書。
#  @param[in,out] io_chars font文字辞書。
def _build_caption_contents(i_contents, i_captions, io_chars):

    # 字幕conttentsから字幕line配列を取得し、字幕辞書を元に書き換える。
    a_lines = i_contents[3:].decode('utf-8').splitlines()
    for i, a_line in enumerate(a_lines):
        if a_line and '#' != a_line[0]:
            a_lines[i] = _build_caption_line(a_line, i_captions, io_chars)

    # 字幕line配列から字幕contentsを構築。
    return i_contents # 未実装なので、そのまま戻す。

#------------------------------------------------------------------------------
## @brief 字幕文字列を書き換えた字幕lineを作る。
#  @param[in] i_line     元となる字幕line
#  @param[in] i_captions 字幕辞書。
#  @param[in] io_chars   font文字辞書。
def _build_caption_line(i_line, i_captions, io_chars):

    # 字幕lineから字幕名を取り出す。
    i = 0
    for a_char in i_line:
        if a_char.isspace():

            # 字幕名をkeyとして、字幕辞書から字幕文字列を取り出す。
            a_caption = i_captions.get(i_line[:i])
            if a_caption:

                # 字幕文字列でfont文字辞書を更新。
                for a_char in a_caption:
                    io_chars.add(a_char)

                # 字幕文字列を書き換えた字幕lineを出力。
                for a_char in i_line[i:]:
                    if a_char.isspace():
                        i += 1
                    else:
                        break
                return i_line[:i] + a_caption + '\n'
            break
        i += 1
    return i_line

#------------------------------------------------------------------------------
## @brief streamからwchar文字列を取り出す。
#  @param[in,out] io_stream
#  @return 取り出した文字列。
def _read_wchar_string(io_stream):

    # 文字列の長さを取得。
    a_length = struct.unpack('<L', io_stream.read(4))[0]
    a_string = ''
    if 0 < a_length:

        # unicode文字列を変換。
        a_data = struct.unpack(
            '<' + str(a_length) + 'H', io_stream.read(a_length * 2))
        for a_char in a_data:
            a_string += chr(a_char)

    return a_string

#------------------------------------------------------------------------------
def _is_directory(i_path):
    if not os.path.isdir(i_path):
        raise Exception(
            ''.join(('"', i_path, '"は、ディレクトリではありません。')))

def _is_file(i_path):
    if not os.path.isfile(i_path):
        raise Exception(
            ''.join(('"', i_path, '"は、ファイルではありません。')))

#------------------------------------------------------------------------------
def _ns0(i_string):
    return '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}' + i_string

def _table_ns(i_string):
    return '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}' + i_string

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
class PackageSection:

    #--------------------------------------------------------------------------
    ## @param[in] i_path      sectionのpath名。
    #  @param[in] i_size      sectionのbyte-size。
    #  @param[in] i_timestamp sectionのtimestamp
    def __init__(self, i_path, i_size, i_timestamp):
        self._path = i_path
        self._size = i_size
        self._contents = None
        self._timestamp = i_timestamp

    #--------------------------------------------------------------------------
    def __str__(self):
        return str(self.__dict__)

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
class PackageFile:

    #--------------------------------------------------------------------------
    ## @param[in,out] io_sections sectionを登録する辞書。
    #  @param[in,out] io_catalog  読み込む目次stream。
    def __init__(self, io_sections, io_catalog):

        self._modified = False

        # 各種file属性を取得。
        a_num_sections = struct.unpack('<H', io_catalog.read(2))[0]
        self._tag = _read_wchar_string(io_catalog)
        self._unknown = io_catalog.read(1)
        self._offset = struct.unpack('<L', io_catalog.read(4))[0]

        # sectionを構築。
        self._sections = list()
        while len(self._sections) < a_num_sections:

            # 新たなsectionを構築し、section配列に登録。
            a_path = _read_wchar_string(io_catalog)
            a_data = struct.unpack('<LQ', io_catalog.read(4 + 8))
            self._sections.append(
                PackageSection(a_path, a_data[0], a_data[1]))

            # section辞書に登録。
            a_section = io_sections.get(a_path)
            if a_section is None or a_section._timestamp < a_data[1]:
                io_sections[a_path] = self._sections[-1]

    #--------------------------------------------------------------------------
    def _read(self, i_path):

        # package-fileを開く。
        _is_file(i_path)
        a_stream = open(i_path, mode='rb')

        # 文字列配列を読み込む。
        a_num_strings = struct.unpack('<L', a_stream.read(4))[0]
        self._strings = list()
        while len(self._strings) < a_num_strings:
            self._strings.append(_read_wchar_string(a_stream))

        if a_stream.tell() != self._offset:
            raise

        # section-contensを読み込む。
        for a_section in self._sections:
            a_section._contents = a_stream.read(a_section._size)

    #--------------------------------------------------------------------------
    def __str__(self):
        return str(self.__dict__)

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
class PackageCluster:

    #--------------------------------------------------------------------------
    ## @param[in,out] io_sections sectionを登録する辞書。
    #  @param[in,out] i_path      読み込む目次fileのpath名。
    def __init__(self, io_sections, i_path):

        # 目次fileを開く。
        self._path = os.path.normpath(i_path)
        a_catalog = open(self._path, mode='rb')

        # file数を取得。
        a_data = struct.unpack('<2H', a_catalog.read(2 * 2))
        a_num_files = a_data[0]

        # Steam version?
        if 9999 < a_data[1]:
            self._steam = a_data[1]
        else:
            # section数として有効だった場合は巻き戻す。
            self._steam = None
            a_catalog.seek(2)

        # file配列を構築。
        self._files = list()
        while len(self._files) < a_num_files:
            self._files.append(PackageFile(io_sections, a_catalog))

    #--------------------------------------------------------------------------
    def _read(self, i_index):
        self._files[i_index]._read(self._file_path(i_index))

    #--------------------------------------------------------------------------
    def _file_path(self, i_index):
        if self._path:
            return self._path[:-len('0000.dgp')] + '%04u.dgp' % (i_index + 1)

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
class PackageArchive:

    #--------------------------------------------------------------------------
    def __init__(self):
        self._clusters = dict()
        self._sections = dict()

    #--------------------------------------------------------------------------
    def read(self, i_path):
        a_cluster = PackageCluster(self._sections, i_path)
        self._clusters[a_cluster._path] = a_cluster

    #--------------------------------------------------------------------------
    def write(self, i_output_dir):
        _is_directory(i_output_dir)

        for a_cluster in self._clusters.values():
            a_written = False
            for i, a_file in enumerate(a_cluster._files):
                if a_file._modified:
                    a_file._write(
                        os.path.join(
                            i_output_dir, 
                            os.path.basename(a_cluster._file_path(i))))
                    a_written = True
            if a_written:
                a_cluster._write_catalog()

    #--------------------------------------------------------------------------
    ## @brief packageからcontentsを取得。
    #  @param[in] i_path contentsのpath名。
    def get(self, i_path):

        # path名に対応するsectionを検索。
        a_target = self._sections.get(i_path)
        if a_target is not None:
            if a_target._contents is not None:
                return a_target._contents

            # sectionが空の場合は、package-fileを読み込む。
            for a_cluster in self._clusters.values():
                for i, a_file in enumerate(a_cluster._files):
                    for a_section in a_file._sections:
                        if a_section is a_target:
                            a_cluster._read(i)
                            return a_target._contents
            else:
                raise

    #--------------------------------------------------------------------------
    ## @brief packageにcontentsを設定。
    #  @param[in] i_path     sectionのpath名。
    #  @param[in] i_contents contentsとして設定するbytes-object。
    def set(self, i_path, i_contents):
        if not isinstance(i_contents, bytes):
            raise

        # path名に対応するsectionを検索。
        a_target = self._sections.get(i_path)
        if a_target is not None:
            for a_cluster in self._clusters.values():
                for a_file in a_cluster._files:
                    for a_section in a_file._sections:
                        if a_section is a_target:
                            if a_section._contents is not i_contents:
                                a_section._contents = i_contents
                                a_file._modified = True
                                return True
                            else:
                                return False
            else:
                raise

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
if __name__ == "__main__":
    a_option_parser = OptionParser()
    a_options, a_arguments = _parse_arguments(a_option_parser)
    if _main(a_options, a_arguments) is not None:
        a_option_parser.print_help()
