#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
from datetime import datetime
import argparse
import re

import aiy.audio
import aiy.cloudspeech
import aiy.voicehat

import numpy as np
import collections
from mic_array import MicArray
from pixel_ring import pixel_ring

import sys
#from snowboydetect import SnowboyDetect

import urllib.request, urllib.parse, urllib.error
DEVICE = 0
CARD   = 1
VOLUME = 50
aquest_dir = '/home/pi/AIY-projects-python/src/aquestalkpi/AquesTalkPi'
RATE = 16000
CHANNELS = 8
KWS_FRAMES = 10     # ms
DOA_FRAMES = 800    # ms

default_speech= 'ja-JP'
default_trans = '' #'en-US'
aiy_lang = ['en-US', 'en-GB', 'de-DE', 'es-ES', 'fr-FR', 'it-IT']

#detector = SnowboyDetect('/home/pi/AIY-projects-python/src/examples/voice/snowboy/resources/common.res','/home/pi/AIY-pro$
#detector.SetAudioGain(1)
#detector.SetSensitivity('0.5')
history = collections.deque(maxlen=int(DOA_FRAMES / KWS_FRAMES))

from google.cloud import translate
def translate_text(text, trans_lang):
    if trans_lang == '':
        return text
    else:
      target_lang = trans_lang.split("-")[0]
      translate_client = translate.Client()
      result = translate_client.translate(text, target_language=target_lang)
      return result['translatedText']

