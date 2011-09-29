#!/usr/bin/env python
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
## @file DefenseGrid.py
#  @brief "Defense Grid: The Awakening" caption builder for Python 3.2 or later.
#  @date 2011.09.22
import sys
import os.path
import subprocess
import zipfile
import glob
import struct
import xml.etree.ElementTree
from optparse import OptionParser

#------------------------------------------------------------------------------
## @brief main関数
#  @param[in] i_options   option値。
#  @param[in] i_arguments 引数list。
def _main(i_options, i_arguments):
    if not i_options.captions_ods or not i_options.base_path:
        return False

    # "*0000.dgp"からfile一覧を作る。
    a_files = {}
    for a_path in glob.iglob(os.path.join(i_options.base_path, '*0000.dgp')):
        _make_file_map(a_files, a_path)

    # ods-fileから'content.xml'を取り出す。
    a_zip = zipfile.ZipFile(i_options.captions_ods, 'r')
    a_content = a_zip.read('content.xml')
    a_zip.close()
    a_content = xml.etree.ElementTree.ElementTree(
        xml.etree.ElementTree.fromstring(a_content.decode('utf-8')))

    # 'content.xml'からtable要素を取り出し、字幕辞書を作る。
    a_archive = {}
    a_body = a_content.find(_ns0('body'))
    a_spreadsheet = a_body.find(_ns0('spreadsheet'))
    for a_table in a_spreadsheet.findall(_table_ns('table')):
        a_name = a_table.attrib.get(_table_ns('name'))
        a_archive[a_name] = _make_caption_dict(a_table)

    # 字幕textを書き換える。
    a_chars = set()
    for a_key, a_captions in a_archive.items():
        a_entry = a_files.get(a_key + '.txt')
        if a_entry is not None:
            #_modify_caption_file(a_path, a_captions, a_chars)
            #break
            print(a_key)

#------------------------------------------------------------------------------
def _make_file_map(io_files, i_path):
    a_dgp_path = os.path.normpath(i_path)
    a_file = open(i_path, mode='rb')
    a_data = struct.unpack('<2H', a_file.read(2 * 2))
    a_num_archives = a_data[0]
    if a_data[1] <= 0xff:
        a_file.seek(2)
    for i in range(a_num_archives):
        a_dgp_path = a_dgp_path[:-len('0000.dgp')] + '%04u.dgp' % (i + 1)
        a_num_files = struct.unpack('<H', a_file.read(2))[0]
        a_directory = _read_wchar_string(a_file)
        a_file.read(1)
        a_offset = struct.unpack('<L', a_file.read(4))[0]
        for j in range(a_num_files):
            a_name = _read_wchar_string(a_file)
            a_data = struct.unpack('<LQ', a_file.read(4 + 8))
            a_entry = io_files.get(a_name)
            if a_entry is None or a_entry['time'] < a_data[1]:
                io_files[a_name] = {
                    'size': a_data[0],
                    'time': a_data[1],
                    'offset': a_offset,
                    'dgp': a_dgp_path}
            a_offset += a_data[0]

#------------------------------------------------------------------------------
def _read_wchar_string(io_file):

    # 文字列の長さを取得。
    a_length = struct.unpack('<L', io_file.read(4))[0]
    a_string = ''
    if 0 < a_length:

        # unicode文字列を変換。
        a_data = struct.unpack(
            '<' + str(a_length) + 'H', io_file.read(a_length * 2))
        for a_char in a_data:
            a_string += chr(a_char)

    return a_string

#------------------------------------------------------------------------------
def _modify_caption_file(i_path, i_captions, io_chars):

    # 字幕textを書き換える。
    a_lines = open(i_path, mode='r', encoding='utf-8').readlines()
    for i, a_line in enumerate(a_lines):
        if a_line and '#' != a_line[0]:
            a_lines[i] = _modify_caption_text(a_line, i_captions, io_chars)

    # 字幕textをfileに出力する。
    a_new_name = i_path + '.new'
    open(a_new_name, mode='w', encoding='utf-8').writelines(a_lines)
    #a_old_name = i_path + '.old'
    #os.rename(i_path, a_old_name)
    #os.rename(a_new_name, i_path)
    #os.remove(a_old_name)

#------------------------------------------------------------------------------
def _modify_caption_text(i_line, i_captions, io_chars):
    i = 0
    for a_char in i_line:
        if a_char.isspace():
            a_caption = i_captions.get(i_line[:i])
            if a_caption:
                for a_char in a_caption:
                    io_chars.add(a_char)
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
def _make_caption_dict(i_table_xml):
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
def _ns0(i_string):
    return '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}' + i_string

def _table_ns(i_string):
    return '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}' + i_string

#------------------------------------------------------------------------------
## @brief command-line引数を解析。
#  @return option値と引数listのtuple。
def _parse_arguments(io_parser):
    io_parser.add_option(
        '-b',
        '--base',
        dest='base_path',
        help='set "Defense Grid: The Awakening" installed directory path name')
    io_parser.add_option(
        '-c',
        '--captions',
        dest='captions_ods',
        default='captions.jp.ods',
        help='set captions ods-file path name')
    return io_parser.parse_args()

#------------------------------------------------------------------------------
if __name__ == "__main__":
    a_option_parser = OptionParser()
    a_options, a_arguments = _parse_arguments(a_option_parser)
    if _main(a_options, a_arguments) is not None:
        a_option_parser.print_help()
