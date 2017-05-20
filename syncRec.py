import socket
import time
import os
import hashlib
import re
import stat
from threading import Thread

host = ""
port1 = 60000  #for s as server
port2 = 40000  #for r as server
port3 = 20000  #for update s
port4 = 10000  #for update r
portUdp = 50000

#for r as server
class ReceiveThread(Thread):

    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val

    def run(self):
        while True:
            s = socket.socket()
            s.connect((host, port2))
            command = s.recv(1024)
            a2 = command.split(" ")

            if len(a2) <= 1 :
                a = 'No Input'
                s.send(a)

            elif a2[0] == str('index') and a2[1] == str('longlist'):
                t = os.popen('ls -l').read()
                t = t.split('\n')
                del t[0]
                del t[-1]
                d = '@'
                t = d.join(t)
                ls = os.listdir('./')
                result = []
                for files in ls :
                    data = os.stat(files)
                    te = int(data.st_mtime)
                    print str(files) + " => " + str(te) + '\n'
                s.send(t)
                time.sleep(0.1)

            elif a2[0] == str('index') and a2[1] == str('shortlist'):
                if len(a2) < 4:
                    a = 'Wrong Input Format Require 2 Arguments'
                    s.send(a)
                    time.sleep(0.1)
                else :
                    t = os.popen('ls -l').read()
                    t = t.split('\n')
                    del t[0]
                    del t[-1]
                    result = []
                    for files in t :
                        se = files.split()
                        data = os.stat(se[8])
                        te = int(data.st_mtime)
                        if te > int(a2[2]) and te < int(a2[3]):
                            #print t[i]
                            result.append(files)
                    d = '@'
                    result = d.join(result)
                    s.send(result)
                    time.sleep(0.1)

            elif a2[0] == str('index') and a2[1] == str('regex') :
                if len(a2) < 3:
                    a = 'Wrong Input Format Require 1 Arguments'
                    s.send(a)
                    time.sleep(0.1)
                else :
                    t = os.popen('ls -l').read()
                    t = t.split('\n')
                    del t[0]
                    del t[-1]
                    result = []
                    for files in t :
                        se = files.split()
                        if not re.search(a2[2], se[8]):
                            continue
                        result.append(files)
                    d = '@'
                    result = d.join(result)
                    s.send(result)
                    time.sleep(0.1)


            elif a2[0] == str('hash') and a2[1] == str('verify') :
                result = []
                ls = os.listdir('./')
                if len(a2) < 3:
                    a = 'Wrong Input Format Require 2 Arguments'
                    s.send(a)
                    time.sleep(0.1)
                if a2[2] not in ls:
                    a = 'Wrong Input, Check The File Name'
                    s.send(a)
                    time.sleep(0.1)
                with open(a2[2],'rb') as f :
                    h = hashlib.md5()
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        h.update(data)
                    result.append(str(h.hexdigest()))
                data = os.stat(a2[2])
                result.append(str(int(data.st_mtime)))
                d = '@'
                result = d.join(result)
                #print result
                s.send(result)
                time.sleep(0.1)

            elif a2[0] == str('hash') and a2[1] == str('checkall') :
                ls = os.listdir('./')
                d = '@'
                result = []
                for files in ls :
                    result.append(str(files))
                    with open(files,'rb') as f :
                        h = hashlib.md5()
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            h.update(data)
                        result.append(str(h.hexdigest()))
                    data = os.stat(files)
                    result.append(str(int(data.st_mtime)))
                result = d.join(result)
                s.send(result)
                time.sleep(0.1)

            elif a2[0] == str('download') and a2[1] == str('tcp') and len(a2) >= 3 :
                #print a2[1]
                filename = a2[2]
                ls = os.listdir('./')
                temp = filename in ls
                s.send(str(temp))
                time.sleep(0.1)
                if filename in ls :
                    f = open(filename,'rb')
                    l = f.read(1024)
                    while (l):
                       s.send(l)
                       l = f.read(1024)
                    time.sleep(0.1)
                    f.close()
                    mode = oct(stat.S_IMODE(os.stat(filename).st_mode))
                    s.send(str(mode))
                else :
                    a = 'Wrong File Name'
                    s.send(a)
                    time.sleep(0.1)

            elif a2[0] == str('download') and a2[1] == str('udp'):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                filename = a2[2]
                ls = os.listdir('./')
                temp = filename in ls
                temp = str(temp)
                print temp + 'sending'
                sock.sendto(temp,(host,portUdp))
                time.sleep(0.1)
                if filename in ls :
                    f = open(filename,'rb')
                    print "hello1"
                    l = f.read(1024)
                    while (l):
                        print l
                        sock.sendto(l,(host,portUdp))
                        print 'sent'
                        l = f.read(1024)
                    time.sleep(0.1)
                    print l
                    f.close()
                    mode = oct(stat.S_IMODE(os.stat(filename).st_mode))
                    sock.send(str(mode))
                else :
                    a = 'Wrong File Name'
                    sock.sendto(a,(host,portUdp))
                    time.sleep(0.1)
                sock.close()

            else :
                a = 'Wrong Input Check The Command'
                sock.sendto(a,(host,portUdp))
                time.sleep(0.1)

            s.close()



