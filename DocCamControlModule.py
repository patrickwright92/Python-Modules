from extronlib.ui import Button
from extronlib.system import ProgramLog, Timer

class DocCamControlClass:
    Objs = []#List to hold reference to each instance of this class
    
    def __init__(self):
        self.Device             = None     
        self.ConnectionType     = 'IP'     
        self.IpConnectionState  = 'Disconnected'
        self.DevIdQualifier     = None     
        self.DeviceName         = 'DocCam'     
        self.RoomId             = 0#Default Rm1Id
        self.AspectCtrl         = 1       #Elmo serial control does not support Aspect Ratio so clear this flag
        self.AutoFocusCtrl      = 1       #For cameras that do not support AutoFocusOn/Off so clear this flag
        self.lstdvTps           = None   #List of touchpanels with staus buttons present
        self.NameBtnId          = None
        self.lstNameBtns        = []        
        self.CommsStatBtnId     = None
        self.lstCommsStatBtns   = []   #Button used to show comms status online/offline    
        self.PwrFlg             = 0       
        self.BaseBtnId          = 9100
        self.PwrOffBtnId        = 1 
        self.lstPwrOffBtns      = [] 
        self.PwrOnBtnId         = 2 
        self.lstPwrOnBtns       = [] 
        self.lstPwrCtrlBtns     = [] 
        self.LightOffBtnId      = 3 
        self.lstLightOffBtns    = [] 
        self.LightOnBtnId       = 4 
        self.lstLightOnBtns     = [] 
        self.lstLightCtrlBtns   = []
        self.AspectRatio        = '16:9' 
        self.Aspect16_9BtnId    = 5 
        self.lstAspect16_9Btns  = [] 
        self.Aspect4_3BtnId     = 6 
        self.lstAspect4_3Btns   = [] 
        self.lstAspectBtns      = [] 
        self.lstZoomCmds        = ['Tele','Wide']
        self.lstZoomBtnIds      = [7,8]
        self.lstZoomBtns        = []
        self.AutoFocusBtnId     = 9 
        self.PstStoreBtnId      = 10
        self.lstPstStoreBtns    = []
        self.lstPstBtnIds       = [11,12,13]
        self.lstPstBtns         = []
        self.lstAutoFocusBtns    = [] 
        self.ManualFocusBtnId   = 14 
        self.lstManualFocusBtns  = [] 
        self.lstAllManualAutoFocusBtns  = [] 
        self.FocusSpeedDefault  = '1'
        self.CurrentFocusSpeed  = 'Stop'
        self.lstFocusCmds       = ['Far','Near']
        self.lstFocusBtnIds     = [15,16]
        self.lstFocusBtns       = []
        self.ZoomSpeedDefault   = '4'
        self.CurrentZoomSpeed   = 'Stop'
        self.PwrUpdate          = 1      
        self.PollCount          = 0
        self.GveServer          = None
        self.ConnectionStatus   = '?'
        self.WriteToProgLog     = True
        self.DebugFlg           = 1
        ##--- Trace Print and Logging ----
        self.MainPrintLog            = None
        self.dictPrintLogCmds        = None
        ##--- Polling ---
        self.PollingDivisor        = 2#the frequency of the main polling timer will be divided by this number
        self.PollingFunc           = None
        self.InhibitModulePolling  = False
        self.PollingTimer          = Timer(0.5,self.DoModulePoll)
        self.PollingTimer.Stop()

        ##--- Init Function ---
        self.MainInitListFunc      = None

        DocCamControlClass.Objs.append(self)#Create List of instances of this class

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
 
    def SendGveConnectionStatus(self):
        if self.ConnectionStatus != self.Device.ReadStatus('ConnectionStatus'):  
            self.ConnectionStatus = self.Device.ReadStatus('ConnectionStatus')   
            if self.ConnectionStatus == 'Connected':
                VisualAlert = '++++'
                StatusLevel = 'info'
            else:
                if self.Device.Unidirectional == 'False':
                    VisualAlert = '-!!!!'
                    StatusLevel = 'error'
                else:
                    VisualAlert = '**** NONE Unidirectional comms'
                    StatusLevel = 'info'
                    
            if self.ConnectionType == 'IP': 
                self.PrintLog('{}-{}:{}, Connection Status = {}{}'.format(self.DeviceName,self.Device.Hostname,self.Device.IPPort,self.ConnectionStatus,VisualAlert))
            else:
                self.PrintLog('{}, Connection Status = {}{}'.format(self.DeviceName,self.ConnectionStatus,VisualAlert))
            if self.WriteToProgLog:
                if self.ConnectionType == 'IP': 
                    ProgramLog('{}-{}:{}, Connection Status = {}{}'.format(self.DeviceName,self.Device.Hostname,self.Device.IPPort,self.ConnectionStatus,VisualAlert),StatusLevel)
                else:
                    ProgramLog('{}, Connection Status = {}{}'.format(self.DeviceName,self.ConnectionStatus,VisualAlert),StatusLevel)

            if self.GveServer != None:  
                if self.ConnectionStatus == 'Connected': #can't pass self.ConnectionStatus directly to GVE as it can have a value of None if it has never connected
                    self.GveServer.SendStatus(self.DeviceName, 'Connection', 'Connected')
                    self.PrintLog('{},GveServer Connection Status  = Connected{}'.format(self.DeviceName,VisualAlert))                                
                else: 
                    self.GveServer.SendStatus(self.DeviceName, 'Connection', 'Disconnected')
                    if self.ConnectionStatus == None:
                        self.PrintLog('{},Connection Status is None GveServer Connection Status = Disconnected{}'.format(self.DeviceName,VisualAlert))                                
                    elif self.ConnectionStatus == 'Disconnected':
                        self.PrintLog('{},Connection Status is Disconnected GveServer Connection Status = Disconnected{}'.format(self.DeviceName,VisualAlert))                                
 
    
    def DoMutexBtnStatus(self,lstOfBtns,lsBtnIdsToSetOn):#Note second parameter lsBtnIdsToSetOn is a list in case there are multiple buttons that need to track the same status
        for button in lstOfBtns:
            if button.ID in lsBtnIdsToSetOn:
                button.SetState(1)
            else:
                button.SetState(0)
                
                
        ##--- Doc Cam Pwr on/Off buttons ---------------------
    def PwrOnBtnEvents(self,button,state):
        if state == 'Pressed':
            self.On()
            
    def PwrOffBtnEvents(self,button,state):
        if state == 'Pressed':
            self.Off()
    
        ##--- Doc Cam Aspect Ratio buttons ---------------------
    def Set16_9BtnEvents(self,button,state):
        if state == 'Pressed':
            self.AspectRatio16_9()
            
    def Set4_3BtnEvents(self,button,state):
        if state == 'Pressed':
            self.AspectRatio4_3()
          
        ##--- Doc Cam Light on/Off buttons ---------------------
    def LightOnBtnEvents(self,button,state):
        if state == 'Pressed':
            self.DoLightOn()
            
    def LightOffBtnEvents(self,button,state):
        if state == 'Pressed':
            self.DoLightOff()
          
    
    def CreateButtonCode(self):
        if self.MainInitListFunc:
            self.MainInitListFunc(type(self).Initialise)
            
        if self.BaseBtnId:
            if self.PwrOffBtnId:
                self.PwrOffBtnId  = self.PwrOffBtnId+self.BaseBtnId
            if self.PwrOnBtnId:
                self.PwrOnBtnId  = self.PwrOnBtnId+self.BaseBtnId
            if self.LightOnBtnId:
                self.LightOnBtnId  = self.LightOnBtnId+self.BaseBtnId 
            if self.LightOffBtnId:
                self.LightOffBtnId  = self.LightOffBtnId+self.BaseBtnId 
            if self.Aspect16_9BtnId:
                self.Aspect16_9BtnId  = self.Aspect16_9BtnId+self.BaseBtnId 
            if self.Aspect4_3BtnId:
                self.Aspect4_3BtnId  = self.Aspect4_3BtnId+self.BaseBtnId 
            if self.AutoFocusBtnId:
                self.AutoFocusBtnId = self.AutoFocusBtnId+self.BaseBtnId
            if self.ManualFocusBtnId:
                self.ManualFocusBtnId = self.ManualFocusBtnId+self.BaseBtnId
            if len(self.lstFocusBtnIds):
                for idx in range(len(self.lstFocusBtnIds)):
                    self.lstFocusBtnIds[idx] = self.lstFocusBtnIds[idx]+self.BaseBtnId
            if len(self.lstZoomBtnIds):
                for idx in range(len(self.lstZoomBtnIds)):
                    self.lstZoomBtnIds[idx] = self.lstZoomBtnIds[idx]+self.BaseBtnId
            if self.PstStoreBtnId:
                self.PstStoreBtnId = self.PstStoreBtnId+self.BaseBtnId
            if len(self.lstPstBtnIds):
                for idx in range(len(self.lstPstBtnIds)):
                    self.lstPstBtnIds[idx] = self.lstPstBtnIds[idx]+self.BaseBtnId


        if self.lstdvTps:
            for dvTp in self.lstdvTps:
                if dvTp != None:
                    if self.NameBtnId:
                        self.lstNameBtns    = self.lstNameBtns+([Button(dvTp,self.NameBtnId)])
                    if self.CommsStatBtnId:
                        self.lstCommsStatBtns = self.lstCommsStatBtns+([Button(dvTp,self.CommsStatBtnId)])
                    if self.PwrOffBtnId:
                        self.lstPwrOffBtns = self.lstPwrOffBtns+([Button(dvTp,self.PwrOffBtnId)])
                    if self.PwrOnBtnId:
                        self.lstPwrOnBtns = self.lstPwrOnBtns+([Button(dvTp,self.PwrOnBtnId)])
                    if self.LightOnBtnId:
                        self.lstLightOnBtns = self.lstLightOnBtns+([Button(dvTp,self.LightOnBtnId)])
                    if self.LightOffBtnId:
                        self.lstLightOffBtns = self.lstLightOffBtns+([Button(dvTp,self.LightOffBtnId)])
                    if self.Aspect16_9BtnId:
                        self.lstAspect16_9Btns = self.lstAspect16_9Btns+([Button(dvTp,self.Aspect16_9BtnId)])
                    if self.Aspect4_3BtnId:
                        self.lstAspect4_3Btns = self.lstAspect4_3Btns+([Button(dvTp,self.Aspect4_3BtnId)])
                    if self.AutoFocusBtnId:
                        self.lstAutoFocusBtns = self.lstAutoFocusBtns+([Button(dvTp,self.AutoFocusBtnId)])
                    if self.ManualFocusBtnId:
                        self.lstManualFocusBtns = self.lstManualFocusBtns+([Button(dvTp,self.ManualFocusBtnId)])
                    if len(self.lstFocusBtnIds):
                        self.lstFocusBtns = self.lstFocusBtns+([Button(dvTp,ID) for ID in self.lstFocusBtnIds])
                    if len(self.lstZoomBtnIds):
                        self.lstZoomBtns = self.lstZoomBtns+([Button(dvTp,ID) for ID in self.lstZoomBtnIds])
                    if self.PstStoreBtnId:
                        self.lstPstStoreBtns = self.lstPstStoreBtns+([Button(dvTp,self.PstStoreBtnId)])
                    if len(self.lstPstBtnIds):
                        self.lstPstBtns = self.lstPstBtns+([Button(dvTp,ID) for ID in self.lstPstBtnIds])
            if self.lstPwrOffBtns  != None:
                for button in self.lstPwrOffBtns:
                    button.Pressed  = self.PwrOffBtnEvents
            if self.lstPwrOnBtns  != None:
                for button in self.lstPwrOnBtns:
                    button.Pressed  = self.PwrOnBtnEvents
            if self.lstLightOnBtns:
                for button in self.lstLightOnBtns: 
                    button.Pressed  = self.LightOnBtnEvents
            if self.lstLightOffBtns:
                for button in self.lstLightOffBtns:
                    button.Pressed  = self.LightOffBtnEvents
            if self.lstAspect16_9Btns  != None:
                for button in self.lstAspect16_9Btns: 
                    button.Pressed  = self.Set16_9BtnEvents
            if self.lstAspect4_3Btns  != None:
                for button in self.lstAspect4_3Btns:
                    button.Pressed  = self.Set4_3BtnEvents
            if self.lstAutoFocusBtns  != None:
                for button in self.lstAutoFocusBtns:
                    button.Pressed  = self.SetAutoFocusBtnEvents
            if self.lstManualFocusBtns  != None:
                for button in self.lstManualFocusBtns:
                    button.Pressed  = self.SetManualFocusBtnEvents
            if self.lstZoomBtns  != None:
                for button in self.lstZoomBtns:
                    button.Pressed  = self.ZoomBtnHandler
                    button.Released = self.ZoomBtnHandler
            if self.lstFocusBtns  != None:
                for button in self.lstFocusBtns:
                    button.Pressed  = self.FocusBtnHandler
                    button.Released = self.FocusBtnHandler
            if self.lstPstStoreBtns  != None:
                for button in self.lstPstStoreBtns:
                    button.Pressed  = self.PstStoreBtnHandler
            if self.lstPstBtns  != None:
                for button in self.lstPstBtns:
                    button.Pressed  = self.PstBtnHandler



        self.lstPwrCtrlBtns   = self.lstPwrOnBtns+self.lstPwrOffBtns
        self.lstLightCtrlBtns = self.lstLightOnBtns+self.lstLightOffBtns
        self.lstAspectBtns    = self.lstAspect16_9Btns+self.lstAspect4_3Btns
        self.lstAllManualAutoFocusBtns = self.lstManualFocusBtns+self.lstAutoFocusBtns
        
        self.CreateConnectionStatusHandler()
   
    
    
    @classmethod   
    def Initialise(cls):
        for Obj in cls.Objs:
            if Obj.dictPrintLogCmds:
                Obj.PrintLog('{},Adding module to PrintLog external commands dictionary,!!!!'.format(Obj.DeviceName))
                Obj.dictPrintLogCmds[Obj.DeviceName] = Obj
            Obj.PrintLog('{},Initialise Modules,!!!!'.format(Obj.DeviceName))
            Obj.PollCount = 0
            Obj.Device.connectionCounter = 3 #set number of unresponded queries to trip offline state- module default is 15. 
            if Obj.ConnectionType == 'IP':
                Obj.Device.Connect(timeout=0.5)
            if Obj.lstNameBtns != None:
                for button in Obj.lstNameBtns:
                    button.SetText(Obj.DeviceName)
            if Obj.PollingFunc:
                Obj.PollingFunc(Obj.CheckStatus,Obj.PollingDivisor)
                Obj.PrintLog('{}, Module using external polling timer'.format(Obj.DeviceName))
            else:
                Obj.PollingTimer.Restart()
                Obj.PrintLog('{}, Module using internal polling timer - Started'.format(Obj.DeviceName))

    @classmethod   
    def AllOn(cls):
        for Obj in cls.Objs:
            Obj.On()
            

    @classmethod   
    def AllOff(cls):
        for Obj in cls.Objs:
            Obj.Off()


    @classmethod
    def AllAspectRatio16_9(cls):
        for Obj in cls.Objs:
            Obj.AspectRatio16_9()


    @classmethod
    def AllAutoFocus(cls):
        for Obj in cls.Objs:
            Obj.SetAutoFocusMode()

    @classmethod   
    def CheckAllStatus(cls):
        for Obj in cls.Objs:
            Obj.CheckStatus()



    def DoModulePoll(self,timer,count):
        if not count % self.PollingDivisor:
            if not self.InhibitModulePolling:
                self.CheckStatus()

    def IpDeviceConnectionStatusHandler(self,interface, state):
        self.IpConnectionState = state
        if self.IpConnectionState == 'Connected':
            self.Device.counter = 0
        elif self.IpConnectionState == 'Disconnected':
        
            self.Device.counter = self.Device.connectionCounter+1 #set counter to max count threshold
            #self.Device.Update('Power',self.DevIdQualifier)#This should increment counter past max count and force status to disconnected
            if self.lstCommsStatBtns:
                if self.lstCommsStatBtns[0].State != 0:
                    for button in self.lstCommsStatBtns:
                        button.SetState(0)

        self.PollCount = 0
        self.PrintLog('{},IpConnectionState = {}'.format(self.DeviceName,self.IpConnectionState))

    def CreateConnectionStatusHandler(self):
        if self.Device != None and self.ConnectionType == 'IP':
            self.Device.Connected    = self.IpDeviceConnectionStatusHandler
            self.Device.Disconnected = self.IpDeviceConnectionStatusHandler

    def On(self):
        self.Device.Set('Power','On',self.DevIdQualifier)
        self.PrintLog('{}, Power On'.format(self.DeviceName))
        self.PollCount = 0
        self.AspectRatio = '16:9'
        self.PwrUpdate = 1
        self.PwrFlg = 1
        if self.lstPwrCtrlBtns:
            self.DoMutexBtnStatus(self.lstPwrCtrlBtns,[self.PwrOnBtnId])

        
    def Off(self):
        self.Device.Set('Power','Off',self.DevIdQualifier)
        self.PrintLog('{}, Power Off'.format(self.DeviceName))
        self.PollCount = 0
        self.PwrUpdate = 1
        self.PwrFlg = 0
        if self.lstPwrCtrlBtns:
            self.DoMutexBtnStatus(self.lstPwrCtrlBtns,[self.PwrOffBtnId])
        if self.lstLightCtrlBtns:
            self.DoMutexBtnStatus(self.lstLightCtrlBtns,[self.LightOffBtnId])
        

    def DoLightOn(self):
        self.Device.Set('Light','On',self.DevIdQualifier)
        self.DoMutexBtnStatus(self.lstLightCtrlBtns,[self.LightOnBtnId])

    def DoLightOff(self):
        self.Device.Set('Light','Off',self.DevIdQualifier)
        self.DoMutexBtnStatus(self.lstLightCtrlBtns,[self.LightOffBtnId])
        
    def AspectRatio16_9(self):
        if self.AspectCtrl and self.PwrFlg and self.Device.ReadStatus('Power',self.DevIdQualifier) == 'On':
            self.Device.Set('AspectRatio','16:9',self.DevIdQualifier)
            self.PrintLog('{},Setting 16:9 mode'.format(self.DeviceName))
            if self.lstAspectBtns:
                self.DoMutexBtnStatus(self.lstAspectBtns,[self.Aspect16_9BtnId])
        self.PollCount = 0
        self.AspectRatio = '16:9'
   
        
    def AspectRatio4_3(self):
        if self.AspectCtrl and self.PwrFlg and self.Device.ReadStatus('Power',self.DevIdQualifier) == 'On':
            self.Device.Set('AspectRatio','4:3',self.DevIdQualifier)
            self.PrintLog('{},Setting 4:3 mode'.format(self.DeviceName))
            if self.lstAspectBtns:
                self.DoMutexBtnStatus(self.lstAspectBtns,[self.Aspect4_3BtnId])
        self.PollCount = 0
        self.AspectRatio = '4:3'

        
    def DoZoom(self,Direction,Speed):
        self.PrintLog('{0},.Set = {1} {2}'.format(self.DeviceName,Direction,Speed,self))
        self.Device.Set('Zoom',Direction,{'Speed':Speed})
        self.PstNumberBtnOff()


    def ZoomBtnHandler(self,button,state):
        BtnIdx = self.lstZoomBtnIds.index(button.ID)
        self.PollCount = 0
        if state == 'Pressed':
            self.CurrentZoomDir = self.lstZoomCmds[BtnIdx]
            self.CurrentZoomSpeed = self.ZoomSpeedDefault
            button.SetState(1)
            self.PstStoreBtnOff()
        elif state == 'Released':
            self.CurrentZoomDir = 'Stop'
            button.SetState(0)
        self.DoZoom(self.CurrentZoomDir,self.CurrentZoomSpeed)


    def DoFocus(self,Direction,Speed):
        self.PrintLog('{0},.Set = {1} {2}'.format(self.DeviceName,Direction,Speed,self))
        self.Device.Set('Focus',Direction,{'Speed':Speed})
        self.PstNumberBtnOff()


    def FocusBtnHandler(self,button,state):
        BtnIdx = self.lstFocusBtnIds.index(button.ID)
        self.PollCount = 0
        if state == 'Pressed':
            self.CurrentFocusDir = self.lstFocusCmds[BtnIdx]
            self.CurrentFocusSpeed = self.FocusSpeedDefault
            button.SetState(1)
            self.PstStoreBtnOff()
        elif state == 'Released':
            self.CurrentFocusDir = 'Stop'
            button.SetState(0)
        self.DoFocus(self.CurrentFocusDir,self.CurrentFocusSpeed)



    def PstStoreBtnOff(self):    
        if self.lstPstStoreBtns:
            for button in self.lstPstStoreBtns:
                button.SetState(0)

    def PstNumberBtnOff(self):    
        if self.lstPstBtns:
            for button in self.lstPstBtns:
                if button.State != 0:
                    button.SetState(0)


    def DoPst(self,intPstNumber):
        #self.PrintLog('{0},len(self.lstPstBtnIds) ={1}'.format(self.DeviceName,len(self.lstPstBtnIds)))
        if intPstNumber <= len(self.lstPstBtnIds) and intPstNumber>0 :
            BtnId = self.lstPstBtnIds[intPstNumber-1]
            #self.PrintLog('{0},Preset BtnId ={1}'.format(self.DeviceName,BtnId))
            if self.lstPstBtns:
                self.DoMutexBtnStatus(self.lstPstBtns,[BtnId])
        Preset = '{0}'.format(intPstNumber)        
        if self.lstPstStoreBtns[0].State == 0:
            Function = 'PresetRecall'
        elif self.lstPstStoreBtns[0].State == 1:
            Function = 'PresetStore'
        self.PrintLog('{0},.Set = {1} {2} {3}'.format(self.DeviceName,Function,Preset,self.DevIdQualifier))
        self.Device.Set(Function,Preset)
        self.PstStoreBtnOff()    

    def PstBtnHandler(self,button,state):
        BtnIdx = self.lstPstBtnIds.index(button.ID)
        self.DoPst(BtnIdx+1)
    
    def PstStoreBtnHandler(self,button,state):
        if self.lstPstStoreBtns:
            if button.State == 1:
                self.PstStoreBtnOff()
            else:
                for button in self.lstPstStoreBtns:
                    button.SetState(1)



    def SetAutoFocusMode(self):
        if self.AutoFocusCtrl and self.PwrFlg and self.Device.ReadStatus('Power',self.DevIdQualifier) == 'On':
            self.Device.Set('AutoFocus','On',self.DevIdQualifier)
            self.PrintLog('{},Setting Auto Focus mode'.format(self.DeviceName))
            if self.lstAllManualAutoFocusBtns:
                self.DoMutexBtnStatus(self.lstAllManualAutoFocusBtns,[self.AutoFocusBtnId])
            if self.lstFocusBtns:
                for button in self.lstFocusBtns:
                    button.SetVisible(False)
        self.PollCount = 0


    def SetAutoFocusBtnEvents(self,button,state):
        if state == 'Pressed':
            self.SetAutoFocusMode()



    def SetManualFocusMode(self):
        if self.AutoFocusCtrl and self.PwrFlg and self.Device.ReadStatus('Power',self.DevIdQualifier) == 'On':
            self.Device.Set('AutoFocus','Off',self.DevIdQualifier)
            self.PrintLog('{},Setting Manual Focus mode'.format(self.DeviceName))
            if self.lstAllManualAutoFocusBtns:
                self.DoMutexBtnStatus(self.lstAllManualAutoFocusBtns,[self.ManualFocusBtnId])
            if self.lstFocusBtns:
                for button in self.lstFocusBtns:
                    button.SetVisible(True)
        self.PollCount = 0


    def SetManualFocusBtnEvents(self,button,state):
        if state == 'Pressed':
            self.SetManualFocusMode()


    def CheckStatus(self):
        self.PollCount += 1
        if self.ConnectionType == 'IP' and self.IpConnectionState != 'Connected':
            if self.PollCount  == 30:
                self.SendGveConnectionStatus()                        
                if self.lstCommsStatBtns:
                    if self.lstCommsStatBtns[0].State != 0:
                        for button in self.lstCommsStatBtns:
                            button.SetState(0)
                self.Device.counter = 0
                self.Device.Disconnect()                
                self.Device.OnDisconnected()                
                self.PrintLog('{},forcing IP disconnect'.format(self.DeviceName))
                self.PrintLog('{},IpConnectionState = {}'.format(self.DeviceName,self.IpConnectionState))
            elif self.PollCount  == 33:
                self.PollCount = 0
                self.Device.counter = 0
                self.PrintLog('{},trying IP connect'.format(self.DeviceName))
                self.Device.Connect(timeout=0.5)
        else:
            if self.PollCount == 2:
                if self.Device.Unidirectional != 'True':
                    self.Device.Update('Power',self.DevIdQualifier)
                    if self.Device.ReadStatus('Power',self.DevIdQualifier) == 'On':
                        if self.AspectCtrl:
                            self.Device.Update('AspectRatio',self.DevIdQualifier)
                        if self.AutoFocusCtrl:
                            self.Device.Update('AutoFocus',self.DevIdQualifier)
            elif self.PollCount == 3:
                if self.AspectCtrl:
                    #self.PrintLog('{},Power Status = {}'.format(self.DeviceName,self.Device.ReadStatus('Power',self.DevIdQualifier)))
                    if self.Device.ReadStatus('AspectRatio',self.DevIdQualifier) == '16:9':
                        #self.PrintLog('{},AspectRatio = {}'.format(self.DeviceName,self.Device.ReadStatus('AspectRatio',self.DevIdQualifier)))
                        if self.lstAspect4_3Btns:
                            for button in self.lstAspect4_3Btns:
                                if button.State  != 0:
                                    button.SetState(0)
                        if self.lstAspect16_9Btns:
                            for button in self.lstAspect16_9Btns:
                                if button.State  != 1:
                                    button.SetState(1)
                    elif self.Device.ReadStatus('AspectRatio',self.DevIdQualifier) == '4:3':
                        #self.PrintLog('{},AspectRatio = {}'.format(self.DeviceName,self.Device.ReadStatus('AspectRatio',self.DevIdQualifier)))
                        if self.lstAspect16_9Btns:
                            for button in self.lstAspect16_9Btns:
                                if button.State  != 0:
                                    button.SetState(0)
                        if self.lstAspect4_3Btns:
                            for button in self.lstAspect4_3Btns:
                                if button.State  != 1:
                                    button.SetState(1)
                if self.AutoFocusCtrl:
                    if self.Device.ReadStatus('AutoFocus',self.DevIdQualifier) == 'On':
                        if self.lstManualFocusBtns:
                            for button in self.lstManualFocusBtns:
                                if button.State  != 0:
                                    button.SetState(0)
                        if self.lstFocusBtns:
                            for button in self.lstFocusBtns:
                                button.SetVisible(False)
                        if self.lstAutoFocusBtns:
                            for button in self.lstAutoFocusBtns:
                                if button.State  != 1:
                                    button.SetState(1)
                    elif self.Device.ReadStatus('AutoFocus',self.DevIdQualifier) == 'Off':
                        if self.lstManualFocusBtns:
                            for button in self.lstManualFocusBtns:
                                if button.State  != 1:
                                    button.SetState(1)
                        if self.lstFocusBtns:
                            for button in self.lstFocusBtns:
                                button.SetVisible(True)
                        if self.lstManualFocusBtns:
                            for button in self.lstAutoFocusBtns:
                                if button.State  != 0:
                                    button.SetState(0)
            elif self.PollCount == 5:
                if self.PwrFlg:
                    if self.Device.ReadStatus('Power',self.DevIdQualifier) == 'On':
                        self.PwrUpdate = 0
                    if self.PwrUpdate:
                        self.Device.Set('Power','On',self.DevIdQualifier)
                        self.PrintLog('{},Power On Request'.format(self.DeviceName))
                        if self.Device.Unidirectional == 'True':
                            self.PwrUpdate=0
                elif self.PwrFlg == 0:
                    if self.Device.ReadStatus('Power',self.DevIdQualifier) == 'Off':                
                        self.PwrUpdate = 0
                    if self.PwrUpdate:
                        self.Device.Set('Power','Off',self.DevIdQualifier)
                        self.PrintLog('{},Power Off Request'.format(self.DeviceName))
                        if self.Device.Unidirectional == 'True':
                            self.PwrUpdate=0
            elif self.PollCount == 9:
                if self.Device.ReadStatus('ConnectionStatus') == 'Connected':
                    if self.lstCommsStatBtns:
                        if self.lstCommsStatBtns[0].State != 1:
                            for button in self.lstCommsStatBtns:
                                button.SetState(1)
                elif self.Device.ReadStatus('ConnectionStatus') == 'Disconnected':
                    if self.lstCommsStatBtns:
                        if self.lstCommsStatBtns[0].State != 0:
                            for button in self.lstCommsStatBtns:
                                button.SetState(0)
                        self.PrintLog('{},is disconnected'.format(self.DeviceName))
                    if self.ConnectionType == 'IP':
                        self.PrintLog('{},forcing IP disconnect'.format(self.DeviceName))
                        self.Device.counter = 0
                        self.Device.Disconnect()  
                self.SendGveConnectionStatus()                        
            elif self.PollCount >= 13:
                self.PollCount = 0


