from string import punctuation
from pydub import AudioSegment as ads
from pydub.playback import play
import word,re

def pronounce_with_punctuations(w):
    if len(w)==0:
        return w
    # for now return without modifying
    # will implement this later
    return w


def say(text):
    punctuations = ['.',',',';',':','?','!']
    text+='.'
    text = re.split('([^a-zA-Z0-9\'])',text)
    output = ads.silent(5)
    last_word=ads.empty()
    for i in text:
        if i.isspace() or i=='':
            output+=last_word
            if len(last_word) != 0:
            	output+=ads.silent(50)
            last_word=ads.empty()
        elif i in punctuations:
            output += pronounce_with_punctuations(last_word)
            last_word=ads.empty()
        else:
            last_word=word.pronounce_word(i)
    
    # output.export("output.wav","wav")
    play(output)
        
