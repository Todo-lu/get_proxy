__author__ = 'lu'
# _*_ coding: utf-8 _*_
from bs4 import BeautifulSoup
import requests
import http.client
import threading

inFile = open('proxy.txt')
outFile = open('verified.txt', 'w')
lock = threading.Lock()

def getProxyList(targeturl="http://www.xicidaili.com/nn/"):
    countNum = 0
    proxyFile = open('proxy.txt', 'a')

    requestHeader = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}

    for page in range(1, 10):
        url = targeturl + str(page)
        req = requests.get(url, headers=requestHeader)
        htmlDoc = req.text

        soup = BeautifulSoup(htmlDoc, 'html.parser')
        trs = soup.find('table', id='ip_list').find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if tds[0].find('img') is None:
                nation = 'Null'
                locate = 'Null'
            else:
                nation = tds[0].find('img')['alt'].strip()
                locate = tds[3].text.strip()

            ip = tds[1].text.strip()
            port = tds[2].text.strip()
            anony = tds[4].text.strip()
            protocol = tds[5].text.strip()
            speed = tds[6].find('div')['title'].strip()
            time = tds[8].text.strip()

            proxyFile.write('%s|%s|%s|%s|%s|%s|%s|%s\n' % (nation, ip, port, locate, anony, protocol, speed, time))
            print('%s=%s:%s' % (protocol, ip, port))
            countNum += 1
    proxyFile.close()
    return countNum

def verifyProxyList():
    '''
    验证代理的有效性
    '''
    requestHeader = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36"}
    myurl = "http://www.baidu.com/"    

    while True:
        lock.acquire()
        ll = inFile.readline().strip()
        lock.release()
        if len(ll) == 0: break
        line = ll.split('|')
        protocol = line[5]
        ip = line[1]
        port = line[2]

        try:
            conn = http.client.HTTPConnection(ip, port, timeout=5.0)
            conn.request(method='GET', url=myurl, headers=requestHeader)
            res = conn.getresponse()
            lock.acquire()
            print("+++Success:" + ip + ":" + port)
            outFile.write(ll + "\n")
            lock.release()
        except:
            print("---Failure:" + ip + ":" + port)

if __name__ == "__main__":
    tmp = open('proxy.txt', 'w')
    tmp.write('')
    tmp.close()

    proxyNum = getProxyList("http://www.xicidaili.com/nn/")
    print(u"国内高匿：" + str(proxyNum))
    proxyNum = getProxyList("http://www.xicidaili.com/nt/")
    print(u"国内透明：" + str(proxyNum))
    proxyNum = getProxyList("http://www.xicidaili.com/wn/")
    print(u"国外高匿：" + str(proxyNum))
    proxyNum = getProxyList("http://www.xicidaili.com/wt/")
    print(u"国外透明：" + str(proxyNum))

    print(u"\n验证代理有效性:")
    all_thread = []
    for i in range(30):
        t = threading.Thread(target=verifyProxyList)
        all_thread.append(t)
        t.start()

    for t in all_thread:
        t.join()
    
    inFile.close()
    outFile.close()
    print("All End!")