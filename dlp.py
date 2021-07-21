import os
import time
import types

import win32api,win32gui,win32file


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import re
import cv2
from pdf2image import convert_from_path
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError)
import pytesseract

pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract"


def pdf_extract(src_path):
    #print("---!pdf_extract!---")
    print(src_path)
    p = re.compile("\d{2}([0]\d|[1][0-2])([0][1-9]|[1-2]\d|[3][0-1])[-]*[1-4]\d{6}")
    dpi = 800
    
    pages = convert_from_path(src_path, dpi)

    images = []
    i = 1
    for page in pages:
        image_name = "Page_" + str(i) + ".jpg"
        page.save(image_name, "JPEG")
        images.append("Page_" + str(i) + ".jpg")
        i = i + 1

    for image in images:
        srcImage = cv2.imread(image)
        #hacv2.namedWindow('img', cv2.WINDOW_NORMAL)
        #cv2.imshow('img', srcImage)
        #cv2.waitKey(1)
        
        text = pytesseract.image_to_string(srcImage, "kor")
        #print(text)
        m2=p.finditer(text)
    
    count=0
    for id in m2:
        count=count+1
        #print(id.group())
        
    if count>0 :
       print("--!Warning!--")
    else :
        print("--!NO Social Secure Number!--")
    

class Handler(FileSystemEventHandler):
#FileSystemEventHandler 클래스를 상속받음.
#아래 핸들러들을 오버라이드 함

    #파일, 디렉터리가 move 되거나 rename 되면 실행
    def on_moved(self, event):
        if event.is_directory :
            print(event)
        else:
            """
            Fname : 파일 이름
            Extension : 파일 확장자 
            """
            Fname, Extension = os.path.splitext(os.path.basename(event.src_path))
            if Extension == '.pdf':
                pdf_extract(event.src_path)

    def on_created(self, event): #파일, 디렉터리가 생성되면 실행
        if event.is_directory:
            print(event)
        else:
            """
            Fname : 파일 이름
            Extension : 파일 확장자 
            """
            Fname, Extension = os.path.splitext(os.path.basename(event.src_path))
            if Extension == '.pdf':
                pdf_extract(event.src_path)



    def on_deleted(self, event): #파일, 디렉터리가 삭제되면 실행
        print(event)

    def on_modified(self, event): #파일, 디렉터리가 수정되면 실행
        if event.is_directory:
            print(event)
        else:
            """
            Fname : 파일 이름
            Extension : 파일 확장자 
            """
            Fname, Extension = os.path.splitext(os.path.basename(event.src_path))
            if Extension == '.pdf':
                pdf_extract(event.src_path)





class Watcher :
    def __init__(self,path):
        print("감시중...")
        self.event_handler = None
        self.observer=Observer()
        self.target_directory=path
        self.currentDirectorySetting()

    def currentDirectorySetting(self):
        print("====================================")
        print("현재 작업 디렉토리:  ", end=" ")
        os.chdir(self.target_directory)
        print("{cwd}".format(cwd=os.getcwd()))
        print("====================================")

    def run(self):
        self.event_handler = Handler()  # 이벤트 핸들러 객체 생성
        self.observer.schedule(
            self.event_handler,
            self.target_directory,
            recursive=False
        )
        self.observer.start()  # 감시 시작
        try:
            while True:  # 무한 루프
                time.sleep(1)  # 1초 마다 대상 디렉토리 감시
        except KeyboardInterrupt as e:  # 사용자에 의해 "ctrl + z" 발생시
            print("감시 중지...")
            self.observer.stop()  # 감시 중단



def get_drive():
    '''
    Drive_TYPES
    0 Unknown
    1 No Root Directory
    2 Removable Disk
    3 Local Disk
    4 Network Drive
    5 Compact Disc
    6 Ran Disk
    '''
    drive = win32api.GetLogicalDriveStrings()
    drive = drive.split('\000')[:-1]
    #print(drive)
    drive_list = []
    rdrive = []
    for drv in drive:
        #print(win32file.GetDriveType(drv))
        if win32file.GetDriveType(drv) == 2:
            drive_list.append(drv)
    for drv in drive_list:
        try :
            if os.path.getsize(drv)>=0:
                rdrive.append(drv)
        except OSError:
            pass
    return rdrive

def detect_device():
    print('Detecting....')
    time.sleep(3)
    devices = set(get_drive())
    #print(devices)
    if(len(devices)):
        for drive in devices:
            print("The drives added :" + drive)
            w=Watcher(drive)
            w.run()



if __name__ == '__main__': #본 파일에서 실행될 때만 실행되도록 함
    while True:
        detect_device()