def main(): #detect="ja-JP", trans="", mail=""):
    recognizer = aiy.cloudspeech.get_recognizer()
    recognizer.expect_phrase('turn off the light')
    recognizer.expect_phrase('turn on the light')
    recognizer.expect_phrase('blink')
    recognizer.expect_phrase('repeat after me')

    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    aiy.audio.get_recorder().start()
    aiy.i18n.set_language_code(detect)

    import RPi.GPIO as GPIO
    BUTTON = 16
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON, GPIO.IN)

    while True:
     print('Press the button and speak')
     state=GPIO.input(BUTTON)
     if state:
      print("off")
     else:
      print("on")
      #button.wait_for_press()

      i = 0
      convs = []
      convs_trans = []
      while True:
      #try:
        """print('Press the button and speak')
        button.wait_for_press()
        print('Listening...')
        text = recognizer.recognize()
        with MicArray(RATE, CHANNELS, RATE * KWS_FRAMES / 1000)  as mic:
            for chunk in mic.read_chunks():
                history.append(chunk)

                # Detect keyword from channel 0
                #ans = detector.RunDetection(chunk[0::CHANNELS].tostring())
                text = recognizer.recognize() #chunk[0::CHANNELS].tostring())
                print(text)

                #if ans > 0:
                #text = "Yes"
                if not text:
                    print('Sorry, I did not hear you.')
                else:
                    frames = np.concatenate(history)
                    direction = mic.get_direction(frames)
                    pixel_ring.set_direction(direction)
                    print('\n{}'.format(int(direction)))

                    direct_person = str(direction) + "KY"
                    print(direct_person + ' said "', text, '"')"""

      #except KeyboardInterrupt:
        #pass

        #print('Press the button and start conversation')
        #button.wait_for_press()

        bye_words    = ['Goodbye', 'Good bye', 'See you', 'Bye bye', '終わり',  '終わりです',  'さようなら',  'バイバイ']
        progress_words=['completed', 'confirmed', 'delayed', 'finished', 'discussed', 'fixed']
        approve_words= ['agreed', 'approved']
        next_words   = ['next step', 'next Steps', 'next action', 'next actions']
        issue_words  = ['issue', 'issues', 'problem', 'error', 'dificit']
        magic_words  = ['magic minutes', 'magical minutes']

        print('Listening in '+detect+'...')
        text = recognizer.recognize()
        if not text:
            print('Sorry, I did not hear you. Please say again')
        else:

            convDateTime = datetime.now()
            convDateStr = convDateTime.strftime('%Y-%m-%d %H:%M:%S')
            i += 1
            directions = []
            dir = [0, 180, 60, 300, 120, 240]

            for j in range(4):
             directions.extend(dir)
            direction = directions[i] #mic.get_direction(frames)

            pixel_ring.set_direction(direction)
            if direction > 45 and direction <= 135:
              direct = "Right"
            elif direction > 135 and direction <= 225:
              direct = "Back"
            elif direction > 225 and direction <= 315:
              direct = "Left"
            else:
              direct = "Front"
            #direct = str(direction)
            print('>> ' + direct + ' said "' + text + '"')

            if detect == "ja-JP":
                os.system(aquest_dir + ' -g {} {} | aplay -D plughw:{},{}'.format(VOLUME, text, CARD, DEVICE))
            else:
                aiy.audio.say(text, detect)

            if trans:
                trans_text = translate_text(text, trans)
                trans_text = trans_text.replace("&#39;","")
                print('Trans: ' + trans_text)

                if trans in aiy_lang:
                  aiy.audio.say(trans_text, trans)
                elif trans == "ja-JP":
                  os.system(aquest_dir + ' -g {} {} | aplay -D plughw:{},{}'.format(VOLUME, trans_text, CARD, DEVICE))
                else:
                  aiy.audio.say('Nothing to trans!', 'en-US')
            #else: #trans_lang = null then default en-US
                #aiy.audio.say(text, 'en-US')

            keyw = "conv"
            text.lower()

            #elif 'open Magic minutes' in text: #or 'open Magic minutes' or 'start magic minutes' in text:
                #pixel_ring.spin()
                #aiy.audio.say('Ok, Start recording your conversation!')
                #keyw = "MC"

            for m in magic_words:
              if trans_text.find(m) > -1:
                keyw = "MC"
                pixel_ring.spin()
                aiy.audio.say('Ok, make magic minutes!')
                break
            for a in progress_words:
              if trans_text.find(a) > -1:
                keyw = "progress"
                break
            for a in approve_words:
              if trans_text.find(a) > -1:
                keyw = "approve"
                break

            for a in issue_words:
              if trans_text.find(a) > -1:
                keyw = "issue"
                break
            for n in next_words:
              if trans_text.find(n) > -1:
                keyw = "next"
                break
            for b in bye_words:
              if trans_text.find(b) > -1:
                keyw = "bye"
                break

            conv = {"number": i,
                "person": direct,
                "convt": text,
                "keyw": keyw}
            convs.append(conv)
            if trans:
              conv_trans = {"number": i,
                "person": direct,
                "convt": trans_text,
                "keyw": keyw}
              convs_trans.append(conv_trans)


            if text in bye_words:
              if mail:
                  dir_name = convDateTime.strftime('%Y%m%d')
                  dir_path = '/home/pi/AIY-projects-python/msg/' + dir_name + '/'
                  file_name= convDateTime.strftime('%H%M%S') + '.txt'

                  fname    = dir_path + file_name

                  """os.makedirs(dir_path, exist_ok=True)
                  with open(os.path.join(dir_path, file_name), mode) as f:
                  f.write(minutes)

                  try:
                    os.system("sudo mkdir " + dir_path)
                    #os.mkdir(dir_path)
                  except OSError:
                    print("Directory already exists")"""

                  conv_org = ""
                  conv_trans_org = ""
                  progressw   = ""
                  conv_progress=""
                  approvew    = ""
                  conv_approve= ""
                  issuew      = ""
                  issuen      = 0
                  conv_issue  = ""
                  nextw       = ""
                  nextn       = 0
                  conv_next   = ""

                  direct_jp = {"Front":"前席の方の発言",
                               "Right":"右側の方の発言",
                               "Left":"左側の方の発言",
                               "Back":"後席の方の発言"}
                  for con in convs:
                    conv_org += str(con["number"]) + '(' + direct_jp[con["person"]] + '): ' + con["convt"] + '\n'

                  is_are = ["is","was","are","were", "it's", "its"]
                  for con in convs_trans:
                    if con["keyw"] not in ["MC", "MM", "bye"]:
                      conv_trans_org += ' ' + str(con["number"]) + '(' + con["person"] + '): ' + con["convt"] + '\n'
                    if con["keyw"] == "progress":
                      progressw = con["convt"]
                      conv_progress+= ' - ' + progressw + " by " + con["person"] + '\n'
                    if con["keyw"] == "approve":
                      approvew = con["convt"]
                      """for a in approve_words + is_are:
                        approvew = approvew.replace(a, "")"""
                      conv_approve+= ' - ' + approvew + " by " + con["person"] + '\n'
                    if con["keyw"] == "issue":
                      issuen += 1
                      issuew = con["convt"]
                      conv_issue += ' - #' + str(issuen) + ': ' + issuew + ' raised by ' + con["person"] + '\n'
                    if con["keyw"] == "next":
                      nextn += 1
                      nextw = con["convt"]
                      """for a in next_words + is_are:
                        nextw = nextw.replace(a, "")"""
                      conv_next += ' - #' + str(nextn) + ': ' + nextw + '\n'

                  #minutes   = '= Meeting Minutes =\n\n'
                  #minutes_jp= u'= 議事録 =\n\n'
                  minutes    = 'RE: Development Status\n'
                  minutes_jp = '議題: 定例進捗会議\n'
                  minutes   += 'Date: ' +convDateStr + '\n'
                  minutes_jp+= '日付: ' +convDateStr + '\n'
                  minutes   += 'MMinutes by: ' + mail + '\n'
                  minutes_jp+= '作成者: ' + mail + '\n'
                  if conv_progress:
                    minutes+= '\n Project progress:\n'
                    minutes+= conv_progress
                  if conv_approve:
                    minutes+= '\n Approved item(s):\n'
                    minutes+= conv_approve
                  if conv_issue:
                    minutes+= '\n Issue(s):\n'
                    minutes+= conv_issue
                  if conv_next:
                    minutes+= '\n Next action(s):\n'
                    minutes+= conv_next
                  minutes   += '\n Meeting details: \n'
                  minutes_jp+= '\n 会議内容: \n'
                  minutes   += conv_trans_org + '\n'
                  minutes_jp+= conv_org + '\n'
                  minutes   += 'Meeting note is attached:'
                  minutes_jp+= '添付資料:'
                  subject   = '"Todays Meeting minutes (' + convDateStr + ')"'
                  subject_jp= '"本日の議事録 (' + convDateStr + ')"'
                  header_jp = "本日行われましたお打合せの議事録を送付いたします。\n宜しくご査収お願い致します。"
                  header_jp+= "(English follows)\n" if trans else ""
                  header    = "Please find the attached meeting minutes held today.\nPlease let me know if you have any qu$
                  magic_minutes = header_jp + '\n' + minutes_jp
                  magic_minutes+= '\n' + header + '\n' + minutes if trans else ""
                  print(magic_minutes)

                  pixel_ring.spin()

                  os.makedirs(dir_path, exist_ok=True)
                  with open(os.path.join(dir_path, file_name), 'w') as f:
                    f.write(magic_minutes)
                  cmd = 'mutt -s ' + subject_jp + ' ' + mail + ' -a "/home/pi/AIY-projects-python/msg/mminutes2.jpg" < ' +$
                  os.system(cmd)
                  if detect != "ja-JP":
                      aiy.audio.say('Minutes is sent to ' + mail)

              if detect != "ja-JP":
                  aiy.audio.say('See you again!')
              pixel_ring.off()
              break

            time.sleep(0.2)
            pixel_ring.off()
            #print(convs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mail', nargs='?', dest='mail', type=str, default='', help='send to email')
    parser.add_argument('--detect', nargs='?', dest='detect', type=str, default='ja-JP', help='detect lang')
    parser.add_argument('--trans', nargs='?', dest='trans', type=str, default='', help='trans lang')
    args  = parser.parse_args()
    mail  = args.mail if args.mail else ""
    detect= args.detect if args.detect else default_speech
    trans = args.trans  if args.trans else  default_trans
    main() #args.mail, detect, args.trans)
