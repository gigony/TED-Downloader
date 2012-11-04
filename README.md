TED Downloader
==============

I found that [TED](http://www.ted.com) videos are useful for learning English because 
TED.COM provides subtitles made by many contributors.

I made a simple python GUI application, *TED Downloader*, using tcl/tk.
*TED Downloader* can easily download videos/audios with subtitles.

Screenshots
-----------------
Click to view.

[![ConsoleLog](https://github.com/gigony/TED-Downloader/raw/master/screenshots/ConsoleLog_th.png)](https://github.com/gigony/TED-Downloader/raw/master/screenshots/ConsoleLog.png)
[![TEDDownloader GUI](https://github.com/gigony/TED-Downloader/raw/master/screenshots/TEDDownloaderGUI_th.png)](https://github.com/gigony/TED-Downloader/raw/master/screenshots/TEDDownloaderGUI.png)
[![TedDownloader Configuration](https://github.com/gigony/TED-Downloader/raw/master/screenshots/TEDDownloaderConfig_th.png)](https://github.com/gigony/TED-Downloader/raw/master/screenshots/TEDDownloaderConfig.png)
[![TedDownloader Configuration](https://github.com/gigony/TED-Downloader/raw/master/screenshots/FileList.png)](https://github.com/gigony/TED-Downloader/raw/master/screenshots/FileList.png)


Download
--------

### [Click here to download latest version](https://github.com/gigony/TED-Downloader/raw/master/releaseFiles/TEDDownloader_ver2.2.zip)

Current release is **v2.2**. See the [changelog]



Usage & Development
-------------------

### Configuration

After extracting the zip file, you first need to run **TEDDownloaderConfig.exe** to configure settings.

If executable files cannot be run, showing an error message in a dialog box, please install [vcredist_x86.exe](http://gigony.tistory.com/attachment/cfile2.uf@147C21264CEC9CDA28F7D8.exe).

- `Encoding` is the encoding of the subtitle text.

  example>
    - English  ==> `ascii` or `utf-8`
    - Korean   ==> `cp949` or `utf-8`
    - Japanese ==> `cp932` or `utf-8`
    
- `Class Name` is a language class for the SMI file (subtitle file).   

- `Language` is an additional language for the subtitle.  

SMI format explanation in detail: http://msdn.microsoft.com/en-us/library/ms971327.aspx

`language.txt` is a pre-defined file for the language code.
Each line consists of four different code types of a language
> \[1\) Language name\]    \[2\) langID for TED.com\]    \[3\) iso639 name for SMI\]    \[4\) iso3166 name for SMI\]

The second type is not used not because TED.com currently uses 3rd type as a language code

`style.txt` is a style file for the customization of the subtitle (SMI) style.
  

### Download

Run **TEDDownloaderGUI.exe**.
It will take more than 15 seconds to load the list of videos.

After that, select items by using *ctrl*(or *shift*) key + *mouse click* or *mouse dragging*, and click `Download` button.

You can see video/audio files with subtitle files in **VIDEO** folder.

You may clone this repository and run **TEDDownloaderConfig.py** or **TEDDownloaderGUI.py** directly, instead of using released executable files.

Executable files were generated by [py2exe](http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/)\(py2exe-0.6.9.win32-py2.7\)

### License

TED Downloader is made available under the MIT license.

TED Downloader incorporates code from Beautiful Soup, which is also made available under the MIT license.

[Click here to see the license](https://github.com/gigony/TED-Downloader/blob/master/LICENSE.txt). 



[changelog]: https://github.com/gigony/TED-Downloader/blob/master/CHANGELOG.md





