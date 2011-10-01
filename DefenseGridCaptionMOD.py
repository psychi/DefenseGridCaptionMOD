#!/usr/bin/env python
# -*- coding: utf-8 -*-

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
## @file DefenseGridCaptionMOD.py
#  @brief "Defense Grid: The Awakening" caption modifier for Python 3.2 or later.
#  @date 2011.10.01
import sys
import os.path
import subprocess
import zlib
import zipfile
import glob
import struct
import xml.etree.ElementTree
from optparse import OptionParser

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
#------------------------------------------------------------------------------
## @brief main関数
#  @param[in] i_options   option値。
#  @param[in] i_arguments 引数の配列。
def _main(i_options, i_arguments):

    # option値の整合性を確かめる。
    _is_directory(i_options.input_dir)
    if not i_options.captions_ods:
        return False

    # "*0000.dgp"を読み込み、package書庫を作る。
    a_packages = PackageArchive()
    for a_path in glob.iglob(os.path.join(i_options.input_dir, '*0000.dgp')):
        a_packages.read(a_path)

    # 字幕ods-fileを元に、字幕を書き換える。
    a_font_chars = _modify_caption(a_packages, i_options.captions_ods)

    # fontを書き換える。
    _modify_font(a_packages, i_options.output_dir, 'ui\\gfxfontlib.gfx')

    # 書き換えたpackageをfileに出力。
    a_packages.write(i_options.output_dir)

#------------------------------------------------------------------------------
## @brief 字幕を書き換える。
#  @param[in,out] io_packages 字幕contentを含むpackage書庫。
#  @param[in] i_ods_path      読み込む字幕ods-fileのpath名。
#  @return 字幕で使われた文字の一覧。
def _modify_caption(io_packages, i_ods_path):

    # 字幕ods-fileからspreadsheetを取り出す。
    a_zip = zipfile.ZipFile(i_ods_path, 'r')
    a_xml = a_zip.read('content.xml')
    a_zip.close()
    a_xml = xml.etree.ElementTree.ElementTree(
        xml.etree.ElementTree.fromstring(a_xml.decode('utf-8')))
    a_xml = a_xml.find(_ns0('body'))
    a_xml = a_xml.find(_ns0('spreadsheet'))

    # spreadsheetからtable要素を取り出し、字幕辞書を作る。
    a_caption_chars = set()
    for a_table in a_xml.findall(_table_ns('table')):
        a_path = a_table.attrib.get(_table_ns('name')) + '.txt'
        a_content = io_packages.get(a_path)
        if a_content is not None:
            a_captions = _build_caption_dict(a_table)

            # 字幕辞書を元に、字幕contentを書き換える。
            a_lines = a_content[3:].decode('utf-8').splitlines()
            a_content = a_content[:3]
            for a_line in a_lines:
                if a_line and '#' != a_line[0]:
                    a_line = _build_caption_line(
                        a_line, a_captions, a_caption_chars)
                a_content += ''.join((a_line, '\r\n')).encode('utf-8')
            if io_packages.set(a_path, a_content) is None:
                raise

    return a_caption_chars

#------------------------------------------------------------------------------
## @brief 字幕辞書を作る。
#  @param[in] i_table_xml 字幕辞書の元となるXML。
#  @return 字幕辞書。
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
## @brief 字幕文字列を書き換えた字幕lineを作る。
#  @param[in] i_line               元となる字幕line
#  @param[in] i_captions           字幕辞書。
#  @param[in,out] io_caption_chars 字幕で使われた文字の一覧。
def _build_caption_line(i_line, i_captions, io_caption_chars):

    # 字幕lineから字幕名を取り出す。
    i = 0
    for a_char in i_line:
        if a_char.isspace():

            # 字幕名をkeyとして、字幕辞書から字幕文字列を取り出す。
            a_caption = i_captions.get(i_line[:i])
            if a_caption:

                # 文字一覧を更新。
                for a_char in a_caption:
                    io_caption_chars.add(a_char)

                # 字幕文字列を書き換えた字幕lineを出力。
                for a_char in i_line[i:]:
                    if a_char.isspace():
                        i += 1
                    else:
                        break
                return ''.join((i_line[:i], a_caption))
            break
        i += 1
    return i_line

