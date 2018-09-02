import re
import json
from io import open
emotion_data = json.loads(open('emotion.json','r',encoding='utf8').read())

def get_text(url):
    for data in emotion_data:
        match = re.findall(data['regex'], url)
        if not match:
            continue
        if isinstance(match[0], tuple):
            match = match[0]
        for emotion in data['emotion_list']:
            flag = True
            for i in range(len(match)):
                if emotion['pattern'][i] == '__index__':
                    index = int(match[i]) - 1
                    if index >= len(emotion['text']):
                        return ' ' + url + ' '
                elif emotion['pattern'][i] != match[i]:
                    flag = False
                    break
            if flag:
                return '[' + emotion['text'][index] + ']'
    return ' ' + url + ' '
