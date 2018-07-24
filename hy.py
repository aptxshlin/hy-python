import base64
import os
import re

import execjs
import requests
from bs4 import BeautifulSoup


def getResponse(url):
    headers = {
    'User-Agent':'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Mobile Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    return r

def getManhuaHtml(manhuaurl):
    r = getResponse(manhuaurl)
    manhuahtml = r.text.encode(r.encoding).decode('gbk').encode('utf-8').decode('utf-8')
    return manhuahtml
    
def getManhuaChapterURLs(manhuahtml):
    def listtodict(a):
        chapterurllist = []
        for i in a:
            chapterurllist.append({
            'title':i['title'],
            'chapterurl':i['href']
            })
        chapterurllist = chapterurllist[::-1]
        for i in range(len(a)):
            chapterurllist[i]['chapterid'] = i+1
        return chapterurllist
    soup = BeautifulSoup(manhuahtml,"html.parser")
    a = soup.find('div','c-l').find_all('a')
    return listtodict(a)

def getChapterHtml(chapterurl):
    r = getResponse(chapterurl)
    chapterhtml = r.text.encode(r.encoding).decode('gbk').encode('utf-8').decode('utf-8')
    return chapterhtml

def getPacked(chapterhtml):
    pattern = re.compile(r'packed="(.*)"')
    packed = pattern.findall(chapterhtml)[0]
    return packed
    
def getChapterImgURLs(packed):
    out64 = base64.b64decode(packed)[4:]
    out = str(out64, encoding='utf-8')
    packearr  = execjs.eval(out)
    chapterimgurls = eval(packearr[14:])
    chimgurls = []
    for i in range(len(chapterimgurls)):
        if i + 1 == len(chapterimgurls):break
        chimgurls.append({
            'chapterpaage' : i+1,
            'chapterpageimgurl':chapterimgurls[i]
        })
    return chimgurls
    
def getManhuaName(manhuahtml):
    soup = BeautifulSoup(manhuahtml, "html.parser")
    name = soup.find('div','main-bar').h1.text
    return name

def getManhua(manhuaurl):
    r = getResponse(manhuaurl)
    manhuaid = re.search(r'/(\d+)/',r.url).group().strip('/')
    manhuaurl = r.url
    manhuahtml = getManhuaHtml(manhuaurl)
    manhuaname = getManhuaName(manhuahtml)
    manhuachapterurls = getManhuaChapterURLs(manhuahtml)
    return {
        'id':manhuaid,
        'name':manhuaname,
        'url':manhuaurl,
        'chapterurllist':manhuachapterurls
    }

def getChapter(chapterurl):
    r = getResponse(chapterurl)
    chapterhtml = getChapterHtml(chapterurl)
    chapterurl = r.url
    packed = getPacked(chapterhtml)
    chapterimgurls = getChapterImgURLs(packed)
    return {
        'chapterurl':chapterurl,
        'chapterimgurls':chapterimgurls
    }

def mkManhuadir(id, name):
    folder = os.getcwd() + '\\{}-{}'.format(id, name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder 

def mkChapterdir(manhuadir, chapterid,title):
    folder = manhuadir+'\\{}-{}'.format(chapterid,title)
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def saveImg(chapterdir, cid, imgurl):
    img = requests.get(imgurl)
    with open('{}\\{}.jpg'.format(chapterdir, cid),'wb') as f:
        f.write(img.content)

def download(manhuaurl):
    manhuahost = 'http://m.katui.net'
    manhuaimghost = 'http://att.katui.net/'
    manhua = getManhua(manhuaurl)
    manhuadir = mkManhuadir(manhua['id'],manhua['name'])
    for i in range(len(manhua['chapterurllist'])):
        chapterdir = mkChapterdir(manhuadir, manhua['chapterurllist'][i]['chapterid'], manhua['chapterurllist'][i]['title'])
        print(chapterdir)
        chapterurl = manhua['chapterurllist'][i]['chapterurl']
        chapterurl = manhuahost+chapterurl
        chapter = getChapter(chapterurl)
        for j in range(len(chapter['chapterimgurls'])):
            pageimgurl = manhuaimghost + chapter['chapterimgurls'][j]['chapterpageimgurl']
            saveImg(chapterdir,chapter['chapterimgurls'][j]['chapterpaage'],pageimgurl)
            print('\t'+pageimgurl)
print(download('http://m.katui.net/manhua/1/'))