#------------------------------------------------------------------------------
def _modify_font(io_packages, i_output_dir, i_gfx_path):
    a_content = io_packages.get(i_gfx_path)
    if a_content is None or len(a_content) < 3:
        raise
    a_signature = a_content[:3]

    # gfx-fileを出力。
    a_gfx_path = os.path.basename(i_gfx_path)
    a_decompress = True
    if a_decompress:
        a_content = b'FWS' + a_content[3: 8] + zlib.decompress(a_content[8:])

        # SWF8以降は、必ずFileAttributes-tagから始まる。
        # その間は、未知のtagとして保存しておく。
        if 8 <= a_content[4]:
            a_unknown_begin = 8 + (((5 + (a_content[8] >> 3) * 4) + 7) // 8) + 2 + 2
            a_unknown_end = a_unknown_begin
            while a_unknown_end < len(a_content):
                a_tag = a_content[a_unknown_end] | (a_content[a_unknown_end + 1] << 8)
                if (a_tag >> 6) != 69:
                    a_unknown_end += 2 + (a_tag & 0x3f)
                else:
                    break;
            else:
                raise
            a_unknown_tags = a_content[a_unknown_begin: a_unknown_end]
    else:
        a_content = b'CWS' + a_content[3:]
    print(''.join(('writing "', a_gfx_path, '"')))
    open(a_gfx_path, mode='wb').write(a_content)

    # gfx-fileをxml-fileに変換。
    a_xml_path = a_gfx_path[:-3] + 'xml'
    print(''.join(('writing "', a_xml_path, '"')))
    subprocess.check_call(('swfmill.exe', 'swf2xml', a_gfx_path, a_xml_path))

    # xml-fileをswf-fileに変換。
    a_swf_path = a_gfx_path[:-3] + 'swf'
    print(''.join(('writing "', a_swf_path, '"')))
    subprocess.check_call(('swfmill.exe', 'xml2swf', a_xml_path, a_swf_path))
    a_content = open(a_swf_path, mode='rb').read()
    io_packages.set(i_gfx_path, a_signature + a_content[3:])

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
## @brief 文字列をbytesに変換。
#  @param[in] i_string      書きこむ文字列。
def _convert_wchar_to_bytes(i_string):
    a_bytes = struct.pack('<L', len(i_string))
    for a_char in i_string:
        a_bytes += struct.pack('<H', ord(a_char))
    return a_bytes

#------------------------------------------------------------------------------
def _write_package_file(i_path, i_bytes):
    open(i_path, mode='wb').write(i_bytes)
    subprocess.check_call(('dgridhash.exe', '-a', '-o', i_path, i_path))

#------------------------------------------------------------------------------
def _is_directory(i_path):
    if not os.path.isdir(i_path):
        raise Exception(
            ''.join(('"', i_path, '"は、ディレクトリではありません。')))

#------------------------------------------------------------------------------
def _ns0(i_string):
    return '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}' + i_string

def _table_ns(i_string):
    return '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}' + i_string

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

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
class PackageSection:

    #--------------------------------------------------------------------------
    ## @param[in] i_path      sectionのpath名。
    #  @param[in] i_size      sectionのbyte-size。
    #  @param[in] i_timestamp sectionのtimestamp
    def __init__(self, i_path, i_size, i_timestamp):
        self._path = i_path
        self._size = i_size
        self._content = None
        self._timestamp = i_timestamp

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
        self._unknown = io_catalog.read(1)[0]
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
    ## @brief content目録をbinary化する。
    def _build_catalog(self):
        a_catalog = struct.pack('<H', len(self._sections))
        a_catalog += _convert_wchar_to_bytes(self._tag)
        a_catalog += struct.pack('<BL', self._unknown, self._offset)
        for a_section in self._sections:
            a_catalog += _convert_wchar_to_bytes(a_section._path)
            a_catalog += struct.pack(
                '<LQ', a_section._size, a_section._timestamp)
        return a_catalog

    #--------------------------------------------------------------------------
    def _read(self, i_path):

        # package-fileを開く。
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
            a_section._content = a_stream.read(a_section._size)

    #--------------------------------------------------------------------------
    def _write(self, i_path):

        # 文字列配列を書きこむ。
        a_package = struct.pack('<L', len(self._strings))
        for a_string in self._strings:
            a_package += _convert_wchar_to_bytes(a_string)
        #self._offset = len(a_package)

        # contentを書きこむ。
        for a_section in self._sections:
            a_package += a_section._content
            a_section._size = len(a_section._content)

        # fileに出力。
        _write_package_file(i_path, a_package)

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
    def _write_catalog(self, i_output_dir):

        # package-fileの数を書き込む。
        a_package = struct.pack('<H', len(self._files))
        if self._steam is not None:
            a_package += struct.pack('<H', self._steam)

        # content目録を書き込む。
        for a_file in self._files:
            a_package += a_file._build_catalog()

        # fileに出力。
        _write_package_file(
            os.path.join(i_output_dir, os.path.basename(self._path)),
            a_package)

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
    ## @brief package-fileを読み込んで、package書庫に追加する。
    #  @param[in] i_path 読み込むpackage-fileのpath名。
    def read(self, i_path):
        a_cluster = PackageCluster(self._sections, i_path)
        self._clusters[a_cluster._path] = a_cluster

    #--------------------------------------------------------------------------
    ## @brief 変更されたpackageをfileに出力する。
    #  @param[in] i_output_dir package-fileを出力するdirectoryのpath名。
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

            # content部分をfileに出力したなら、catalog部分もfileに出力する。
            if a_written:
                a_cluster._write_catalog(i_output_dir)

    #--------------------------------------------------------------------------
    ## @brief packageからcontentを取得。
    #  @param[in] i_path contentのpath名。
    def get(self, i_path):

        # path名に対応するsectionを検索し、contensを取得。
        a_target = self._sections.get(i_path)
        if a_target is not None:
            if a_target._content is not None:
                return a_target._content

            # contentが空だったので、package-fileを読み込む。
            for a_cluster in self._clusters.values():
                for i, a_file in enumerate(a_cluster._files):
                    for a_section in a_file._sections:
                        if a_section is a_target:
                            a_cluster._read(i)
                            return a_target._content
            raise

    #--------------------------------------------------------------------------
    ## @brief packageにcontentを設定。
    #  @param[in] i_path    sectionのpath名。
    #  @param[in] i_content contentとして設定するbytes-object。
    def set(self, i_path, i_content):
        if not isinstance(i_content, bytes):
            raise

        # path名に対応するsectionを検索。
        a_target = self._sections.get(i_path)
        if a_target is not None:
            for a_cluster in self._clusters.values():
                for a_file in a_cluster._files:
                    for a_section in a_file._sections:
                        if a_section is a_target:
                            if a_section._content is i_content:
                                return False
                            else:
                                a_section._content = i_content
                                a_file._modified = True
                                return True
            else:
                raise

#ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
if __name__ == '__main__':
    a_option_parser = OptionParser()
    a_options, a_arguments = _parse_arguments(a_option_parser)
    if _main(a_options, a_arguments) is False:
        a_option_parser.print_help()
