from class_SrGui import *

wordsReceive, wordsSend = Pipe()
languageReceive, languageSend = Pipe()   
hmmReceived, hmmSend = Pipe()
lmReceived, lmSend = Pipe()
dictionaryReceived, dictionarySend = Pipe()

srStart = Event()
srFinished = Event()
e_start_sr = Event()   
e_end_sr = Event()
closeSR_E = Event()
onlineSR_E = Event()
offlineSR_E = Event()
LMRunning_E = Event()

def main():
    processGUI = Process(target = SrGui, args = (wordsReceive, e_start_sr, e_end_sr, languageReceive, languageSend, srFinished, srStart, hmmSend, lmSend, dictionarySend, closeSR_E, onlineSR_E, offlineSR_E, LMRunning_E))   
    processOnlineSR = Process(target = onlineSRecognition, args = (languageReceive, wordsSend, e_start_sr, e_end_sr, closeSR_E))
    processOfflineSR = Process(target = offlineSRecognition, args = (hmmReceived, lmReceived, dictionaryReceived, languageReceive, wordsSend, srStart, srFinished, closeSR_E))
    
    processGUI.start()
    processOnlineSR.start()
    processOfflineSR.start()
    
    processGUI.join()
    
    processOnlineSR.kill()
    processOfflineSR.kill()  
    gc.collect()
    
    exit()    
    
if __name__ == '__main__':
    main()
