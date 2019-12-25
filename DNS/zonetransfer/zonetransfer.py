import threading
import os
import re

def platform():
    result = os.popen('whoami').read()[:-2]
    if '\\' in result:
        return True     # Windows
    else:
        return False    # Linux or Mac

print platform()

urls = []
list = open('list.txt')
# format of list as following
# google.com
# facebook.com
for line in list.readlines():
    urls.append(line)

lock = threading.Lock()
index = 0

def zonetransfer():
    global index
    while True:
        lock.acquire()
        if index >= len(urls):
            lock.release()
            break
        domain = urls[index]
        index += 1
        lock.release()
        if platform():
            command = os.popen('nslookup -type=ns ' + domain).read()  # fetch DNS Server List
            dns_servers = re.findall('nameserver = ([\w\.]+)', command)
        else:
            command = os.popen('dig -t ns' + domain).read
            dns_servers = re.findall('NS\t+([\w\.]+)', command)
        for server in dns_servers:
            if len(server) < 5: server += domain
            if platform():
                command = os.popen(os.getcwd() + '\\BIND9\\dig @%s axfr %s' % (server, domain)).read()
            else:
                command = os.popen('dig @%s axfr %s' % (server, domain)).read()
            if command.find('Transfer failed.') < 0 and command.find('connection timed out') < 0 and command.find('XFR size') > 0:
                with open('vulnerable.txt', 'a') as f:
                    f.write('%s\t%s\n' % (server.ljust(30), domain))
                with open('dns\\' + server + '.txt', 'w') as f:
                    f.write(command)
threads = []
for i in range(10):
    t = threading.Thread(target=zonetransfer)
    t.start()
    threads.append(t)

for t in threads:
    t.join()