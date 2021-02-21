#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: loglib.py

'''
Created on Aug 23, 2020

@author: anduin
'''

import logging
import logging.handlers
#from .clienthandler import ClientHandler

class LogLib:
    '''
    日志格式‘%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s’
    
    使用TimedRotatingFileHandler时，保持240个日志备份，每小时一个日志文件。
    使用ConcurrentRotatingFileHandler时，保持100个1MB的文件。
    上面两个handle仅使用一个。
    
    使用前调用init初始化
    使用LogLib.logger中的debug、info、warn、error、critical写日志
    系统结束后调用unint
    
    需要向每个client发送日志时，要求日志的msg部分，以clientid+空格开始。
    ClientHandle中会取msg第一个空格前的字符串，转换成clientid，所以需要避免以数字字符+空格开始的日志信息，这样会导致信息分发错误。
    '''
    
    logger = None
    #for file log
    fhdlr = None
    #for client log
    chdlr = None
    
    @staticmethod
    def init():
        LogLib.logger = logging.getLogger()
        
        LogLib.logger.setLevel(logging.DEBUG)
        
        return True
    
    @staticmethod
    def addTimedRotatingFileHandler(filename):
        try:
            if __name__ == '__main__':
                #for test
                LogLib.fhdlr = logging.handlers.TimedRotatingFileHandler(filename, 'm', 1, 3)
            else:
                LogLib.fhdlr = logging.handlers.TimedRotatingFileHandler(filename, 'h', 1, 240)
                
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s')
            LogLib.fhdlr.setFormatter(formatter)
            LogLib.logger.addHandler(LogLib.fhdlr)
            return True
        except Exception as data:
            print('LogLib addTimedRotatingFileHandler exception:%s' % (str(data)))
            return False
        

    @staticmethod
    def writeToFile():
        if LogLib.logger == None or LogLib.fhdlr == None:
            return
        try:
            LogLib.fhdlr.flush()
        except Exception as data:
            print('log flush error %s' % (str(data)))
        
    @staticmethod
    def uninit():
        """
        Perform any cleanup actions in the logging system (e.g. flushing buffers).
        Should be called at application exit.
        """
        try:
            if LogLib.fhdlr != None:
                LogLib.fhdlr.flush()
        except Exception as data:
            print('file log flush error %s' % (str(data)))
            
        try:
            if LogLib.fhdlr != None:
                LogLib.fhdlr.close()
        except Exception as data:
            print('file log close error %s' % (str(data)))
                
        try:
            if LogLib.chdlr != None:
                LogLib.chdlr.close()
        except Exception as data:
            print('client log close error %s' % (str(data)))
                
        if LogLib.fhdlr != None:
            LogLib.logger.removeHandler(LogLib.fhdlr)
            LogLib.fhdlr = None
        
        if LogLib.chdlr != None:
            LogLib.logger.removeHandler(LogLib.chdlr)
            LogLib.chdlr = None
        
        LogLib.logger = None
        
    @staticmethod
    def debug(msg):
        if LogLib.logger is None:
            return

        LogLib.logger.debug(msg)
        
    @staticmethod
    def info(msg):
        if LogLib.logger is None:
            return

        LogLib.logger.info(msg)
        
    @staticmethod
    def warning(msg):
        if LogLib.logger is None:
            return

        LogLib.logger.warning(msg)
        
    @staticmethod
    def warn(msg):
        if LogLib.logger is None:
            return

        LogLib.logger.warn(msg)

    @staticmethod
    def error(msg):
        if LogLib.logger is None:
            return

        LogLib.logger.error(msg)
        
    @staticmethod
    def exception(msg, exc_info=True):
        if LogLib.logger is None:
            return

        LogLib.logger.exception(msg, exc_info=exc_info)
        
    @staticmethod
    def critical(msg):
        if LogLib.logger is None:
            return

        LogLib.logger.critical(msg)
        
#for test
if __name__ == '__main__':
    import time
    #from dispatch.clientmgr import ClientMgr
    
    LogLib.init()
    #LogLib.addTimedRotatingFileHandler('./testlog')
    #cm = ClientMgr()
    #LogLib.addClientHandle(cm)
    
    for i in range(0, 400):
        #LogLib.write(logging.INFO, 'test')
        LogLib.logger.debug('test')
        time.sleep(1)
        
    LogLib.uninit()
    
    print('test done')
    
