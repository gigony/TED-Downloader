del /s /q dist
python setup-config.py py2exe
python setup.py py2exe
python makePyFiles.py
cp TEDDownloaderGUI.pyc .\dist\
cp TEDDownloaderConfig.pyc .\dist\
pause