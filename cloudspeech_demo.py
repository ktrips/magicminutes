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

RATE = 16000
CHANNELS = 8
KWS_FRAMES = 10     # ms
DOA_FRAMES = 800    # ms

#detector = SnowboyDetect('/home/pi/AIY-projects-python/src/examples/voice/snowboy/resources/common.res','/home/pi/AIY-projects-python/src/examples/voice/snowboy/resources/a$
#detector.SetAudioGain(1)
#detector.SetSensitivity('0.5')
history = collections.deque(maxlen=int(DOA_FRAMES / KWS_FRAMES))

def main():
    recognizer = aiy.cloudspeech.get_recognizer()
    recognizer.expect_phrase('turn off the light')
    recognizer.expect_phrase('turn on the light')
    recognizer.expect_phrase('blink')
    recognizer.expect_phrase('repeat after me')

    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    aiy.audio.get_recorder().start()

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

        bye_words    = ['goodbye', 'good bye', 'see you', 'bye bye']
        progress_words=['completed', 'confirmed', 'delayed', 'finished', 'discussed', 'fixed']
        approve_words= ['agreed', 'approved']
        next_words   = ['next step', 'next Steps', 'next action', 'next actions']
        issue_words  = ['issue', 'issues', 'problem', 'error', 'dificit']
        magic_words  = ['magic minutes', 'magical minutes']

        print('Listening...')
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
            if direction > 90 and direction < 270:
              direct = "Back-side person"
            else:
              direct = "Front person"
            #direct = str(direction)
            print('>> ' + direct + ' said "' + text + '"')
            aiy.audio.say(text)

            keyw = "conv"
            text.lower()
            if 'turn on the light' in text:
                led.set_state(aiy.voicehat.LED.ON)
            elif 'turn off the light' in text:
                led.set_state(aiy.voicehat.LED.OFF)
            elif 'blink' in text:
                led.set_state(aiy.voicehat.LED.BLINK)
            elif 'repeat after me' in text:
                to_repeat = text.replace('repeat after me', '', 1)
                aiy.audio.say(to_repeat)

            #elif 'open Magic minutes' in text: #or 'open Magic minutes' or 'start magic minutes' in text:
                #pixel_ring.spin()
                #aiy.audio.say('Ok, Start recording your conversation!')
                #keyw = "MC"

            for m in magic_words:
              if text.find(m) > -1:
                keyw = "MC"

                pixel_ring.spin()
                aiy.audio.say('Ok, make magic minutes!')
                break
            for a in progress_words:
              if text.find(a) > -1:
                keyw = "progress"
                break
            for a in approve_words:
              if text.find(a) > -1:
                keyw = "approve"
                break
            for a in issue_words:
              if text.find(a) > -1:
                keyw = "issue"
                break
            for n in next_words:
              if text.find(n) > -1:
                keyw = "next"
                break
            for b in bye_words:
              if text.find(b) > -1:
                keyw = "bye"
                break

            conv = {"number": i,
                "person": direct,
                "convt": text,
                "keyw": keyw}
            convs.append(conv)

            if text in bye_words:
                #print(convs)
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

                  conv_org    = ""
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

                  is_are = ["is","was","are","were", "it's", "its"]
                  for con in convs:
                    if con["keyw"] not in ["MC", "MM", "bye"]:
                      conv_org += ' ' + str(con["number"]) + '(' + con["person"] + '): ' + con["convt"] + '\n'
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
                      """for a in issue_words + is_are:
                        issuew = issuew.replace(a, "") """
                      conv_issue += ' - #' + str(issuen) + ': ' + issuew + ' raised by ' + con["person"] + '\n'
                    if con["keyw"] == "next":
                      nextn += 1
                      nextw = con["convt"]
                      """for a in next_words + is_are:
                        nextw = nextw.replace(a, "")"""
                      conv_next += ' - #' + str(nextn) + ': ' + nextw + '\n'

                  minutes = '= Meeting Minutes =\n\n'
                  minutes+= 'RE: Development Status\n'
                  minutes+= 'Date: ' +convDateStr + '\n'
                  minutes+= 'MMinutes by: ' + mail + '\n'
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
                  minutes+= '\n Meeting details: \n'
                  minutes+= conv_org + '\n'
                  minutes+= 'Meeting note is attached:'
                  subject = '"Meeting minutes (' + convDateStr + ')"'
                  print(subject + '\n' + minutes)

                  pixel_ring.spin()

                  os.makedirs(dir_path, exist_ok=True)
                  with open(os.path.join(dir_path, file_name), 'w') as f:
                    f.write(minutes)
                  #cmd = 'echo ' + minutes + ' | mail -s ' + subject + ' ' + mail
                  cmd = 'mutt -s ' + subject + ' ' + mail + ' -a "/home/pi/AIY-projects-python/msg/mminutes2.jpg" < ' + fname
                  os.system(cmd)
                  aiy.audio.say('Minutes is sent to ' + mail)

                aiy.audio.say('See you again!')
                pixel_ring.off()

                break
            time.sleep(0.2)
            pixel_ring.off()
            #print(convs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
   parser.add_argument('--mail', dest='mail', type=str, default='', help='send to email')
    args   = parser.parse_args()
    mail = args.mail if args.mail else ''

    main()
