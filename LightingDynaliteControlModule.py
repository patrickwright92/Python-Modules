from extronlib.ui import Button
from extronlib.system import Timer
from collections import deque
import json

class DynaliteControlClass:
    Objs = []#List to hold reference to each instance of this class
    CommsContinue = 0
    CommsPacerTimer = None
    Device          = None
    SysInitialised  = 0 # Used to hold off lighting comms until system is fully booted
    
    
    def __init__(self):
        self.DeviceName               = 'Lights'
        self.RoomId                   = 0#Default Rm1Id
        self.lstdvTps                 = [None]
        self.BaseBtnId                = 6100
        self.lstAutoLightsBtnIds      = [98,99]      
        self.lstPstBtnStates          = [0,1]#Button States for eBus Plates are 0 = off 1= dim 2 = white 4 = red
        self.lstAutoLightsBtns        = []
        
        self.dictPstBtnIdParams       = {
                                         1:{'PstNum':1,'PstCmds':[]},
                                         2:{'PstNum':2,'PstCmds':[]},
                                         3:{'PstNum':3,'PstCmds':[]},
                                         4:{'PstNum':4,'PstCmds':[]},  
                                         #'NoBtn1':{'PstNum':5,'PstCmds':[]}, If presets are required that don't use a buttonput NoBtn in the key                              
                                         #'NoBtn2':{'PstNum':6,'PstCmds':[]} If presets are required that don't use a buttonput NoBtn in the key                              
                                        }
        self.LightsOffPst             = 4 #Default Lights Off Preset number
        self.dictPstNumParams         = {}#Reverse lookup of Preset num to Button ID. Popuplated at init
        self.lstLightsPstBtns         = []
        
        self.AutoLightsFlg            = 1 
        self.CurrentPst               = 1    
        self.AutoLightsBrightPst      = 2 
        self.AutoLightsDimPst         = 3      
        self.lstArea                  = [] 
        self.CurrentPst               = 1       
        self.FauxFeedback             = 0       
        self.PstRate                  ='1'      
        self.lstChans                 = []      
        self.ChannelLevel             = 100
        self.ChannelRate              = '1'# Second
        self.lstAisleChans            = []       
        self.lstScreenChans           = []       
        self.DisplaysShowingVideo     = 'No'
        self.Queue                    = deque()
        self.AreaName                 = 'LightsArea'
        self.CheckScreenLightsDelay   = None
        self.PresetChangeCallback     = None#Function to call if information about preset change is desired
        #self.MasterSlaveMode          = None
        self.LocalClientSocket        = None#This IP socket will be available if this system is a client transmitting to the lighting interface on a remote master system
        self.LocalMasterSocket        = None#This IP socket will be available if this system is a Master receiving to the lighting messages from a remote client system
        self.DebugFlg                 = 1
        ##--- Trace Print and Logging ----
        self.MainPrintLog         = None
        self.dictPrintLogCmds     = None
        
        DynaliteControlClass.Objs.append(self)#Create List of instances of this class

    ##--- Trace Print, Logging  and GVE Status ---------------------------------     
    def PrintLog(self,*args):
        if '!!!!' in args[0] or self.DebugFlg: 
            LogString =''
            if self.MainPrintLog != None:
                for arg in args:
                    LogString = LogString+'{0}'.format(arg)
                if self.DebugFlg =='LogAll' or (self.DebugFlg =='LogConn' and '!!!!' in args[0]):
                    LogString = LogString+',>>Log'
                self.MainPrintLog(LogString)
            else:
                print(*args)


    def CreateButtons(self):
        if self.MainInitListFunc:
            self.MainInitListFunc(type(self).Initialise)

        if self.BaseBtnId:
            lstNewKeys = []
            for OffsetNum in self.dictPstBtnIdParams:
                if isinstance(OffsetNum,int):#Check if this is an integer button ID and hence not one of 'NoBtn?' keys
                    lstNewKeys = lstNewKeys+[OffsetNum+self.BaseBtnId]
            if lstNewKeys:
                for key in lstNewKeys:
                    if isinstance(key,int):#Check if this is an integer button ID and hence not one of 'NoBtn?' keys
                        self.dictPstBtnIdParams[key] = self.dictPstBtnIdParams.pop(key-self.BaseBtnId)
            if len(self.lstAutoLightsBtnIds):
                for Idx in range(len(self.lstAutoLightsBtnIds)):
                    self.lstAutoLightsBtnIds[Idx] = self.lstAutoLightsBtnIds[Idx]+self.BaseBtnId
                    
        for BtnId in self.dictPstBtnIdParams:
            key = self.dictPstBtnIdParams[BtnId]['PstNum']
            self.dictPstNumParams[key] = {}
            if isinstance(BtnId,int):            
                self.dictPstNumParams[key]['BtnId']  = BtnId
                self.dictPstNumParams[key]['PstCmds'] = self.dictPstBtnIdParams[BtnId]['PstCmds']
            else:
                self.dictPstNumParams[key] = None
                
        
        if self.lstdvTps:
            for dvTp in self.lstdvTps:
                if dvTp != None:
                    for BtnId in self.dictPstBtnIdParams:
                        if isinstance(BtnId,int):#Check if this is an integer button ID and hence not one of 'NoBtn?' keys
                            self.lstLightsPstBtns = self.lstLightsPstBtns+([Button(dvTp,BtnId)])
                    if len(self.lstAutoLightsBtnIds):
                        self.lstAutoLightsBtns = self.lstAutoLightsBtns+([Button(dvTp,ID) for ID in self.lstAutoLightsBtnIds])
                    if self.NameBtnId      != None:
                        self.lstNameBtns    = self.lstCommsStatBtns+[Button(dvTp,self.NameBtnId)]
                        #self.PrintLog('self.NameBtnId = ',self.NameBtnId)
                    if self.CommsStatBtnId != None:
                        #self.PrintLog('self.CommsStatBtnId = ',self.CommsStatBtnId)
                        self.lstCommsStatBtns = self.lstCommsStatBtns+([Button(dvTp,self.CommsStatBtnId)])
            
            if self.lstLightsPstBtns:
                for button in self.lstLightsPstBtns: #button events must be created for each touch panel controlling this list of lighting areas
                    button.Pressed  = self.PstBtnEvents
            if self.lstAutoLightsBtns:
                for button in self.lstAutoLightsBtns: #button events must be created for each touch panel controlling this list of lighting areas
                    button.Pressed  = self.SetAutoLightsFlagBtnEvents


    @classmethod   
    def Initialise(cls):
        for Obj in cls.Objs:
            Obj.CheckScreenLightsDelay   = Timer(0.3,Obj.CheckScreenLightConditions)
            if Obj.dictPrintLogCmds:
                Obj.PrintLog('{},Adding module to PrintLog external commands dictionary,!!!!'.format(Obj.DeviceName))
                Obj.PrintLog('{},LocalClientSocket ={}****************'.format(Obj.DeviceName,Obj.LocalClientSocket))
                Obj.dictPrintLogCmds[Obj.DeviceName] = Obj
            Obj.PrintLog('{},Initialise Modules,!!!!'.format(Obj.DeviceName))
        if cls.Device:#The lighting comms device may not exist if this control system is communicating with another where the lighting interface is connected
            cls.Device.SubscribeStatus('PresetStatus',None, DynaliteControlClass.LightsPresetStatus)
        cls.CreateCommsPacerTimer()

    @classmethod
    def CommsPacer(cls,timer,count): #Ticker for pacing comms to devices
        #print('{},CommsPacer count = {}'.format('DynaliteControlClass',count))
        CommsContinue = 0
        for Obj in cls.Objs:
            if len(Obj.Queue):
                if cls.SysInitialised: # Used to hold off lighting comms until system is fully booted
                    CommsContinue = 1
                    LightsMsg = Obj.Queue.popleft()
                    if cls.Device:#The lighting comms device may not exist if this control system is communicating with another where the lighting interface is connected
                        cls.Device.Set(LightsMsg[0],LightsMsg[1],LightsMsg[2])
                    break #Only one dynalite command can be sent per CommsPacer period       
                else:         
                    Obj.Queue.clear()                
        if CommsContinue == 0:
            DynaliteControlClass.CommsPacerTimer.Stop()
            
    @classmethod
    def CreateCommsPacerTimer(cls):
        #print('######################Creating DynaliteControlClass.CommsPacerTimer')
        DynaliteControlClass.CommsPacerTimer = Timer(0.1,DynaliteControlClass.CommsPacer)
                    
    @classmethod
    def CommsPacerTimerRestart(cls):
        #print('!!!!!!!!!!!!!!!!!!!!!!RESTARTING DynaliteControlClass.CommsPacerTimer')
        if DynaliteControlClass.CommsPacerTimer.Count<1:#This starts the CommsPacer if it was stopped
            #print('!!!!!!!!!!!!!!!!!!!!!!Doing It')
            DynaliteControlClass.CommsPacerTimer.Restart()


    @classmethod
    def LightsPresetStatus(cls,command,value,qualifier):
        #cls.Objs[0].PrintLog('{},DynalitePresetStatus command = {}'.format(cls.Objs[0].DeviceName,command))
        #cls.Objs[0].PrintLog('{},DynalitePresetStatus value = {}'.format(cls.Objs[0].DeviceName,value))
        #cls.Objs[0].PrintLog('{},DynalitePresetStatus qualifier = {}'.format(cls.Objs[0].DeviceName,qualifier))
        for Obj in cls.Objs:
            Obj.DoBtnStatus(command,value,qualifier)
    



    def QueueLightsChannelMsg(self,lstArea=[],lstChannels =[],Level=100,Rate='1'):
        if DynaliteControlClass.SysInitialised:
            if self.LocalClientSocket:
                dictArgs ={'lstArea':lstArea,'lstChannels':lstChannels,'Level':Level,'Rate':Rate}
                self.LocalClientSocket.Send(json.dumps(dictArgs))
            else:    
                if Rate == '1':
                    suffix = ' second'
                else:
                    suffix = ' seconds'
                for Area in lstArea:
                    for Channel in lstChannels:
                        self.PrintLog('{},{} LinearChannel msg-{}'.format(self.DeviceName,self.AreaName,{'Area':Area,'Channel':Channel,'Channel Level':Level,'Fade Time':Rate+suffix}))
                        self.Queue.append(('LinearChannel',None,{'Area':Area,'Channel':Channel,'Channel Level':Level,'Fade Time':Rate+suffix}))
        else:
            self.PrintLog('{},Comms not available until cls.SysInitialised is set'.format(self.DeviceName))
        
    def QueueLightsPresetMsg(self,lstArea=[],Preset=1,Rate='1'):
        if DynaliteControlClass.SysInitialised:
            if self.LocalClientSocket:
                #print('self.LocalClientSocket = {}'.format(self.LocalClientSocket))
                dictArgs ={'lstArea':lstArea,'Preset':Preset,'Rate':Rate}
                self.LocalClientSocket.Send(json.dumps(dictArgs))
            else:    
                self.Queue.clear()
                if Rate == '1':
                    suffix = ' second'
                else:
                    suffix = ' seconds'
                for Area in lstArea:
                    self.PrintLog('{},{}ClassicPreset msg-{}'.format(self.DeviceName,self.AreaName,{'Area':Area,'Preset':'Preset {0}'.format(Preset),'Fade Time':Rate+suffix}))
                    self.Queue.append(('ClassicPreset',None,{'Area':Area,'Preset':'Preset {0}'.format(Preset),'Fade Time':Rate+suffix}))
        else:
            self.PrintLog('{},Comms not available until cls.SysInitialised is set'.format(self.DeviceName))


    def AddToQueueLightsChannelMsg(self,dictArgs):
        self.QueueLightsChannelMsg(dictArgs['lstArea'],dictArgs['lstChannels'],dictArgs['Level'],dictArgs['Rate'])
        DynaliteControlClass.CommsPacerTimerRestart()


    def AddToQueueLightsPresetMsg(self,dictArgs):
        #print('Received request - AddToQueueLightsPresetMsg with Args {}'.format(dictArgs))
        self.QueueLightsPresetMsg(dictArgs['lstArea'],dictArgs['Preset'],dictArgs['Rate'])
        DynaliteControlClass.CommsPacerTimerRestart()




    def SetAutoLightsFlag(self,state):
        self.AutoLightsFlg = state
        if self.lstAutoLightsBtns:
            for button in self.lstAutoLightsBtns:
                if button.ID == self.lstAutoLightsBtnIds[0]:#for all Auto Lights Off buttons
                    button.SetState(not self.AutoLightsFlg) #set the opposite state of self.AutoLightsFlg
                elif button.ID == self.lstAutoLightsBtnIds[1]:#for all Auto Lights On buttons
                    button.SetState(self.AutoLightsFlg)       #set the state of self.AutoLightsFlg
        
    def SetAutoLightsFlagBtnEvents(self,button, state):
        self.AutoLightsFlg = self.lstAutoLightsBtnIds.index(button.ID)
        self.SetAutoLightsFlag(self.AutoLightsFlg)

    def DoAutoLights(self,AutoLightsPst):
        if self.AutoLightsFlg:
            if self.CurrentPst != AutoLightsPst:
                self.QueueLightsPresetMsg(self.lstArea,AutoLightsPst,self.PstRate)
                DynaliteControlClass.CommsPacerTimer.Restart()
            if self.FauxFeedback:
                self.CurrentPst = AutoLightsPst
                PstIdx = self.lstPst.index(self.CurrentPst)
                BtnId  = self.lstPstBtnIds[PstIdx]
                for button in self.lstLightsPstBtns:
                    if button.ID == BtnId:
                        button.SetState(1)
                    else:
                        button.SetState(0)


    def CheckScreenLightConditions(self,timer,count):
        if (self.CurrentPst == self.lstPst[0] or self.CurrentPst == self.lstPst[1]):
            if self.DisplaysShowingVideo == 'Yes':
                self.QueueLightsChannelMsg(self.lstArea,self.lstScreenChans,Level=0,Rate='0')
            elif self.DisplaysShowingVideo == 'No': 
                self.QueueLightsPresetMsg(self.lstArea,self.CurrentPst,self.PstRate) 
            DynaliteControlClass.CommsPacerTimer.Restart()
        self.CheckScreenLightsDelay.Stop()                

    def CheckScreenLights(self):
        if len(self.lstScreenChans):
            try:
                self.CheckScreenLightsDelay.Restart()
                self.PrintLog('{}, CheckScreenLightsDelay Timer already created'.format(self.DeviceName))
            except:
                self.PrintLog('{}, CheckScreenLightsDelay TIMER NOT CREATED'.format(self.DeviceName))
                         
    
    def RecallPst(self,prmPst):
        if DynaliteControlClass.CommsPacerTimer:
            self.CurrentPst = prmPst
            self.QueueLightsPresetMsg(self.lstArea,self.CurrentPst,self.PstRate)
            if self.DisplaysShowingVideo == 'Yes':
                self.CheckScreenLights()
            DynaliteControlClass.CommsPacerTimer.Restart()
            if self.FauxFeedback:
                PstIdx = self.lstPst.index(self.CurrentPst)
                BtnId  = self.lstPstBtnIds[PstIdx]
                for button in self.lstLightsPstBtns:
                    if button.ID == BtnId:
                        button.SetState(1)
                    else:
                        button.SetState(0)



    def PstBtnEvents(self,button, state):
        PresetIdx = self.lstPstBtnIds.index(button.ID)
        self.CurrentPst = self.lstPst[PresetIdx]
        self.RecallPst(self.CurrentPst)


    def AisleLightsOn(self,Level=100,Rate='0'):
        if self.lstAisleChans and DynaliteControlClass.CommsPacerTimer:
            self.QueueLightsChannelMsg(self.lstArea,self.lstAisleChans,Level,Rate)
            DynaliteControlClass.CommsPacerTimer.Restart()

    def AisleLightsOff(self,Level=0,Rate='0'):
        if self.lstAisleChans and DynaliteControlClass.CommsPacerTimer:
            self.QueueLightsChannelMsg(self.lstArea,self.lstAisleChans,Level,Rate)
            DynaliteControlClass.CommsPacerTimer.Restart()

    def ScreenLightsOff(self,Level=0,Rate='0'):
        if self.lstScreenChans and DynaliteControlClass.CommsPacerTimer:
            self.QueueLightsChannelMsg(self.lstArea,self.lstScreenChans,Level,Rate)
            DynaliteControlClass.CommsPacerTimer.Restart()


    def DoBtnStatus(self,command,value,qualifier):
        if qualifier['Area'] == self.lstArea[0]:
            self.PrintLog('{},Lights Area =  {}'.format(self.DeviceName,self.AreaName))
            if 'Off' in value:
                self.PrintLog('{},Lights are off in  {}'.format(self.DeviceName,self.AreaName))
                self.CurrentPst = self.lstPst[3]
            else:
                self.CurrentPst = int(value.strip('Preset '))
            if self.CurrentPst in self.lstPst:
                PstIdx = self.lstPst.index(self.CurrentPst)
                BtnId  = self.lstPstBtnIds[PstIdx]
                for button in self.lstLightsPstBtns:
                    if button.ID == BtnId:
                        button.SetState(1)
                    else:
                        button.SetState(0)
            else:
                self.PrintLog('{},Preset not used in control system  {}'.format(self.DeviceName,self.AreaName))
                for button in self.lstLightsPstBtns:
                    button.SetState(0)
            if self.PresetChangeCallback:
                self.PresetChangeCallback(qualifier['Area'],'{}'.format(self.CurrentPst))
        self.PrintLog('{},{} CurrentPst = {}'.format(self.DeviceName,self.AreaName,self.CurrentPst))
            
            
    def ClearButtonStatus(self):            
        for button in self.lstLightsPstBtns:
            button.SetState(0)
        