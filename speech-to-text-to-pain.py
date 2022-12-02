import asyncio
import base64
import json
import os
import pyaudio
import random
import re
import websockets
from dotenv import load_dotenv
 
load_dotenv()

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()
 
# starts recording
stream = p.open(
   format=FORMAT,
   channels=CHANNELS,
   rate=RATE,
   input=True,
   frames_per_buffer=FRAMES_PER_BUFFER
)
 
# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")
INPUT_FILE = os.getenv("INPUT_FILE")
TORTURE_METHOD = os.getenv("METHOD")
BAD_WORDS = os.getenv("WORDS_LIST").split(',')

def delete_random_line():
  all_lines = []
  with open(INPUT_FILE,'r') as input:
    all_lines = input.readlines()
  if (len(all_lines) > 0) :
    removed_lines = sacrifice_line(all_lines, TORTURE_METHOD)
    with open(INPUT_FILE,'w') as output:
      output.write(''.join(removed_lines))

def sacrifice_line(all_lines, method):
  if method == 'RANDOM':
    deleted_line_num = random.randint(0, len(all_lines)-1)
    all_lines.remove(all_lines[deleted_line_num])
  elif method == 'LONGEST':
    max = 0
    line_to_delete = None
    for line in all_lines:
      if len(line) > max:
        max = len(line)
        line_to_delete = line
    all_lines.remove(line_to_delete)
  return all_lines


async def send_receive():
   print(f'Connecting websocket to url ${URL}')
   async with websockets.connect(
       URL,
       extra_headers=(("Authorization", API_KEY),),
       ping_interval=5,
       ping_timeout=20
   ) as _ws:
       await asyncio.sleep(0.1)
       print("Receiving SessionBegins ...")
       session_begins = await _ws.recv()
       print(session_begins)
       print("Sending messages ...")
       async def send():
           while True:
               try:
                   data = stream.read(FRAMES_PER_BUFFER)
                   data = base64.b64encode(data).decode("utf-8")
                   json_data = json.dumps({"audio_data":str(data)})
                   await _ws.send(json_data)
               except websockets.exceptions.ConnectionClosedError as e:
                   print(e)
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"
               await asyncio.sleep(0.01)
          
           return True
      
       async def receive():
           while True:
               try:
                   result_str = await _ws.recv()
                   result = json.loads(result_str)
                   if result['message_type'] == 'FinalTranscript':
                    already_deleted = False
                    line = re.sub(r'[^a-zA-Z0-9 ]', '', result['text'].lower())
                    print(line)
                    for bad_word in BAD_WORDS:
                      if bad_word in line and not already_deleted:
                        delete_random_line()
                        already_deleted = True
               except websockets.exceptions.ConnectionClosedError as e:
                   print(e)
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"
      
       send_result, receive_result = await asyncio.gather(send(), receive())

asyncio.run(send_receive())