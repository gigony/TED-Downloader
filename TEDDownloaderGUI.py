# -*- coding: utf-8 -*-
import locale
from bs4 import BeautifulSoup
locale.setlocale(locale.LC_ALL, '')

import os
import sys
import json
import urllib
import urllib2
import ConfigParser
import codecs
import time
import socket
import glob
from urllib import *
from Tkinter import *
import Queue
import threading,thread
import functools

class myURLOpener(urllib.FancyURLopener):
    """Create sub-class in order to overide error 206.  This error means a
       partial file is being sent,
       which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass



# Convert TED Subtitles to SMI Subtitles
def convertTEDSubtitlesToSMISubtitles(jsonString,talkIntroDuration) :
    global className,transLang,iso639ID,iso3166ID
    smiContent = '''<SAMI>
<HEAD>
<TITLE> TED Downloader by gigony (http://gigony.tistory.com ) </TITLE>
'''+styleText%{"className":className,"transLang":transLang,"iso639ID":iso639ID,"iso3166ID":iso3166ID}+'''
</HEAD>
<BODY>
'''
    if not transLang=='English':
        jsonObject = json.loads( jsonString[0])
        for caption in jsonObject['captions'] :
            smiContent+='<SYNC Start=%s><P Class=%s>%s'%(str(talkIntroDuration + caption['startTime']),className,os.linesep)
            smiContent+= caption['content'] +os.linesep
    jsonObject = json.loads( jsonString[1])
    if not jsonObject.has_key('captions'):
        smiContent+='<SYNC Start=%s><P Class=ENCC>%s'%(str(talkIntroDuration),os.linesep)
        smiContent+= "Subtitle is not prepared yet."+os.linesep
        smiContent+= "Please re-download the subtitle a few days later"+os.linesep
    else:
        for caption in jsonObject['captions'] :
            smiContent+='<SYNC Start=%s><P Class=ENCC>%s'%(str(talkIntroDuration + caption['startTime']),os.linesep)
            smiContent+= caption['content'] +os.linesep
    smiContent+='''</BODY>
</SAMI>'''
    return smiContent

# Convert TED Subtitles to TXT Subtitles
def convertTEDSubtitlesToTXTSubtitles(jsonString) :
    global transLang
    txtContent=''
    if not transLang=='English':
        jsonObject = json.loads( jsonString[0])
        txtContent='##'+transLang+'##'+ os.linesep
        for caption in jsonObject['captions'] :
            if not txtContent.endswith(' '):
                txtContent+=' '
            txtContent+= caption['content']
    jsonObject = json.loads( jsonString[1])
    txtContent+=os.linesep +'##English##'+ os.linesep
    if not jsonObject.has_key('captions'):
        return None
    else:
        for caption in jsonObject['captions'] :
            if not txtContent.endswith(' '):
                txtContent+=' '
            txtContent+= caption['content']
    return txtContent
    
def getTEDSubtitlesByTalkID ( talkId , language ) :
    tedSubtitleUrl = 'http://www.ted.com/talks/subtitles/id/' + str(talkId) + '/lang/' + language
    req = urllib2.Request(tedSubtitleUrl)
    response = urllib2.urlopen(req)
    result = response.read()
    return ( result )

    
def getTranslationList(language):
    global encoding,stopRetriveList

    resultList=[]
    titleList=[]
    oldtext=""    
    pageIndex=1
    while True:
        try:            
            req = urllib2.Request('http://www.ted.com/talks?lang=%s&event=&duration=&sort=newest&tag=&page=%d'%(language,pageIndex))
            req.add_header("Host","www.ted.com")
            req.add_header("Connection","keep-alive")
            req.add_header("Connection","close")
            req.add_header("X-Requested-With","XMLHttpRequest")
            req.add_header("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5")
            req.add_header("Accept","*/*")
            req.add_header("Referer","http://www.ted.com/talks?lang=ko&event=&duration=&sort=newest&tag=")
            # req.add_header("Accept-Encoding","gzip,deflate,sdch")
            req.add_header("Accept-Language","ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4")            
            r = urllib2.urlopen(req,timeout=1.5)            
            text=r.read()
            r.close()                        
            if text==oldtext:
                break
            oldtext=text
            
            soup = BeautifulSoup(text)
            for link in soup.find_all('li'):          
              em=link.find('em')
              postInfo=em.get_text().replace("\n","").replace("\t","")
              a=link.find('a')
              title=a['title']
              href=a['href']
              resultList+=['http://www.ted.com'+href]
              titleList+=[postInfo+"|"+title]
            pageIndex=pageIndex+1
            
            if stopRetriveList: # if canceled
                return ([],[])
                        
            print ".",
    
        except Exception,msg:
            print 't',
            time.sleep(0.1)         
          

    txtFile = open ( './VIDEO/'+'titleList.txt' , 'w' )
    addFile = open ( './VIDEO/'+'titleList-address.txt' , 'w' )
    for i in range(len(titleList)):
    #for element in titleList:
        txtFile.write( titleList[i].encode ( encoding,'xmlcharrefreplace').strip() )        
        txtFile.write(os.linesep)
        addFile.write( titleList[i].encode ( encoding,'xmlcharrefreplace').strip() )        
        addFile.write("\t|"+resultList[i].strip())
        addFile.write(os.linesep)
    txtFile.close()
    addFile.close()
    return ( resultList,titleList )

def getConfig():
    global config,transLang,tedLangID,iso639ID,iso3166ID,encoding,autoDown,videoQuality,downVideo,downAudio,className
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')
    try:
        transLang = config.get('Config','Lang')
    except (ConfigParser.NoSectionError,ConfigParser.NoOptionError):
        config.add_section('Config')
        lang=locale.getlocale()[0].split('_')[0]
        config.set('Config','Lang',lang)
        transLang=lang
    try:
        encoding=config.get('Config','Encoding')
    except ConfigParser.NoOptionError:
        config.set('Config','Encoding',sys.stdout.encoding)
        encoding=sys.stdout.encoding
    try:
        className=config.get('Config','ClassName')
    except ConfigParser.NoOptionError:
        config.set('Config','ClassName','KRCC')
        className='KRCC'      
    try:
        autoDown=config.getboolean('Config','Auto_Down')
    except ConfigParser.NoOptionError:
        config.set('Config','Auto_Down','false')
        autoDown=False        
    try:
        videoQuality=config.getint('Config','Quality')
    except ConfigParser.NoOptionError:
        config.set('Config','Quality',1)
        videoQuality=1
    try:
        downVideo=config.getboolean('Config','Down_Video')
    except ConfigParser.NoOptionError:
        config.set('Config','Down_Video','true')
        downVideo=True
    try:
        downAudio=config.getboolean('Config','Down_Audio')
    except ConfigParser.NoOptionError:
        config.set('Config','Down_Audio','false')
        downAudio=False
        
    with open('./config.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()
    isFound=False
    with codecs.open('./language.txt',encoding='utf-8') as langfile:
        for langText in langfile:
            tokens=langText.replace('\r','').replace('\n','').split('\t')
            if tokens[0]==transLang:
                tedLangID,iso639ID,iso3166ID=(tokens[2],tokens[2],tokens[3])
                isFound=True
        langfile.close()
    return isFound

def getStyle():
    global styleText
    try:
        with open('./style.txt','r') as stylefile:
            styleText=stylefile.read()
            stylefile.close()
    except Exception,msg:
        print msg
        return False
    return True

def isExistTEDFile(address,fileList):
    splits = address.split ( '/' )
    pattern = '_'+splits[len ( splits )-1].split ('.')[0]
    for filename in fileList:
        if filename.find(pattern)>=0:
            filename=filename[:-3]
            if os.access(filename+'url',os.F_OK) or (((os.access(filename+'mp3',os.F_OK) and os.path.getsize(filename+'mp3')>0) or (os.access(filename+'mp4',os.F_OK) and os.path.getsize(filename+'mp4')>0)) and os.access(filename+'smi',os.F_OK) and os.path.getsize(filename+'smi')>0 and os.access(filename+'txt',os.F_OK) and os.path.getsize(filename+'txt')>0):
                return True
    return False		
    
    
def initProgram():
    global stopRetriveList
    socket.setdefaulttimeout(300)
    print '##########################################################'
    print '## TED Video & Subtitle Downloader Ver 2.3 (2012-11-04) ##'
    print '##                                                      ##'
    print '##                                       made by gigony ##'
    print '##                            http://gigony.tistory.com ##'    
    print '##             https://github.com/gigony/TED-Downloader ##'
    print '##########################################################'
    print
    isConfigOK=getConfig()
    if not isConfigOK:
        print "Config.ini file is not correct! Please run 'config.exe'"        
        return False
    isStyleOK=getStyle()
    if not isStyleOK:
        print "style.txt file is not correct! Please modify 'style.txt'"
        return False
    
    # make VIDEO folder
    if not os.path.exists("./VIDEO/"):
        os.makedirs("./VIDEO/")
    
    stopRetriveList=False
    return True

        
def getTEDFileList():    
    return glob.glob('VIDEO/*.mp4')+glob.glob('VIDEO/*.url')
    

class App:
    def __init__(self):
        global tedLangID
        print 'Loading the talk list...',
        self.tedAddressList,self.titleList=getTranslationList(tedLangID)
        fileList=getTEDFileList()
        count=0
        self.listbox=[]
        for title in self.titleList:
            if not isExistTEDFile(self.tedAddressList[count],fileList):
                self.listbox+=[count]            
            count=count+1
        print 'Done!'
        
    def download(self):
        global tedList
        tedList=[]
        print '==   List   =='        
        for item in self.listbox:
            tedList+=[(self.titleList[self.item],self.tedAddressList[item])]
            print self.tedAddressList[item]
        print		
        
class GUIApp:
    def __init__(self,master):
        global qualityValue,tedLangID,videoQuality,downAudio,isDownAudio        
        self.root=master
        qualityValue=IntVar()
        isDownAudio=IntVar()
        master.configure(width=600,height=400)
        
        self.button=Button(master,text='Download',command=self.download)
        self.button.pack(side=BOTTOM)
        
        self.refreshBtn=Button(master,text='Refresh List',command=self.refresh_list)        
        self.refreshBtn.pack(side=BOTTOM)        
        
        self.downAudioBtn=Checkbutton(master,text='Download Audio',variable=isDownAudio)
        self.downAudioBtn.pack(side=BOTTOM)
        if downAudio:
            self.downAudioBtn.select()        

        QUALITY=[("Low-res",0),("Standard-res",1),("Hi-res",2)]
        for text, mode in QUALITY:
          resBtn=Radiobutton(master,text=text,variable=qualityValue,value=mode)
          resBtn.pack(side=BOTTOM, anchor=W, fill='x')
        qualityValue.set(videoQuality)
        
        scrollbar =  Scrollbar(master)        
        self.listbox=Listbox(master,yscrollcommand=scrollbar.set,selectmode=EXTENDED)    
        scrollbar.config(command=self.listbox.yview)        
        scrollbar.pack(side=RIGHT,fill=Y)                
        self.listbox.pack(side=BOTTOM,fill=BOTH,expand=1)
        
        Label(master,text='Text to find:').pack(side=LEFT)
        self.edit = Entry(master)
        self.edit.pack(side=LEFT, fill=BOTH, expand=1)
        self.edit.focus_set()
        self.edit.bind('<Return>', self.on_enterkey)
        butt = Button(master, text='Find')
        butt.pack(side=RIGHT)
        butt.config(command=self.find_btn)
        
        self.queue=None
        self.isRefreshing=False
        self.titleList=[]
        self.resultList=[]
        self.fileList=[]        
        
        self.load_video_list()
    def find_btn(self):
        pattern=self.edit.get().lower()
        
        selectedSet=set()
        curSel=self.listbox.curselection()
        for i in curSel:
            selectedSet.add(self.indexList[int(i)])
        
        if pattern=='':
            idxList=list(set(range(len(self.titleList)))-selectedSet)            
        else:
            self.fileList=getTEDFileList()
            idxList=set()
            count=0            
            for title in self.titleList:
                if title.lower().find(pattern)>=0:
                    idxList.add(count)
                count+=1
            idxList=list(idxList-selectedSet)
        idxList.sort()
        selectedList=list(selectedSet)
        selectedList.sort()
        idxList=selectedList+idxList
        self.indexList=idxList
        self.update_video_list(selectedSet)
        self.edit.delete(0,END) 
        self.listbox.see(len(selectedList)-1)         
        self.listbox.focus_set()
    def on_enterkey(self,key):
        self.find_btn()           

    def load_video_list(self):        
        if os.access('./VIDEO/'+'titleList-address.txt',os.F_OK):
            print 'Loading the talk list...',
            addFile = open ( './VIDEO/'+'titleList-address.txt' , 'r' )
            lines=addFile.readlines()
            resultList=[]
            titleList=[]
            for line in lines:            
                item=line.split("\t|")
                if len(item)==2:
                    titleList+=[item[0].decode(encoding)]
                    resultList+=[item[1].decode(encoding)]                   
                    
            addFile.close()    
            self.tedAddressList,self.titleList=(resultList,titleList)
            self.indexList=range(len(titleList))
            self.update_video_list()
        else:
            self.refresh_list()
        
    def check_me(self):
        try:
            while True:
                isOK= self.queue.get_nowait()
                self.queue=None                 
                if isOK:                    
                    self.indexList=range(len(self.titleList))
                    self.update_video_list()
                    
                self.isRefreshing=False
                return
        except Queue.Empty:
            pass        
        self.root.after(1000, self.check_me)
        
    def refresh_list(self):
        if self.isRefreshing:
            return        
        print 'Loading the talk list...',
        self.isRefreshing=True
        self.queue = Queue.Queue()
        self.check_me()
        thread.start_new_thread(self.get_video_list,())
    def update_video_list(self,selSet=set()):
        self.fileList=getTEDFileList()
        size=self.listbox.size()
        self.listbox.delete(0,size-1)
        count=0        
        for item in self.indexList:
            self.listbox.insert(END,self.titleList[item])            
            if isExistTEDFile(self.tedAddressList[item],self.fileList):                
                self.listbox.itemconfig(count,bg='white',fg='gray')
            if item in selSet:
                self.listbox.select_set(count)
            count=count+1
        print count,"^^"
        print 'Done!'
        
    def get_video_list(self):
        self.tedAddressList,self.titleList=getTranslationList(tedLangID)
        self.queue.put(True)
        
        
    def download(self):
        global config,tedList,qualityValue,videoQuality,downAudio,isDownAudio
        
        if self.queue is not None:
            self.queue.put(False)
        
        items=self.listbox.curselection()
        videoQuality=qualityValue.get()
        if isDownAudio.get()==1:
            downAudio=True
        else:
            downAudio=False
        try:
            items=map(int,items)
        except ValueError:pass            
        tedList=[]
        print '==   List   =='
        for item in items:
            tedList+=[(self.titleList[self.indexList[item]],self.tedAddressList[self.indexList[item]])]
            print self.tedAddressList[self.indexList[item]]
        print
        self.root.destroy()
        config.set('Config','Quality',qualityValue.get())   

        with open('./config.ini', 'w') as configfile:
            config.write(configfile)
            configfile.close()

def initComponent():
    global autoDown
    if autoDown:
        app=App()
        app.download()
    else:
        root=Tk(className=' TED Downloader by gigony')        
        root.geometry("%dx%d" % (600,400))
        app=GUIApp(root)    
        root.mainloop()    
        
def downloadHook(blockNumber,blockSize,totalSize):
    global downloadCount
    if downloadCount==-1:
        print '  Total Size:'+str(totalSize) + ' bytes'
        print "  Downloading...",
    if int(blockNumber*blockSize*10/totalSize)>downloadCount:
        downloadCount=int(blockNumber*blockSize*10/totalSize)
        print downloadCount,

# this method refer to http://code.activestate.com/recipes/83208-resuming-download-of-a-file/
def download_file(videoURL,filename,isStopped):
    global downloadCount    
    if isStopped:
        filePath='./VIDEO/' + filename
        loop = True    
        existSize = 0
        myUrlclass = myURLOpener()
        if os.path.exists(filePath):
            outputFile = open(filePath,"ab")
            existSize = os.path.getsize(filePath)
            #If the file exists, then only download the remainder
            myUrlclass.addheader("Range","bytes=%s-" % (existSize))
        else:
            outputFile = open(filePath,"wb")

        webPage = myUrlclass.open(videoURL)

        totalSize=int(webPage.headers['Content-Length'])
        #If the file exists, but we already have the whole thing, don't download again
        if totalSize == existSize:
            loop = False
            print "File already downloaded"
        
        numBytes = 0
        while loop:
            data = webPage.read(8192)
            if not data:
                break
            outputFile.write(data)
            numBytes = numBytes + len(data)
        
            
            if downloadCount==-1:
                print '  Total Size:'+str(totalSize) + ' bytes'
                print '  Starts from '+str(existSize) + ' bytes'
                print "  Downloading...",
            if int(numBytes*10/totalSize)>downloadCount:
                downloadCount=int(numBytes*10/totalSize)
                print downloadCount,            

        webPage.close()
        outputFile.close()
        # for k,v in webPage.headers.items():
        #     print k, "=",v
        # print "downloaded", numBytes, "bytes from", webPage.url
        return filename
    else:
        fname,header=urlretrieve(videoURL,'./VIDEO/' + filename,downloadHook)
        return fname

def download(tedList,videoQuality):
    global downloadCount,tedLangID,encoding,downVideo,downAudio,stopRetriveList
    
    stopRetriveList=True
    logFile = './VIDEO/'+'log.txt'
    if os.access(logFile,os.F_OK):
        os.remove(logFile)        
    
    if not os.access('./VIDEO',os.F_OK):
        os.mkdir('./VIDEO')
    for tedItem in tedList:
        ted=tedItem[1]
        isStopped=False
        tryCount=3
        while tryCount>0 :
            try:
                log_print(logFile,"") 
                filename=None
                log_print(logFile,tedItem[0].encode(sys.stdout.encoding,'xmlcharrefreplace'))
                log_print(logFile,'  '+ted)                
                req = urllib2.Request(ted)
                response = urllib2.urlopen(req)                
                result = response.read()
                
                ## Get Talk ID value
                splits = result.split ( '''ti:"''' )
                talkId = splits[1].split ( '"' )[0]                

                # Generate file name
                splits = ted.split ( '/' )
                filename = ('00000'+str(talkId))[-5:]+'_'+splits[len ( splits )-1].split ('.')[0]
                log_print(logFile,'  '+filename)

                ## Get Talk Intro Duration value
                splits = result.split ( "playlist:'" )
                if len(splits)==1:
                    log_print(logFile,'  '+"This is a Youtube video")
                    splits = result.split ( '''<iframe src="''')
                    youtubeURL=splits[1].split('"')[0]
                    log_print(logFile,'  '+youtubeURL)
                    urlFile = open ( './VIDEO/'+filename + '.url' , 'w' )
                    urlFile.write ("""[InternetShortcut]\r\nURL="""+youtubeURL)
                    urlFile.close()                    
                    break
                talkIntroDuration = splits[1].split ( "'" )[0]
                talkIntroDuration = unquote(talkIntroDuration)
                talkIntroDuration = talkIntroDuration.split('''"introDuration":''')[1].split(",")[0]
                talkIntroDuration = int ( talkIntroDuration )*1000
                splits = result.split ( """download_dialog.load('""")
                downloadURL='http://www.ted.com'+splits[1].split("'")[0]
                videoName=downloadURL.split("links/slug/")[1].split("/type")[0]
                log_print(logFile,downloadURL)
                req = urllib2.Request(downloadURL)
                response = urllib2.urlopen(req)
                result = response.read()

                # Get Talk Audio
                if downAudio:
                    audioResult=result.split('''<dt><a href="''')
                    if len(audioResult)>1:
                        audioURL=audioResult[1].split('''">Download to desktop (MP3)</a></dt>''')[0]
                        downloadCount=-1
                        log_print(logFile, "  Downloading from "+audioURL)
                        fname=download_file(audioURL,filename+'.mp3',isStopped)
                        log_print(logFile,'')
                        log_print(logFile,'  %s is saved' % fname)
                    else:
                        log_print(logFile, '    '+'No audio file existed')
                        
                #check mp4/smi/txt file 
                if os.access('./VIDEO/'+filename+'.mp4',os.F_OK) and os.path.getsize('./VIDEO/'+filename+'.mp4')>0 and os.access('./VIDEO/'+filename+'.smi',os.F_OK)and os.path.getsize('./VIDEO/'+filename+'.smi')>0 and os.access('./VIDEO/'+filename+'.txt',os.F_OK)and os.path.getsize('./VIDEO/'+filename+'.txt')>0:
                    log_print(logFile,'    '+filename+'.mp4/smi/txt is already exist')
                    break

                ## Get Talk Video
                if downVideo and not(os.access('./VIDEO/'+filename+'.mp4',os.F_OK) and os.path.getsize('./VIDEO/'+filename+'.mp4')>0 and os.access('./VIDEO/'+filename+'.smi',os.F_OK)and os.path.getsize('./VIDEO/'+filename+'.smi')>0):                    
                    downloadSplits=result.split('''<input name="download_quality"''')
                    numOfDownloadLink=len(downloadSplits)-1
                    postFixList=[]
                    for i in range(1,numOfDownloadLink+1):
                        postFixList=postFixList+[downloadSplits[i].split(''' value="''')[1].split('"')[0]]
                    if videoQuality>=numOfDownloadLink:
                        videoQuality=numOfDownloadLink-1
                    videoURL="http://download.ted.com/talks/%s%s.mp4"%(videoName,postFixList[videoQuality])
                    
                    downloadCount=-1                
                    log_print(logFile,"  Downloading from "+videoURL)                    

                    #fname,header=urlretrieve(videoURL,'./VIDEO/' + filename + '.mp4',downloadHook)
                    fname=download_file(videoURL,filename+'.mp4',isStopped)
                    log_print(logFile,'')
                    log_print(logFile,'  %s is saved' % fname)            
    
                #download smi file
                if not transLang=='English':
                    jsonString1 = getTEDSubtitlesByTalkID ( talkId , tedLangID )
                else:
                    jsonString1 = ''
                jsonString2 = getTEDSubtitlesByTalkID ( talkId , 'eng' )
                smiContent=convertTEDSubtitlesToSMISubtitles((jsonString1,jsonString2),talkIntroDuration)
                smiFile = open ( './VIDEO/'+filename + '.smi' , 'w' )
                smiFile.write ( smiContent.encode ( encoding,'xmlcharrefreplace') )
                smiFile.close ()
                    
                #download txt file
                if jsonString1==None: jsonString1 = getTEDSubtitlesByTalkID ( talkId , tedLangID)
                if jsonString2==None: jsonString2 = getTEDSubtitlesByTalkID ( talkId , 'eng' )
                txtContent=convertTEDSubtitlesToTXTSubtitles((jsonString1,jsonString2))
                if not txtContent==None:
                    txtFile = open ( './VIDEO/'+filename + '.txt' , 'w' )
                    txtFile.write ( txtContent.encode ( encoding,'xmlcharrefreplace'))
                    txtFile.close ()                                
                break
            except Exception,msg:        
                log_print(logFile,str(msg))
                log_print(logFile,'waiting 10 seconds..')
                isStopped=True
                tryCount=tryCount-1
                time.sleep(10)                
        
def log_print(logFile,msg):
    print msg
    f=open ( './VIDEO/'+'log.txt' , 'a' )
    f.write(msg + os.linesep)
    f.close()


tedList=[]
if not initProgram():
    exit()
        
if len(sys.argv)==2:
    tedList=[(' ',sys.argv[1])]
    download(tedList,videoQuality)
else:        
    initComponent()
    download(tedList,videoQuality)
