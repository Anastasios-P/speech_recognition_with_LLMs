import speech_recognition as sr
from pocketsphinx import LiveSpeech
from multiprocessing import Pipe, Event, Process

def onlineSRecognition(languageReceive, wordsSend, e_start_sr, e_end_sr, closeOfflineSR_E):
    speech = sr.Recognizer()
    global voiceInput
    voiceInput = ""
    
    while True:
        e_start_sr.wait()
        e_start_sr.clear()
        with sr.Microphone() as sound:            
            speech.adjust_for_ambient_noise(sound)
            
            audio = speech.listen(sound)
            try:
                voiceInput = speech.recognize_google(audio, language = languageReceive.recv())
        
            except sr.UnknownValueError:
                print("Unknown Value!", flush=True)
                wordsSend.send("")                 
                e_end_sr.set()
                continue
            except sr.RequestError:
                print("Unknown Value!", flush=True)
                wordsSend.send("")                 
                e_end_sr.set()                
                continue
            except sr.WaitTimeoutError:
                print("Unknown Value!", flush=True)  
                wordsSend.send("")                
                e_end_sr.set()
                continue 
                    
        print(voiceInput, flush = True)
        wordsSend.send(str(voiceInput))
        e_end_sr.set() 
                
            
def offlineSRecognition(hmmReceived, lmReceived, dictionaryReceived, languageReceived, wordsSend, srStart, srFinished, closeOfflineSR_E):
    while(True):
        srStart.wait()
        srStart.clear()
        speech = LiveSpeech(
        hmm = hmmReceived.recv(),
        lm = lmReceived.recv(),
        dic = dictionaryReceived.recv()
        )
        for phrase in speech:
            if(closeOfflineSR_E.is_set()):
                wordsSend.send("")
                srFinished.set()
                break
            print(phrase, flush = True)
            w = str(phrase)
            wordsSend.send(w)
            srFinished.set()
            srStart.wait()
            srStart.clear()
