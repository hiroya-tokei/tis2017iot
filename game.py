# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys
from time import sleep
import urllib
import os
import subprocess
import json
from datetime import datetime
import requests
import yaml
from time import sleep
import RPi.GPIO as GPIO

PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN)

BASE_DIR = os.path.dirname(__file__)

# ファイルからMS APIキーとkintone設定ファイルのの読み込み
ms_api_key       = yaml.load(open(os.path.join(BASE_DIR, 'conf/ms_api_key.yaml')).read())
# MS Face APIのヘッダ
face_api_headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': ms_api_key['key'],
}
face_api_params = urllib.parse.urlencode({
    'returnFaceId': 'false',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender',
})



def shutter_camera():
    """
    ラズパイカメラで撮影する
    """
    sleep(3)
    # cam.jpgというファイル名、640x480のサイズ、待ち時間5秒で撮影する"
    cmd = "raspistill -o cam.jpg -h 640 -w 480 -t 5000"
    subprocess.call(cmd, shell = True)
count = 0
def detect_faces(filename):
    """
    Microsoft Face APIで画像から顔を検出する
    """

    face_image = open(filename, "r+b").read()

    # Miscosoft Face APIへ画像ファイルをPOST
    response = requests.post('https://westus.api.cognitive.microsoft.com/face/v1.0/detect?%s' % face_api_params, data = face_image, headers=face_api_headers)
    results = response.json()

    if response.ok:
        print('Result-->  {}'.format(results))
    else:
        print(response.raise_for_status())
    return results
    
    for result in results:
        global count
        count+=1
    
SCREEN_SIZE = (640, 480)
 
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("sample")

# フォントの作成
sysfont = pygame.font.SysFont(None, 40)
text = "sample"
rectX   = 200
rectY   = 400


while True:
# 人間センサからデータを読みこむ（0: 検出なし, 1:検出あり）
    human_exists = int(GPIO.input(PIN) == GPIO.HIGH)

    if human_exists:
        print('Human exists!')

        print('Taking a picture in 5 seconds...')
        shutter_camera()
        print('Done.')

        # MS Face APIで顔検出
        print('Sending the image to MS face API...')
        results = detect_faces('cam.jpg')
        print('Done.')

    screen.fill((0,0,0))
    rectY       = 400
    # 図形を描画
    # 黄の矩形
    # テキストを描画したSurfaceを作成
    hello1      = sysfont.render(text, False, (255,255,255))
    for var in range(0, count):
        pygame.draw.rect(screen, (255,255,0), Rect(rectX,rectY,50,50))
        rectY -= 50

    screen.blit(hello1, (500,400))
    
    pygame.draw.rect(screen, (255,255,0), Rect(rectX, rectY, 50, 50))
    #print(rectX)
    #rectY - = 50
    pygame.draw.rect(screen, (255,255,0), Rect(50,50,50,50))
    # 赤の円
    # pygame.draw.circle(screen, (255,0,0), (320,240), 100)
    # 紫の楕円
    #pygame.draw.ellipse(screen, (255,0,255), (400,300,200,100))
    # 白い線
    #pygame.draw.line(screen, (255,255,255), (0,0), (640,480))
    
    pygame.display.update()
    sleep(1)
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()

