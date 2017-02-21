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


# rest interface setting
key = os.getenv("maker_key")
event = os.getenv("maker_event_store_sensor")
trigger_url = 'https://maker.ifttt.com/trigger/' + event + '/with/key/' + key
PIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN)

BASE_DIR = os.path.dirname(__file__)

# ファイルからMS APIキーとkintone設定ファイルのの読み込み
ms_api_key       = yaml.load(open(os.path.join(BASE_DIR, 'conf/ms_api_key.yaml')).read())
kintone_conf = yaml.load(open(os.path.join(BASE_DIR, 'conf/kintone_conf.yaml')).read())
# MS Face APIのヘッダ
face_api_headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': ms_api_key['key'],
}
# kintone APIのヘッダ
kintone_api_headers = {
    'Content-Type': 'application/json',
    'X-Cybozu-API-Token': kintone_conf['token'],
}


face_api_params = urllib.parse.urlencode({
    'returnFaceId': 'false',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender',
})
count = 0


def trigger_ifttt():
    # post data
    #current = str(datetime.now())
    #humanExists = int(GPIO.input(17) == GPIO.HIGH)
    #temp = read_tmp_sensor()
    # post
    payload = {'value1':count ,'value2': 0, 'value3': 0}
    r = requests.post(trigger_url, data=payload)
    print( "success" if r.status_code == 200 else "fail")


def send_face_attr_to_kintone(face_results):
    """
    検出されたすべての顔データをkintoneにPOSTする
    """

    # 顔の検出人数分だけループ
    #for result in face_results:
    if True:
        # 性別と年齢のみ取り出す
        #gender = result['faceAttributes']['gender']
        #age = result['faceAttributes']['age']
        
        record = {"number": {'value': count}}
        payload = {'app': kintone_conf['id'], 'record': record }

        # 1人分をkintoneへPOST
        response = requests.post('https://{}.cybozu.com/k/v1/record.json'.format(kintone_conf['domain']), data=json.dumps(payload), headers=kintone_api_headers)

        if response.ok:
            print("ok")
        else:
            print('Error!')
            print(response.raise_for_status())

def shutter_camera():
    """
    ラズパイカメラで撮影する
    """
    sleep(3)
    # cam.jpgというファイル名、640x480のサイズ、待ち時間5秒で撮影する"
    cmd = "raspistill -o cam.jpg -h 640 -w 480 -t 5000"
    subprocess.call(cmd, shell = True)

def detect_faces(filename):
    """
    Microsoft Face APIで画像から顔を検出する
    """
    global count
    count = 0
    face_image = open(filename, "r+b").read()

    # Miscosoft Face APIへ画像ファイルをPOST
    response = requests.post('https://westus.api.cognitive.microsoft.com/face/v1.0/detect?%s' % face_api_params, data = face_image, headers=face_api_headers)
    results = response.json()

    for result in results:
        #print("a")
        global count
        count+=1
        
    if response.ok:
        print('Result-->  {}'.format(results))
    else:
        print(response.raise_for_status())
    return results
    
    
SCREEN_SIZE = (640, 480)
 
#pygame.init()
#screen = pygame.display.set_mode(SCREEN_SIZE)
#pygame.display.set_caption("sample")

# フォントの作成
#sysfont = pygame.font.SysFont(None, 40)
#text = "sample"
#rectX   = 200
#rectY   = 400

flag=1

while True:
# 人間センサからデータを読みこむ（0: 検出なし, 1:検出あり）
    human_exists = int(GPIO.input(PIN) == GPIO.HIGH)


    #if human_exists:
    if False:
        print('Human exists!')

        print('Taking a picture in 5 seconds...')
        #shutter_camera()
        print('Done.')

        # MS Face APIで顔検出
        print('Sending the image to MS face API...')
        results = detect_faces('pict.jpg')
        print('Done.')

    if flag==1:
        results = detect_faces('pict.jpg')
        flag=0
    else:
        results = detect_faces('pict2.jpg')
        flag=1
        
    #screen.fill((0,0,0))
    #rectY       = 400
    print(count)
    # 図形を描画
    # 黄の矩形
    # テキストを描画したSurfaceを作成
    #hello1      = sysfont.render(text, False, (255,255,255))

    '''for var in range(0, count):
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
    '''
    
    send_face_attr_to_kintone(results)
    #pygame.display.update()
    trigger_ifttt()
    
    sleep(1)
'''
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
'''
