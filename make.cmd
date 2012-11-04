del /s /q dist
python setup-config.py py2exe
python setup.py py2exe
python makePyFiles.py
copy TEDDownloaderGUI.pyc .\dist\
copy TEDDownloaderConfig.pyc .\dist\
pause