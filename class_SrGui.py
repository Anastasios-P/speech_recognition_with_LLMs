import tkinter as tki
from tkinter import StringVar, END, Scrollbar, Frame, filedialog, simpledialog, IntVar, Checkbutton, Listbox, ttk
import tkinter.scrolledtext as tkiS
from functools import partial
from speechR import *
import os
from multiprocessing import Pipe
import csv
import asyncio
import threading
import gc
import win32gui
    
class SrGui():
    #Fenster1 für die GUI erzeugen
    window1 = tki.Tk()   
    window1.attributes("-alpha", 1.0)   
    window1.daemon = True  
    
    w1x=1920    #x Größe vom Fenster1
    w1y=800     #y Größe vom Fenster1
    
    writtingSize = 15       #Variable für die Schriftgröße des gesprochenen Textes
    
    message = StringVar()   #Variable für die Nachrichten an den Benutzer 
    wordsReceive = ""
    wholeText = ""
    
    newLLM_name = ""
    newLLM_hmm = ""
    newLLM_lm = ""
    newLLM_dic = ""
    
    activeLLM_name = ""
    activeLLM_hmm = ""
    activeLLM_lm = ""
    activeLLM_dic = ""
    
    rel_y = 0.2 
    
    #Variable für das Text Feld (für den gesprochenen Text)
    spokenText = tkiS.ScrolledText(width = int(1150 / writtingSize), height = int(330 / writtingSize), foreground = 'blue')
    spokenText['font'] = ['Comic Sans MS', writtingSize]
    spokenText.pack()
    
    label2=tki.Label(window1, text=message.get()) #Label für die Nachrichten
    label2.pack(side="top")    
        
    def __init__(self, wordsReceive, e_start_sr, e_end_sr, languageReceive, languageSend,srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E, LMRunning_E): 
        LMRunning_E.clear()
        self.window1Handler = self
        #GUI transparency
        self.window1.attributes("-alpha", 0.95)
        
        #Titel vom Fenster1
        self.window1.title("Speech recognition with Language Models")
        
        #Set Fenster1 größe
        self.window1.geometry(str(self.w1x) + "x" + str(self.w1y)) 

        #Nachricht an den Benutzer senden
        self.message.set("Please choose a Language Model..")
        self.label2.configure(text=self.message.get(), font="Bahnschrift")    

        self.LoadLM_flag = False
        self.deleteLM_flag = False 
        self.flag_once_deleteLM = True
        self.flag_once_loadLM = True
        
        #Event variables
        self.onlineSR_E = onlineSR_E
        self.offlineSR_E = offlineSR_E
        self.e_start_sr = e_start_sr
        self.e_end_sr = e_end_sr
        self.srFinished = srFinished
        self.srStart = srStart
        self.closeSR_E = closeSR_E
        self.LMRunning_E = LMRunning_E
        #Pipe variables
        self.hmmSend = hmmSend
        self.lmSend = lmSend
        self.dictionarySend = dictionarySend  
        self.languageReceive = languageReceive
        self.languageSend = languageSend
        self.wordsReceive = wordsReceive 

        #Online LLMs
        #Available languages
        self.languages = {
        "English" : "en-US",
        "Deutsch" : "de-GE",
        "ελληνικά" : "el-GR",
        "Français" : "fr-FR",
        "日本語" : "ja-JP",
        "中國人" : "zh-CN",
        "Русский" : "ru-RU",
        "Español" : "es-ES",
        "Italiano" : "it-IT"
        }
        
        #Label 1 - on the right side of the window
        self.label1 = tki.Label(self.window1, text="Online speech recognition", font=("Bahnschrift", 21)) #Label für die Nachrichten
        self.label1.pack(side = "right") 
        self.label1.place(relx = 0.94, rely = 0.1, anchor = "se")
    
        #Listbox 2 - on the right side of the window
        self.listbox2 = ttk.Combobox(self.window1, values=list(self.languages), state="readonly", font=("Bahnschrift", 21))
        self.listbox2.set("Select a language");
        self.listbox2.pack()
        
        self.listbox2.current(0)
        self.listbox2.bind("<<ComboboxSelected>>", self.chooseLanguage)        
        self.listbox2.pack(side="right")
        self.listbox2.place(relx = 0.94, rely = 0.2, anchor = "se")    

        cmd5=partial(self.closeOfflineSR, closeSR_E) 
        self.B7 = tki.Button(self.window1, text="end online speech recognition", font="Bahnschrift", command=cmd5, padx=21)
        self.B7.pack(side="left")
        self.rel_y += 0.1
        self.B7.place(relx=0.94,rely = 0.5,anchor="se")  
        self.B7.configure(bg = "red")   

        self.listbox1 = tki.Listbox(self.window1, height = 14, width = 35)
        self.listbox1.pack()        
        self.listbox1.place(relx = 0.02, rely = 0.32)                
        self.listbox1.config(font = ("Helvetica", 15, "bold"), cursor = "hand2", selectmode = "multiple")  

        self.csvFile = "LM_list.csv"
        self.List1 = []
        
        #LMs
        cmd=partial(self.addNewLM, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend, srFinished, srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E)
        self.B7 = tki.Button(self.window1, text="Add New LM", font="Bahnschrift", command=cmd, padx=23)
        self.B7.pack(side="right")
        self.B7.place(relx=0.07,rely=0.1,anchor="sw")
        self.B7.configure(bg = "green")
        
        cmd2=partial(self.deleteLM, e_start_sr, e_end_sr, wordsReceive, languageSend,srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E)
        self.B8 = tki.Button(self.window1, text="Delete LM", font="Bahnschrift", command=cmd2, padx=15)
        self.B8.pack(side="right")
        self.B8.place(relx=0.07,rely=0.2,anchor="sw") 
        self.B8.configure(bg = "red")   

        cmd3=partial(self.loadLM, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend, srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E, LMRunning_E)       
        self.B9 = tki.Button(self.window1, text="Load LM", font="Bahnschrift", command=cmd3, padx=15)        
        self.B9.pack(side="right")
        self.B9.place(relx=0.07,rely=0.3,anchor="sw")
        self.B9.configure(bg = "green")            
       
        t2 = threading.Thread(target = asyncio.run, args=[self.updateListAndListbox(0.25, self.csvFile, self.listbox1)], daemon = True) 
        t2.start()   
        
        self.window1.mainloop()  

    def chooseLanguage(self, event):
        self.closeSR_E.set() #first close the running speech recognitions -if there are any running..
        self.onlineSR_E.set()
        self.languageSend.send(self.languages[self.listbox2.get()])
        print("Language chosen.")         
        self.thread1 = threading.Thread(target=asyncio.run, args=[self.startLM()], daemon = True)
        self.thread1.start()       
    
    def label2Receive(self, connection):
        w = str(connection.recv())
        self.window1.words.set(str(connection.recv()))
        print(w, flush = True)
        
    #update label2
    def label2U(self, text):
        self.message.set(text)
        self.label2.configure(text=self.message.get(), font="Bahnschrift")
        self.window1.update()

    #update spokenText
    def showSpokenText(self, text):
        self.wholeText = self.wholeText + text + ". "
        self.spokenText.insert(tki.END, text + ". ")
        self.window1.update()        
        
    def chooseFolder(self, windowTitle):
        folderPath = filedialog.askdirectory( title = windowTitle, initialdir = os.getcwd() )
        
        if folderPath:
            return str(folderPath)
        else:
            return ""

    def chooseFile(self, windowTitle):
        filePath = filedialog.askopenfile( title = windowTitle, initialdir = os.getcwd())
        
        if filePath:
            ret = filePath.name
            filePath.close()
            return str(ret)
        else:
            return ""    

    #start Language Model
    async def startLM(self):
        self.LMRunning_E.set()
        self.closeSR_E.clear()
        if(self.onlineSR_E.is_set()):
            self.onlineSR_E.clear()
            lang = str(self.languageReceive.recv())
            while( True ):
                if(self.closeSR_E.is_set()):
                    self.LMRunning_E.clear()
                    return                
                self.languageSend.send(lang)
                self.e_start_sr.set()
                self.e_end_sr.wait()  
                self.e_end_sr.clear()
                if(self.closeSR_E.is_set()):
                    self.LMRunning_E.clear()
                    return                
                w = self.wordsReceive.recv()
                self.showSpokenText(w)
                self.label2U(w)
        elif(self.offlineSR_E.is_set()):
            self.offlineSR_E.clear()            
            while(True):
                if(self.closeSR_E.is_set()):
                    self.LMRunning_E.clear()
                    return                               
                self.srStart.set()
                self.srFinished.wait() 
                self.srFinished.clear()
                if(self.closeSR_E.is_set()):
                    self.LMRunning_E.clear()
                    return                  
                w = self.wordsReceive.recv()
                self.showSpokenText(w)
                self.label2U(w)
                self.label2.configure(text=self.message.get(), font="Bahnschrift")
                self.window1.update()              

    def addNewLM(self, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend,srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E):  
        self.LoadLM_flag = False
        self.deleteLM_flag = False
        #Open a dialog to ask the new LLM name
        self.newLLM_name = simpledialog.askstring(title = "select new Large Language Model path", prompt = "Please give a name for the new LLM:", parent = self.window1)

        if((self.newLLM_name == "") or (self.newLLM_name == None)):
            return
            
        #open a dialog for asking the folder for the HMM
        hmm = self.chooseFolder("select Hidden Markov Model ordner")
        self.newLLM_hmm = hmm

        if(self.newLLM_hmm == ""): 
            return       
        
        #open a dialog for asking the file for the Language Model
        lm = self.chooseFile("select file for this Large Language Model")
        self.newLLM_lm = lm
        
        if(self.newLLM_lm == ""):           
            return
        
        #open a dialog for asking the file for the dictionary of this LLM
        dictionary = self.chooseFile("select file for the dictionary of this Large Language Model")
        self.newLLM_dic = dictionary
        
        if(self.newLLM_dic == ""):  
            return
        
        if(self.newLLM_dic != ""):
            data = [{'name':self.newLLM_name, 'hmm':self.newLLM_hmm, 'lm':self.newLLM_lm, 'dic':self.newLLM_dic}]
            self.appendConfigFile("LM_list.csv", data)
            
    def deleteLM(self, e_start_sr, e_end_sr, wordsReceive, languageSend,srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E): 
        self.listbox1.selection_clear(0, tki.END) #diselect the previous selection in the listbox1, if there is any.
        self.LoadLM_flag = False
        self.deleteLM_flag = True
        self.listbox1.config(fg = "red", font = "Bahnschrift", selectmode = "multiple")  
        if(self.flag_once_deleteLM == True):
            self.flag_once_deleteLM = False
            t1 = threading.Thread(target = asyncio.run, args=[self.selectItemAndDelete(0.05, self.listbox1, self.csvFile)], daemon = True) 
            t1.start()         
        
        
    def loadLM(self, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend, srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E, LMRunning_E):  
        self.listbox1.selection_clear(0, tki.END) #diselect the previous selection in the listbox1, if there is any.
        self.listbox1.config(fg = "green", font = "Comic", selectmode = "single")  
        self.LoadLM_flag = True
        self.deleteLM_flag = False
        if(self.flag_once_loadLM == True):
            self.flag_once_loadLM = False
            t1 = threading.Thread(target = asyncio.run, args=[self.selectItemFromListbox(0.05, self.csvFile, self.listbox1, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend,srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E, LMRunning_E)], daemon = True) 
            t1.start()         
            
    #start Language Model    
    def LMs(self, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend,srFinished,srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E):               
        pass
        
    def closeOfflineSR(self, closeSR_E):
        closeSR_E.set()
        
    def f2(self, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend, srFinished, srStart,hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E): 
        offlineSR_E.set()
        self.window1Handler.thread6 = threading.Thread(target = asyncio.run, args=[self.startLM()], daemon = True)         
        self.window1Handler.thread6.start()
        
    def createNewFile(self, name):
        try:
            f = open(name, "x", encoding = 'utf-8')
        except FileExistsError:
            pass
        
    def appendConfigFile(self, name, data):
        columns = ['name','hmm','lm','dic']
        with open(name, 'a', newline = '', encoding = 'utf-8') as f:
            write = csv.DictWriter(f, columns)
            if(os.path.getsize(name) == 0):
                write.writeheader()
            write.writerows(data)################### Hier is the problem when i write greek characters as file name ###############################
    
    def firstWriteList1(self, csvFileName):
        list1 = []
        try:
            with open(csvFileName, mode = 'r', encoding = 'utf-8') as file:               
                data = csv.reader(file)
                flagOnce = False
                for rows in data:
                    if(flagOnce == True):#spring the first line...
                        list1.append(rows)
                    else:
                        flagOnce = True
        except FileExistsError: 
            print(list1)
            return list1        
    
    def updateListbox(self, csvFileName, listbox):
        self.list1 = []
        try:
            with open(csvFileName, mode = 'r', encoding = 'utf-8') as file:               
                data = csv.reader(file)
                flagOnce = False
                for rows in data:
                    if(flagOnce == True):#spring the first line...
                        self.list1.append(rows)
                    else:
                        flagOnce = True
        except FileExistsError: 
            print(self.list1)
            return self.list1         
        if(self.list1 != self.List1):
            listbox.delete(0, END)             
            for nn in self.list1: 
                i = 0
                for n in nn:
                    if(i == 0):
                        listbox.insert(END, n)
                        i += 1
        return self.list1                   
        
    async def selectItemFromListbox(self, secondsTimeInterval, csvFileName, listbox, e_start_sr, e_end_sr, wordsReceive, languageReceive, languageSend,srFinished,srStart, hmmSend,lmSend,dictionarySend, closeSR_E, onlineSR_E, offlineSR_E, LMRunning_E): 
        while(True):
           
            await asyncio.sleep(secondsTimeInterval)
            if(self.LoadLM_flag == True): 
                if not(LMRunning_E.is_set()):               
                    element = listbox.curselection()
                    if(len(element) > 0): 
                        hmmSend.send(str(self.List1[element[0]][1]))
                        lmSend.send(str(self.List1[element[0]][2]))
                        dictionarySend.send(str(self.List1[element[0]][3]))

                        offlineSR_E.set() 
                        
                        t = threading.Thread(target = asyncio.run, args=[self.startLM()], daemon = True)         
                        t.start()                                        

    async def updateListAndListbox(self, secondsTimeInterval, csvFileName, listbox):
        while(True):
            await asyncio.sleep(secondsTimeInterval)
            self.List1 = self.updateListbox(csvFileName, listbox)                       
            
    def deleteLinesFromFile(self, fileName, *lineContent):
        with open(fileName, "r+", encoding = 'utf-8') as file:
            data = file.readlines()
            file.seek(0)
            for line in data:
                flag = False
                for singleLine in lineContent:
                    if(line.split(",")[0] == singleLine[0]):
                        flag = True
                        break
                if(flag == False):
                    file.write(line)
            file.truncate()     

    async def selectItemAndDelete(self, secondsTimeInterval, listbox, csvFileName):       
        while(True):
            await asyncio.sleep(secondsTimeInterval)
            if(self.deleteLM_flag == True): ############## Do Event().. not variable                
                elements = listbox.curselection()
                elementList = []
                if(len(elements) > 0):
                    for i in elements:
                        elementList.append(listbox.get(i))
                    for i in elements:                        
                        listbox.delete(i)
                    self.deleteLinesFromFile( csvFileName, elementList )                    
                
    def applyConfigFile(self):
        iniFile = pd.read_csv("config.csv")
        pass
        
    def changeConfigFile(self):
        pass
        
    def createRow(self, **args):
        data = {}
        for i in args:
            data.append(i)
        return data