class SendThread(Thread):

    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val

    def run(self):
        while True:
            command = raw_input("\n Enter command >>")
            s = socket.socket()
            s.connect((host, port1))
            s.send(command)
            time.sleep(0.1)
            a = command.split(" ")
            if a[0] != 'download':
                nameFile = s.recv(1024)
                t = nameFile.split('@')
                for files in t :
                     print files
            else :
                if a[1] == 'udp' and len(a) >=3 :
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.bind((host, portUdp))
                    data,addr = sock.recvfrom(1024)
                    if data == 'True':
                        nameFile = a[2]
                        with open(nameFile, 'wb') as f:
                            while True:
                                data,addr = sock.recvfrom(1024)
                                if not data:
                                    break
                                f.write(data)
                        mode = sock.recv(1024)
                        mode = int(mode,8)
                        os.chmod(nameFile,mode)
                    else :
                        data,addr = sock.recvfrom(1024)
                        print data
                    sock.close()
                elif a[1] == 'tcp' and len(a) >= 3:
                    data = s.recv(1024)
                    if data == 'True':
                        nameFile = a[2]
                        with open(nameFile, 'wb') as f:
                            while True:
                                data = s.recv(1024)
                                if not data:
                                    break
                                f.write(data)
                        mode = s.recv(1024)
                        mode = int(mode,8)
                        os.chmod(nameFile,mode)
                        print 'Successfully got the file => ' + a[1]
                    else :
                        data = s.recv(1024)
                        print data
            s.close()
        print('connection closed')

class RecieveUpdate(Thread):

    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val

    def run(self):
        while True:
            s = socket.socket()
            s.connect((host, port4))
            #conn2, addr2 = s2.accept()
            command = s.recv(1024)
            a2 = command.split(" ")
            if a2[0] == str('update') :
                #print "Update Started"
                ls = os.listdir('./')
                d = '@'
                s.send(str(len(ls)))
                time.sleep(0.1)
                for files in ls :
                    result = []
                    data1 = os.stat(files)
                    tempTime = int(data1.st_mtime)
                    result.append(str(files))
                    with open(files,'rb') as f :
                        h = hashlib.md5()
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            h.update(data)
                        result.append(str(h.hexdigest()))
                    result.append(str(tempTime))
                    result = d.join(result)
                    s.send(result)
                    time.sleep(0.1)

            elif a2[0] == str('download') :
                #print a2[1]
                filename = a2[1]
                f = open(filename,'rb')
                l = f.read(1024)
                while (l):
                   s.send(l)
                   l = f.read(1024)
                time.sleep(0.1)
                f.close()
                mode = oct(stat.S_IMODE(os.stat(filename).st_mode))
                s.send(str(mode))

            s.close()


class SendUpdate(Thread):

    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val
        self.startTime = 0

    def run(self):
        while True:
            if time.time()-self.startTime > 20 :
                s3 = socket.socket()
                s3.connect((host, port3))
                self.startTime = time.time()
                currFiles = os.listdir('./')
                filesToDwnld = []
                s3.send('update')
                time.sleep(0.1)
                reply = s3.recv(1024)
                for i in range(int(reply)) :
                    r = s3.recv(1024)
                    r = r.split('@')
                    if r[0] in currFiles :
                        data1 = os.stat(r[0])
                        tempTime = int(data1.st_mtime)
                        with open(r[0],'rb') as f :
                            h = hashlib.md5()
                            while True:
                                data = f.read(1024)
                                if not data:
                                    break
                                h.update(data)
                            tempHash = str(h.hexdigest())
                        if tempHash != r[1]:
                            filesToDwnld.append(r[0])
                        if tempHash == r[1] and tempTime < int(r[2]):
                            filesToDwnld.append(r[0])
                    else :
                        filesToDwnld.append(r[0])
                s3.close()
                for files in filesToDwnld :
                    s3 = socket.socket()
                    s3.connect((host, port3))
                    command = 'download ' + files
                    s3.send(command)
                    time.sleep(0.1)
                    with open(files, 'wb') as f:
                        while True:
                            data = s3.recv(1024)
                            if not data:
                                break
                            f.write(data)
                    print 'file ' + files + ' updated'
                    mode = s3.recv(1024)
                    print mode
                    mode = int(mode,8)
                    os.chmod(files,mode)
                    s3.close()
                #print "Update Completed"



if __name__ == '__main__':
   # Declare objects of MyThread class
   myThreadOb1 = SendThread(4)
   myThreadOb1.setName('Thread 1')

   myThreadOb2 = ReceiveThread(4)
   myThreadOb2.setName('Thread 2')

   myThreadOb3 = SendUpdate(4)
   myThreadOb3.setName('Thread 3')

   myThreadOb4 = RecieveUpdate(4)
   myThreadOb4.setName('Thread 4')

   # Start running the threads!
   myThreadOb1.start()
   myThreadOb2.start()
   myThreadOb3.start()
   time.sleep(0.1)
   myThreadOb4.start()

   # Wait for the threads to finish...
   myThreadOb1.join()
   myThreadOb2.join()
   myThreadOb3.join()
   myThreadOb4.join()

   print('Main Terminating...')
0664