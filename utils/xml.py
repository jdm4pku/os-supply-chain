import xml.etree.ElementTree as ET
import xmltodict
import gzip


class XMLParser(object):
    @staticmethod
    def parsefile(file_name, skip_line=0):
        # 加载XML文件
        with open(file_name, 'r', encoding='utf-8') as file:
            for i in range(skip_line):
                next(file)
            try:
                doc = xmltodict.parse(file.read())
                return doc
            except:
                return None

    @staticmethod
    def gz_parsefile(file_name, skip_line=0):
        # 打开.gz文件
        with gzip.open(file_name, 'rt', encoding='utf-8') as file:  # 'rt' 表示读取文本模式
            for i in range(skip_line):
                next(file)
            try:
                doc = xmltodict.parse(file.read())
                return doc
            except:
                return None