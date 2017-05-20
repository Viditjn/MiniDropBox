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
        s2 = socket.socket()
        s2.bind((host, port1))
        s2.listen(5)
        while True:
            conn2, addr2 = s2.accept()
            command = conn2.recv(1024)
            a2 = command.split(" ")

            if len(a2) <= 1 :
                a = 'No Input'
                conn2.send(a)

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
                conn2.send(t)
                time.sleep(0.1)

            elif a2[0] == str('index') and a2[1] == str('shortlist'):
                if len(a2) < 4:
                    a = 'Wrong Input Format Require 2 Arguments'
                    conn2.send(a)
                    time.sleep(0.1)
                else:
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
                            result.append(files)
                    d = '@'
                    result = d.join(result)
                    conn2.send(result)
                    time.sleep(0.1)

            elif a2[0] == str('index') and a2[1] == str('regex') :
                if len(a2) < 3:
                    a = 'Wrong Input Format Require 1 Arguments'
                    conn2.send(a)
                    time.sleep(0.1)
                else:
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
                    conn2.send(result)
                    time.sleep(0.1)


            elif a2[0] == str('hash') and a2[1] == str('verify') :
                result = []
                ls = os.listdir('./')
                if len(a2) < 3:
                    a = 'Wrong Input Format Require 2 Arguments'
                    conn2.send(a)
                    time.sleep(0.1)
                elif a2[2] not in ls:
                    a = 'Wrong Input, Check The File Name'
                    conn2.send(a)
                    time.sleep(0.1)
                else :
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
                    conn2.send(result)
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
                conn2.send(result)
                time.sleep(0.1)

            elif a2[0] == str('download') and a2[1] == str('tcp') and len(a2) >= 3 :
                filename = a2[1]
                ls = os.listdir('./')
                temp = filename in ls
                conn2.send(str(temp))
                time.sleep(0.1)
                if filename in ls :
                    f = open(filename,'rb')
                    l = f.read(1024)
                    while (l):
                       conn2.send(l)
                       l = f.read(1024)
                    time.sleep(0.1)
                    mode = oct(stat.S_IMODE(os.stat(filename).st_mode))
                    conn2.send(str(mode))
                    f.close()
                else :
                    a = 'Wrong File Name'
                    conn2.send(a)
                    time.sleep(0.1)

            elif a2[0] == str('download') and a2[1] == str('udp'):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                filename = a2[2]
                ls = os.listdir('./')
                temp = filename in ls
                sock.sendto(str(temp),(host,portUdp))
                time.sleep(0.1)
                if filename in ls :
                    f = open(filename,'rb')
                    l = f.read(1024)
                    while (l):
                       sock.sendto(l,(host,portUdp))
                       l = f.read(1024)
                    time.sleep(0.1)
                    mode = oct(stat.S_IMODE(os.stat(filename).st_mode))
                    conn2.send(str(mode))
                    f.close()
                else :
                    a = 'Wrong File Name'
                    sock.sendto(a,(host,portUdp))
                    time.sleep(0.1)
                sock.close()

            else :
                a = 'Wrong Input Check The Command'
                conn2.send(a)
                time.sleep(0.1)
            conn2.close()

class SendThread(Thread):

    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val

    def run(self):
        s2 = socket.socket()
        s2.bind((host, port2))
        s2.listen(5)
        while True:
            conn2, addr2 = s2.accept()
            command = raw_input("\n Enter command >>")
            conn2.send(command)
            time.sleep(0.1)
            a = command.split(" ")
            if a[0] != 'download':
                nameFile = conn2.recv(1024)
                t = nameFile.split('@')
                for files in t :
                    print files
            else :
                if len(a) >=3 and (len(a)>=1 and a[1] == 'udp') :
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.bind((host, portUdp))
                    data1,addr = sock.recvfrom(1024)
                    print data1 + " => data1"
                    #print data + ' recieving'
                    if data1 == 'True' :
                        #data,addr = sock.recvfrom(1024)
                        print "loop 1 recieving"
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
                if len(a) >=3 and (len(a)>1 and a[1] == 'tcp') :
                    data = conn2.recv(1024)
                    if data == 'True' :
                        nameFile = a[2]
                        with open(nameFile, 'wb') as f:
                            while True:
                                data = conn2.recv(1024)
                                if not data:
                                    break
                                f.write(data)
                        mode = conn2.recv(1024)
                        mode = int(mode,8)
                        os.chmod(nameFile,mode)
                    else :
                        data = conn2.recv(1024)
                        print data
            conn2.close()
        print('connection closed')

class RecieveUpdate(Thread):

    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val

    def run(self):
        s2 = socket.socket()
        s2.bind((host, port3))
        s2.listen(5)
        while True:
            conn2, addr2 = s2.accept()
            command = conn2.recv(1024)
            a2 = command.split(" ")
            if a2[0] == str('update') :
                #print "Update Started"
                ls = os.listdir('./')
                d = '@'
                conn2.send(str(len(ls)))
                time.sleep(0.1)
                for files in ls :
                    result = []
                    result.append(str(files))
                    data1 = os.stat(files)
                    tempTime = int(data1.st_mtime)
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
                    conn2.send(result)
                    time.sleep(0.1)

            elif a2[0] == str('download') :
                filename = a2[1]
                f = open(filename,'rb')
                l = f.read(1024)
                while (l):
                   conn2.send(l)
                   l = f.read(1024)
                time.sleep(0.1)
                f.close()
                mode = oct(stat.S_IMODE(os.stat(filename).st_mode))
                print mode
                conn2.send(str(mode))
                time.sleep(0.1)

            conn2.close()


class SendUpdate(Thread):

    def __init__(self, val):
        ''' Constructor. '''
        Thread.__init__(self)
        self.val = val
        self.startTime = 0

    def run(self):
        s2 = socket.socket()
        s2.bind((host, port4))
        s2.listen(5)
        while True:
            conn2, addr2 = s2.accept()
            #self.startTime = time.time()
            currFiles = os.listdir('./')
            filesToDwnld = []
            conn2.send('update')
            time.sleep(0.1)
            reply = conn2.recv(1024)
            #print "Number of files " + str(reply) + '\n'
            for i in range(int(reply)) :
                r = conn2.recv(1024)
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
            conn2.close()
            #"Download file"
            #print filesToDwnld
            for files in filesToDwnld :
                conn2, addr2 = s2.accept()
                command = 'download ' + files
                conn2.send(command)
                time.sleep(0.1)
                with open(files, 'wb') as f:
                    while True:
                        data = conn2.recv(1024)
                        if not data:
                            break
                        f.write(data)
                mode = conn2.recv(1024)
                mode = int(mode,8)
                os.chmod(files,mode)
                print 'file ' + files + ' updated'
                conn2.close()
            time.sleep(15)
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
   myThreadOb4.start()
   time.sleep(0.1)
   myThreadOb3.start()

   # Wait for the threads to finish...
   myThreadOb1.join()
   myThreadOb2.join()
   myThreadOb3.join()
   myThreadOb4.join()

   print('Main Terminating...')
