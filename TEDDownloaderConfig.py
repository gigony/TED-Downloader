# -*- coding: utf-8 -*-
from Tkinter import *
import ConfigParser
import codecs
import locale
import os

locale.setlocale(locale.LC_ALL, '')


styleTextTemplate='''<STYLE TYPE="text/css">
<!--
P { margin-left:2pt; margin-right:2pt; margin-bottom:1pt;
    margin-top:1pt; font-size:20pt; text-align:center;
    font-family:Arial, Sans-serif; font-weight:bold; color:white;
    }
.%(className)s {Name: %(transLang)s; lang: %(iso639ID)s-%(iso3166ID)s; SAMI_TYPE: CC;}
.ENCC {Name: English; lang: en-US; SAMI_TYPE: CC;}
-->
</STYLE>'''

langfileTextTemplate='''Afrikaans    afr    af    AF
Albanian    alb    sq    AL
Arabic    ara    ar    XX
Armenian    arm    hy    AM
Assamese    asm    as    XX
Azerbaijani    aze    az    AZ
Basque    baq    eu    XX
Bengali    ben    bn    BD
Bislama    bis    bi    XX
Bosnian    bos    bs    BA
Bulgarian    bul    bg    BG
Burmese(Myanmar)    bur    my    MM
Catalan    cat    ca    XX
Chinese(Simplified)    chi_hans    zh    CN
Chinese(Traditional)    chi_hant    zh    CN
Chinese,Yue(Cantonese)    yue    zh    CN
Croatian    scr    hr    HR
Czech    cze    cs    CZ
Danish    dan    da    XX
Dutch    dut    nl    XX
English    eng    en    US
Esperanto    epo    eo    XX
Estonian    est    et    EE
Filipino(Pilipino)    fil    xx    XX
Finnish    fin    fi    XX
French(Canada)    fre_ca    fr    FR
French(France)    fre_fr    fr    FR
Galician    glg    gl    XX
Georgian    geo    ka    GE
German    ger    de    DE
Greek    gre    el    GR
Gujarati    guj    gu    XX
Hausa    hau    ha    XX
Hebrew    heb    he    XX
Hindi    hin    hi    XX
Hungarian    hun    hu    HU
Icelandic    ice    is    IS
Indonesian    ind    id    ID
Italian    ita    it    IT
Japanese    jpn    ja    JP
Kannada    kan    kn    XX
Kazakh    kaz    kk    KZ
Khmer(Cambodian)    khm    km    KH
Kirghiz(Kyrgyz)    kir    ky    KG
Korean    kor    ko    KR
Latvian    lav    lv    LV
Lithuanian    lit    lt    LT
Macedonian    mac    mk    MK
Malay    may    ms    MY
Malayalam    mal    ml    XX
Maltese    mlt    mt    XX
Marathi    mar    mr    XX
Mongolian    mon    mn    MN
Nepali    nep    ne    NP
Norwegian    nor    no    NO
Norwegian,Bokmål(Bokmaal)    nob    nb    NO
Norwegian,Nynorsk    nno    nn    NO
Persian(Farsi)    per    fa    XX
Polish    pol    pl    PL
Portuguese(Brazil)    por_br    pt    BR
Portuguese(Portugal)    por_pt    pt    PT
Romanian    rum    ro    RO
Romanian,Macedo(Aromanian)    rup    ro    RO
Russian    rus    ru    RU
Serbian    scc    sr    CS
Serbo-Croatian    hbs    hr    HR
Slovak    slo    sk    SK
Slovenian    slv    sl    SI
Spanish    spa    es    ES
Swahili    swa    sw    XX
Swedish    swe    sv    SE
Tagalog    tgl    tl    XX
Tamil    tam    ta    XX
Telugu    tel    te    XX
Thai    tha    th    TH
Turkish    tur    tr    TR
Ukrainian    ukr    uk    UA
Urdu    urd    ur    XX
Uzbek    uzb    uz    UZ
Vietnamese    vie    vi    VN'''



def getConfig():
    global config, transLang, encoding, autoDown, videoQuality, downAudio, downVideo, className
    config = ConfigParser.RawConfigParser()
    config.read('./config.ini')
    try:
        transLang = config.get('Config', 'Lang')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        config.add_section('Config')
        lang = locale.getlocale()[0].split('_')[0]
        config.set('Config', 'Lang', lang)                
        transLang = lang
    try:
        encoding = config.get('Config', 'Encoding')
    except ConfigParser.NoOptionError:
        config.set('Config', 'Encoding', sys.stdout.encoding)
        encoding = sys.stdout.encoding
    try:
        className = config.get('Config', 'ClassName')
    except ConfigParser.NoOptionError:
        config.set('Config', 'ClassName', 'KRCC')
        className = 'KRCC'
    try:
        autoDown = config.getboolean('Config', 'Auto_Down')
    except ConfigParser.NoOptionError:
        config.set('Config', 'Auto_Down', 'false')
        autoDown = False        
    try:
        videoQuality = config.getint('Config', 'Quality')
    except ConfigParser.NoOptionError:
        config.set('Config', 'Quality', 1)
        videoQuality = 1
    try:
        downAudio = config.getboolean('Config', 'Down_Audio')
    except ConfigParser.NoOptionError:
        config.set('Config', 'Down_Audio', 'false')
        downAudio = False
    try:
        downVideo = config.getboolean('Config', 'Down_Video')
    except ConfigParser.NoOptionError:
        config.set('Config', 'Down_Video', 'true')
        downVideo = True
        
    with open('./config.ini', 'w') as configfile:
        config.write(configfile)
        configfile.close()

