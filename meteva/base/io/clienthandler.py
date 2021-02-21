#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: clienthandler.py

'''
Created on Aug 23, 2020

@author: anduin
'''

import logging
import threading
import time

class LogData():
    def __init__(self, cid, logstr):
        self.clientid = cid
        self.logstr = logstr
        
class ClientHandler(logging.Handler):
    def __init__(self, clientmgr):
        logging.Handler.__init__(self)
        
        self.clientmgr = clientmgr
        
        self.logbuf = []
        
        self.con = threading.Condition()
        self.stopit = False
        self.logThread = threading.Thread(target=ClientHandler.threadproc, args=(self,))
        self.logThread.start()
        
    def __del__(self):
        #logging.Handler.__del__(self)
        self.stopit = True
        time.sleep(2)
    
    def sendlog(self):
        while not self.stopit:
            if len(self.logbuf) == 0:
                time.sleep(1)
                continue
                
            tmpbuf = []
            self.con.acquire()
            try:
                while len(tmpbuf) < 5 and len(self.logbuf) > 0:
                    tmpbuf.append(self.logbuf.pop(0))
            except Exception as data:
                print('clienthandle sendlog read from logbuf exception:%s' % (str(data)))
            self.con.release()
            
            
            try:
                for log in tmpbuf:
                    self.clientmgr.addLog(log.clientid, log.logstr)
            except Exception as data:
                print('clienthandle sendlog add log to client exception:%s' % (str(data)))
            
    @staticmethod
    def threadproc(chandler):
        time.sleep(5)
        chandler.sendlog()
            
    def emit(self, record):
        """
        Emit a record.

        Send the record to the Web server as a percent-encoded dictionary
        """
        try:
            clientid = 0
            index = record.msg.find(' ')
            if index != -1:
                str = record.msg[:index]
                try:
                    clientid = int(str)
                    record.msg = record.msg[index + 1:]
                except:
                    clientid = 0
                    #record.msg = '0 ' + record.msg
            #else:
            #    record.msg = '0 ' + record.msg
                
            #self.clientmgr.addLog(clientid, self.format(record))
            self.con.acquire()
            try:
                if len(self.logbuf) < 200:
                    self.logbuf.append(LogData(clientid, self.format(record)))
            except Exception as data:
                print('clienthandle exception:%s' % (str(data)))
                
            self.con.release()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

        
if __name__ == '__main__':
    from dispatch.clientmgr import ClientMgr
    cm = ClientMgr()
    ch = ClientHandler(cm)
    
    print('test done')
    
