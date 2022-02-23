from pydub import AudioSegment as ads
from pydub import effects
from pydub import playback as play
import re,eng_to_ipa
from os import listdir
from os.path import isfile, join


syllables = [f[:-4] for f in listdir("./assets/eng/") if isfile(join("./assets/eng/", f))]
syllables.sort(key=len,reverse=True)
symbols = ['<', '>', '/', '\\', '|', '@', '#', '%', '&', '*', '+', '-', '~', '^']


def funnel_up_soft(audio, position=-30, step=5, duration=30, gain_per_step=0.8):
    if len(audio) < duration:
        return audio
    sound = audio[:position]
    for i in range(duration//step):
        sound+= (audio[position+ step*i: position+ step*(i+1)] + gain_per_step*(i+1))
    return sound

def funnel_up_hard(audio, position=-30, step=5, duration=30, gain_per_step=1):
    if len(audio) < duration:
        return audio
    sound = audio[:position]
    for i in range(duration//step):
        sound+= (audio[position+ step*i: position+ step*(i+1)] + gain_per_step*(i+1))
    return sound

def funnel_down_soft(audio, position=-30, step=5, duration=30, gain_per_step=-0.8):
    if len(audio) < duration:
        return audio
    sound = audio[:position]
    for i in range(duration//step):
        sound+= (audio[position+ step*i: position+ step*(i+1)] + gain_per_step*(i+1))
    return sound

def funnel_down_hard(audio, position=-30, step=5, duration=30, gain_per_step=-1):
    if len(audio) < duration:
        return audio
    sound = audio[:position]
    for i in range(duration//step):
        sound+= (audio[position+ step*i: position+ step*(i+1)] + gain_per_step*(i+1))
    return sound

def stress(audio, position=0, initial_gain= 5, duration=50,step=5):
    dec_per_step = initial_gain*step/duration
    sound = ads.empty()
    for i in range(duration//step):
        sound += (audio[position+step*i:position+step*(i+1)]  + initial_gain - dec_per_step*i)
    sound+=audio[position+duration:]
    return sound

def add_overlay(audio1 , audio2, length=30):
    x = len(audio1)
    y = len(audio2)
    if x ==0:
        return audio2.fade_in(20)
    return audio1.fade_out(30).overlay(audio2, position= -length, gain_during_overlay=-6) + funnel_up_soft( (audio2[length: min(50, y-length)] -5 ) , position=0, step=5,duration=min(50, y-length),gain_per_step=0.5 ) + audio2[min(50, y-length):]

def is_acronym(w):
    # for now acronym is word in all capital letters
    if w==w.upper():
        return True
    return False

def pronounce_alphabet(a):
    return funnel_down_soft(ads.from_wav("assets/alphabets/"+a+".wav").fade_in(30))

def pronounce_digit(a):
    return funnel_down_soft(ads.from_wav("assets/digits/"+a+".wav").fade_in(30))

def pronounce_symbol(a):
    return funnel_down_soft(ads.from_wav("assets/digits/"+a+".wav").fade_in(30))

def pronounce_acronym(w):
    w=w.lower()
    audio = ads.empty()
    for i in w:
        audio+=pronounce_alphabet(i)
    return funnel_down_hard(effects.speedup(audio, 1.15))

def pronounce_number(w):
    # for now can pronounce only non negative integers
    audio=ads.empty()
    for i in inttoword(int(w)).split():
        audio+=pronounce_word(i)
        audio+=ads.silent(20)
    return audio
        

def huntoword(x):
	l1= [0,'one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety','hundred']
	l2=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,30,40,50,60,70,80,90,100]
	ptr=len(l2)-1
	ans=""
	if x==0:
		return ""
	while x and ptr>0:
		if x>=l2[ptr]:
			if l2[ptr]==100:
				z=l1[x//l2[ptr]]+" "
			else:
				z=""
			ans=ans+" "+z+l1[ptr]
			x%=l2[ptr]
		ptr-=1
	return(ans+" ")

def inttoword(x):
	ans=""
	l1=["","thousand","million", "billion", "trillion", "quadrillion", "quintillion", "sextillion", "septillion", "octillion", "nonillion", "decillion", "undecillion", "duodecillion", "tredecillion", "quattuordecillion", "quindecillion", "sexdecillion", "septendecillion", "octodecillion", "novemdecillion", "vigintillion"]
	ptr=len(l1)-1
	if x==0:
		return("zero")
	while x :
		if x>=1000**ptr:
			ans+=huntoword(x//1000**ptr)+l1[ptr]
			x%=1000**ptr
		ptr-=1
	return(ans.strip())


def pronounce_word(w):
    audio = ads.empty()
    if len(w) == 1:
        w=w.lower()
        if w.isalpha():
            return pronounce_alphabet(w)
        elif w.isdigit():
            return pronounce_number(int(w))
        elif w in symbols:
            return pronounce_symbol(w)
        else:
            return audio
    else:
        if w.isdigit():
            return pronounce_number(int(w))
        if is_acronym(w):
            return pronounce_acronym(w)
        if w.isalpha():
            ipa = eng_to_ipa.convert(w)
            if ipa[-1]=="*":
                return effects.speedup(pronounce_acronym(w),1.2)
            
            list_of_syllables = re.split('({})'.format("|".join(syllables)), ipa)
            # print(list_of_syllables)
            audio = ads.empty()
            last=ads.empty()
            i=0
            while i<len(list_of_syllables):
                if list_of_syllables[i]=="":
                    i+=1
                    continue
                elif list_of_syllables[i] == ":":
                    audio = funnel_up_hard(audio,-20,5,20,1.5)
                    audio+= ads.silent(10)
                elif list_of_syllables[i] == "ˈ":
                    sound = ads.from_wav("./assets/eng/"+list_of_syllables[i+1]+".wav")
                    # audio+=ads.silent(20)
                    sound = stress(sound,0,10)
                    if len(list_of_syllables[i+1])==1:
                        audio = add_overlay(audio,sound,40)
                    else:
                        audio = add_overlay(audio,sound,20)
                    i+=1
                elif list_of_syllables[i] == "ˌ":
                    sound = ads.from_wav("./assets/eng/"+list_of_syllables[i+1]+".wav")
                    # audio+=ads.silent(20)
                    sound = stress(sound)
                    if len(list_of_syllables[i+1])==1:
                        audio = add_overlay(audio,sound,40)
                    else:
                        audio = add_overlay(audio,sound,20)
                else:
                    sound = ads.from_wav("./assets/eng/"+list_of_syllables[i]+".wav")
                    if len(list_of_syllables[i])==1:
                        audio = add_overlay(audio,sound,40)
                    else:
                        audio = add_overlay(audio,sound,20)
                i+=1
            return funnel_down_soft(audio)


