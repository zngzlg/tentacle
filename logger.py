#!/usr/bin/python
#-*- coding:utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler


class SimpleLogger(object):
    def __init__(self,name):
        #log file
        self.logger_file = "./logs/%s.log" % name
        #basic config
        logging.basicConfig(
            level=logging.DEBUG,
            filename=self.logger_file,
            format="%(asctime)s <%(levelname)s> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filemode='a'
        )
        self.logger = logging.getLogger(name)
    def log(self,content):
        self.logger.info(content)

class ConsoleLogger(object):
    def __init__(self,name):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s <%(levelname)s> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.logger = logging.getLogger(name)
    def log(self,content):
        self.logger.info(content)
    def error(self,content):
        self.logger.error(content)

class TimedRotatingLogger(object):
    def __init__(self,name):
        self.logger_file =  "./logs/%s.log" % name
        logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S")
        loghandle = TimedRotatingFileHandler(self.logger_file, 'midnight', 1, 2)
        loghandle.suffix= '%Y%m%d'
        loghandle.setFormatter(logging.Formatter("%(asctime)s <%(levelname)s> %(message)s"))
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(loghandle)

    def log(self,content):
        self.logger.info(content)
    def warn(self,content):
        self.logger.warn(content)
    def error(self,content):
        self.logger.error(content)

