from string import punctuation
from pydub import AudioSegment as ads
from pydub import effects
from pydub.playback import play
import word,re

def pronounce_with_punctuations(w,i):
    if i=='.':
        return w + ads.silent(500)
    if i==',':
        return word.funnel_down_soft(w) + ads.silent(250)
    if i==';':
        return word.funnel_down_soft(w) + ads.silent(300)
    if i==':':
        return word.funnel_down_soft(w) + ads.silent(300)
    if i=='!':
        return effects.speedup((word.funnel_up_hard(w)+5), 1.15) + ads.silent(400)
    if i=='?':
        return effects.speedup((word.funnel_up_hard(w)+3), 1.1) + ads.silent(400)
    return w


def word_status(w):
    if w.isdigit():
        return 'number'
    if w.isalpha():
        return 'word'
    if w in word.symbols:
        return 'symbol'
    return False

punctuations = ['.',',',';',':','?','!']

def say(text):
    text+='.'
    regexPattern = '|'.join('(?<={})'.format(re.escape(delim)) for delim in punctuations)
    list_of_senntences = re.split(regexPattern,text)
    # print(list_of_senntences)
    output = ads.empty()
    for i in list_of_senntences:
        if(i==''):
            continue
        output+=pronounce_with_punctuations(say_sentence(i[:-1]+' '),i[-1])
    play(output+15)

        
def say_sentence(text):
    # print(text)
    text = re.split('([^a-zA-Z0-9\'])',text)
    output = ads.silent(5)
    last_word=ads.empty()
    for i in text:
        if i.isspace() or i=='':
            output+=last_word
            if len(last_word) != 0:
                output+=ads.silent(60)
            last_word=ads.empty()
        elif word_status(i)!=False:
            output+=last_word
            last_word=word.pronounce_word(i)
        else:
            last_word=word.pronounce_word(i)
    
    # output.export("output.wav","wav")
    # play(output)
    return output
        