def getStyle():
    global styleText, styleTextTemplate
    try:
        with open('./style.txt', 'r') as stylefile:
            styleText = stylefile.read()
            stylefile.close()
    except Exception, msg:
        print msg
        print 'created a new style file'
        styleText = styleTextTemplate 
        with open('./style.txt', 'w') as stylefile:
            stylefile.write(styleText)
            stylefile.close()

    
def initProgram():
    print '###################################################################'
    print '##        TED Video & Subtitle Downloader Configuration          ##'
    print '##                                                               ##'
    print '##                                                made by gigony ##'
    print '##                                     http://gigony.tistory.com ##'
    print '##                      https://github.com/gigony/TED-Downloader ##'    
    print '###################################################################'
    print
    getConfig()    
    getStyle()    

class App:
    def __init__(self, master):
        global transLang, qualityValue, isAutoDown, isDownAudio, isDownVideo, videoQuality, autoDown, downAudio, downVideo, encoding, className
        qualityValue = IntVar()
        isAutoDown = IntVar()
        isDownAudio = IntVar()
        isDownVideo = IntVar()    

        self.button = Button(master, text='Save', command=self.save)
        self.button.pack(side=BOTTOM) 


        self.encodingLabel = Label(master, text="Encoding")
        self.encodingLabel.pack(side=TOP)
        self.encodingText = Text(master, width=10, height=1)
        self.encodingText.insert(END, encoding)
        self.encodingText.pack(side=TOP)
        self.classNameLabel = Label(master, text="Class Name")
        self.classNameLabel.pack(side=TOP)
        self.classNameText = Text(master, width=10, height=1)
        self.classNameText.insert(END, className)
        self.classNameText.pack(side=TOP)	
		
        self.languageLabel = Label(master, text="\nLanguage")
        self.languageLabel.pack(side=TOP)

        QUALITY = [("Low-res", 0), ("Standard-res", 1), ("Hi-res", 2)]
        for text, mode in QUALITY:
          resBtn = Radiobutton(master, text=text, variable=qualityValue, value=mode)
          resBtn.pack(side=BOTTOM, anchor=W, fill='x')
        qualityValue.set(videoQuality)
        
        self.downVideoBtn = Checkbutton(master, text='Download Video', variable=isDownVideo)
        self.downVideoBtn.pack(side=BOTTOM)
        if downVideo:
            self.downVideoBtn.select()
        self.downAudioBtn = Checkbutton(master, text='Download Audio', variable=isDownAudio)
        self.downAudioBtn.pack(side=BOTTOM)
        if downAudio:
            self.downAudioBtn.select()        
        self.autoDownBtn = Checkbutton(master, text='Auto Download', variable=isAutoDown)
        self.autoDownBtn.pack(side=BOTTOM)
        if autoDown:
            self.autoDownBtn.select()
        
        scrollbar = Scrollbar(master)        
        self.listbox = Listbox(master, yscrollcommand=scrollbar.set, selectmode=SINGLE)    
        scrollbar.config(command=self.listbox.yview)        
        scrollbar.pack(side=RIGHT, fill=Y)                
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
                    
        self.languageList = self.getLanguageList()
        count = 0
        found = False
        for languageName in self.languageList:
            self.listbox.insert(END, languageName)
            if languageName == transLang:
                found = True
                self.listbox.selection_set(count)
                self.listbox.see(count)
            count += 1
        if not found:
            self.listbox.selection_set(0)
        
        #delete title-list file
        titleAddressFile = './VIDEO/'+'titleList-address.txt'
        if os.access(titleAddressFile,os.F_OK):
            os.remove(titleAddressFile)
        
    def getLanguageList(self):
        global langfileTextTemplate
        result = []
        try:
            with codecs.open('./language.txt', encoding='utf-8') as langfile:
                for langText in langfile:
                    tokens = langText.replace('\r', '').replace('\n', '').split('\t')
                    result += [tokens[0]]
        except Exception, msg:
            print msg
            print 'created a new language file'
            langfileText=langfileTextTemplate.replace('    ','\t')            
            with open('./language.txt', 'w') as langfile:
                langfile.write(langfileText)
                langfile.close()
            with codecs.open('./language.txt', encoding='utf-8') as langfile:
                for langText in langfile:
                    tokens = langText.replace('\r', '').replace('\n', '').split('\t')
                    result += [tokens[0]]            
        return result

    def save(self):
        global qualityValue, isAutoDown
        items = self.listbox.curselection()
        language = self.listbox.get(items[0])
        encoding = self.encodingText.get(1.0, 2.0)
        className = self.classNameText.get(1.0, 2.0)

        root.destroy()

        config.set('Config', 'Lang', language)            
        config.set('Config', 'Quality', qualityValue.get())            
        if isAutoDown.get() == 1:
            config.set('Config', 'Auto_Down', 'true')
        else:
            config.set('Config', 'Auto_Down', 'false')

        if isDownVideo.get() == 1:
            config.set('Config', 'Down_Video', 'true')
        else:
            config.set('Config', 'Down_Video', 'false')
        if isDownAudio.get() == 1:
            config.set('Config', 'Down_Audio', 'true')
        else:
            config.set('Config', 'Down_Audio', 'false')

        config.set('Config', 'Encoding', encoding)

        config.set('Config', 'ClassName', className)

        with open('./config.ini', 'w') as configfile:
            config.write(configfile)
            configfile.close()
        

def initComponent():
    global root
    root = Tk(className=' TED Downloader Configuration')
    root.geometry("%dx%d" % (300, 400))
    app = App(root)    
    root.mainloop()

initProgram()    
initComponent()



















