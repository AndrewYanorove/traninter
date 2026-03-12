import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'Работа Ни Виртуальный тренажер (1).py',
    '--onefile',
    '--windowed',
    '--name=ЭлектроКвест',
    '--icon=NONE',
    '--add-data=.:.',
    '--clean',
])
