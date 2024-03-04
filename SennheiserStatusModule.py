from extronlib.ui import Button

class SennheiserMicStatusClass:
    Objs = []#List to hold reference to each instance of this class

    def __init__(self):
        self.Device                  = None
        self.DeviceName              = 'RadioMic'
        self.BatteryLevelStatus      = 'Unknown'
        self.FrequencyStatus         = 'Unknown'
        self.SquelchStatus           = 'Unknown'
        self.TxNameStatus            = 'Unknown'
        self.lstdvTps                = []
        self.NameBtnId               = None
        self.lstNameBtns             = []        
        self.CommsStatBtnId          = None
        self.lstCommsStatBtns        = []        
        self.BatteryLevelStatBtnId   = None
        self.lstBatteryLevelStatBtns = []        
        self.FrequencyStatBtnId      = None
        self.lstFrequencyStatBtns    = []        
        self.SquelchStatBtnId        = None
        self.lstSquelchStatBtns      = []       
        self.lstCurrentStatus        = ['?','?','?','?']
        self.PollCount               = 0
        self.GveServer               = None
        self.ConnectionStatus        = '?'
        self.DebugFlg                = 1
        ##--- Trace Print and Logging ----
        self.MainPrintLog            = None
        self.dictPrintLogCmds        = None
        
        SennheiserMicStatusClass.Objs.append(self)#Create List of instances of this class



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
   

        
    def CreateButtonCode(self):

        if self.lstdvTps:
            for dvTp in self.lstdvTps:
                if dvTp != None:
                    if self.NameBtnId             != None:
                        self.lstNameBtns             = [Button(dvTp,self.NameBtnId) for dvTp in self.lstdvTps]
                    if self.CommsStatBtnId        != None:
                        self.lstCommsStatBtns        = [Button(dvTp,self.CommsStatBtnId) for dvTp in self.lstdvTps]
                    if self.BatteryLevelStatBtnId != None:
                        self.lstBatteryLevelStatBtns = [Button(dvTp,self.BatteryLevelStatBtnId) for dvTp in self.lstdvTps]
                    if self.FrequencyStatBtnId    != None:
                        self.lstFrequencyStatBtns    = [Button(dvTp,self.FrequencyStatBtnId) for dvTp in self.lstdvTps]
                    if self.SquelchStatBtnId      != None:
                        self.lstSquelchStatBtns      = [Button(dvTp,self.SquelchStatBtnId) for dvTp in self.lstdvTps]



    @classmethod   
    def InitialiseAllSennheiserMics(cls):
        for Obj in cls.Objs:
            if Obj.dictPrintLogCmds:
                Obj.PrintLog('{},Adding module to PrintLog external commands dictionary,!!!!'.format(Obj.DeviceName))
                Obj.dictPrintLogCmds[Obj.DeviceName] = Obj
            Obj.PrintLog('{},Initialise Modules,!!!!'.format(Obj.DeviceName))
            Obj.PollCount = 0
            Obj.Device.SubscribeStatus('Frequency',None, Obj.FrequencyStatusSub)
            Obj.Device.connectionCounter = 3#set number of unresponded queries to trip offline state- module default is 15. 
            #Obj.Device.Connect(timeout=0.5) #Not for UDP connections
            if Obj.lstNameBtns != None:
                for button in Obj.lstNameBtns:
                    button.SetText(Obj.DeviceName)
            
            Obj.BatteryLevelStatus      = 'Unknown'
            Obj.FrequencyStatus         = 'Unknown'
            Obj.SquelchStatus           = 'Unknown'               
            Obj.TxNameStatus            = 'Unknown'               
            Obj.SetAllStatus()    

                
    @classmethod   
    def CheckAllStatus(cls):
        for Obj in cls.Objs:
            Obj.CheckStatus()


    def SendGveConnectionStatus(self):
        if self.ConnectionStatus != self.Device.ReadStatus('ConnectionStatus'):  
            self.ConnectionStatus = self.Device.ReadStatus('ConnectionStatus')   
            self.PrintLog('{},Connection Status = {},!!!!'.format(self.DeviceName,self.ConnectionStatus))
            if self.GveServer != None:  
                if self.ConnectionStatus == 'Connected': #can't pass self.ConnectionStatus directly to GVE as it can have a value of None if it has never connected
                    self.GveServer.SendStatus(self.DeviceName, 'Connection', 'Connected')
                    self.PrintLog('{},GveServer Connection Status  = Connected,!!!!'.format(self.DeviceName))                                
                else: 
                    self.GveServer.SendStatus(self.DeviceName, 'Connection', 'Disconnected')
                    if self.ConnectionStatus == None:
                        self.PrintLog('{},Connection Status is None GveServer Connection Status = Disconnected,!!!!'.format(self.DeviceName))                                
                    elif self.ConnectionStatus == 'Disconnected':
                        self.PrintLog('{},Connection Status is Disconnected GveServer Connection Status = Disconnected,!!!!'.format(self.DeviceName))                                



    def UpdateBtnText(self,prmlstBtns,prmBtnText):
        for button in prmlstBtns:
            button.SetText('{0}'.format(prmBtnText))

    def SetAllStatus(self):
        if self.lstCurrentStatus != [self.TxNameStatus,self.BatteryLevelStatus,self.FrequencyStatus,self.SquelchStatus]:
            self.lstCurrentStatus = [self.TxNameStatus,self.BatteryLevelStatus,self.FrequencyStatus,self.SquelchStatus]
            self.PrintLog('{0},Connection Status = {1},Battery Level = {2},Frequency = {3},Squelch = {4},TxName = {5}'.format(self.DeviceName,self.Device.ReadStatus('ConnectionStatus'),self.BatteryLevelStatus,self.FrequencyStatus,self.SquelchStatus,self.TxNameStatus))
            if self.lstBatteryLevelStatBtns and self.BatteryLevelStatus:
                self.UpdateBtnText(self.lstBatteryLevelStatBtns,self.BatteryLevelStatus)    
                if self.GveServer != None:            
                    if self.BatteryLevelStatus in ('100%','70%'):
                        GveStatus = 'Normal'
                    elif self.BatteryLevelStatus in ('30%'):
                        GveStatus = 'Warning'
                    else:
                        GveStatus = 'Error'
                    self.GveServer.SendStatus(self.DeviceName, 'Device Status', GveStatus)
                    self.PrintLog('{},GveServer Device Status = {}'.format(self.DeviceName,GveStatus))
            if self.lstFrequencyStatBtns and self.FrequencyStatus:
                self.UpdateBtnText(self.lstFrequencyStatBtns,self.FrequencyStatus)                
            if self.lstSquelchStatBtns and self.SquelchStatus:
                self.UpdateBtnText(self.lstSquelchStatBtns,self.SquelchStatus)                
            if self.lstNameBtns and self.TxNameStatus:
                self.UpdateBtnText(self.lstNameBtns,'{0}\n{1}'.format(self.DeviceName,self.TxNameStatus))             
            if self.Device.ReadStatus('ConnectionStatus') == 'Connected':
                if self.lstCommsStatBtns:
                    if self.lstCommsStatBtns[0].State != 1:
                        for button in self.lstCommsStatBtns:
                            button.SetState(1)
            else:
                if self.lstCommsStatBtns:
                    if self.lstCommsStatBtns[0].State != 0:
                        for button in self.lstCommsStatBtns:
                            button.SetState(0)
        self.SendGveConnectionStatus()
        

    def CheckStatus(self):
        self.PollCount += 1
        if self.PollCount == 13:
            self.Device.Set('Push',None)
        if self.PollCount == 14:
            self.Device.Update('Squelch')            
        elif self.PollCount == 15:
            if self.Device.ReadStatus('ConnectionStatus') == 'Connected':
                self.BatteryLevelStatus = self.Device.ReadStatus('BatteryLevel')  
                if self.FrequencyStatus    != self.Device.ReadStatus('Frequency'):  
                    self.FrequencyStatus    = self.Device.ReadStatus('Frequency')  
                    self.BatteryLevelStatus = 'Unknown'
                self.SquelchStatus      = self.Device.ReadStatus('Squelch')          
                self.TxNameStatus       = self.Device.ReadStatus('Name')          
            else:
                self.BatteryLevelStatus = 'Unknown'
                self.FrequencyStatus    = 'Unknown'
                self.SquelchStatus      = 'Unknown'
                self.TxNameStatus       = 'Unknown'
            self.SetAllStatus()
        elif self.PollCount >= 16:
            self.PollCount = 0



    def FrequencyStatusSub(self,command,value,qualifier):
        #self.PrintLog('FrequencyStatus command =',command)
        self.PrintLog('{},FrequencyStatus value = {}'.format(self.DeviceName,value))
        #self.PrintLog('FrequencyStatus qualifier =',qualifier)
        if self.FrequencyStatus    != value:  
            self.BatteryLevelStatus = 'Unknown'
        self.FrequencyStatus = value
        self.SetAllStatus()


