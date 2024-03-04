from extronlib import event
from extronlib.interface import SerialInterface, EthernetClientInterface, EthernetServerInterface
from extronlib.system import Wait
from decimal import *
import re


class DeviceEthernetClass:
    Objects = {}
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 5
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        #self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Name  = 'RadioMic'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGain': {'Status': {}},
            'BatteryLevel': {'Status': {}},
            'Warning': {'Status': {}},
            'Equalizer': {'Status': {}},
            'EqualizerSR': {'Parameters': ['Low', 'Low Mid', 'Mid', 'Mid High', 'High'], 'Status': {}},
            'Frequency': {'Parameters': ['Bank', 'Channel'], 'Status': {}},
            'Mode': {'Status': {}},
            'Mute': {'Status': {}},
            'Push': {'Status': {}},
            'Sensitivity': {'Status': {}},
            'Squelch': {'Status': {}},
            'Name': {'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'AfOut (-?\d{1,2})\r'), self.__MatchAudioGain, None)
            self.AddMatchString(re.compile(b'Bat (\d{1,3}|\?)\r'), self.__MatchBatteryLevel, None)
            self.AddMatchString(re.compile(b'Msg (Low_Battery|OK)\r'), self.__MatchWarning, None)
            self.AddMatchString(re.compile(b'Equalizer (0|1|2|3)\r'), self.__MatchEqualizer, None)
            self.AddMatchString(re.compile(b'Frequency \\b([5-8][0-9]{5})\\b \\b([0-9]|1[0-9]|20)\\b ([0-9]{1,2})\r'), self.__MatchFrequency, None)#MS Edit Would not decode Bank 20
            self.AddMatchString(re.compile(b'Mode (0|1)\r'), self.__MatchMode, None)
            self.AddMatchString(re.compile(b'Mute (0|1)\r'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'Sensitivity (-[0-9]{1,2}|0)\r'), self.__MatchSensitivity, None)
            self.AddMatchString(re.compile(b'Squelch (\d{1,2})\r'), self.__MatchSquelch, None)
            self.AddMatchString(re.compile(b'Name (.{0,8})\r'), self.__MatchName, None)
            self.AddMatchString(re.compile(b'10(?P<errno>\d{1})0: .* \[ (?P<command>.+) \]\r'), self.__MatchError, None)

        #self.WriteStatus('BatteryLevel', 'Not Measured Yet', None)

        DeviceEthernetClass.Objects[self.IPAddress] = self #MS Edit

    @classmethod
    def StartDataDispatch(cls):
        cls.server = EthernetServerInterface(53212, 'UDP')
        print('^^^^^^^^^^^^^^^^^^ RadioMicServer Start ^^^^^^^^^')
        @event(cls.server, 'ReceiveData')
        def handleData(client, data):
            #print('+++++++++++++++++ RadioMic @classmethod ReceiveData ^^^^^^^^^')
            try:
                Object = cls.Objects[client.IPAddress]
                Object.ReceiveDataHandler(data)
            except KeyError:
                print('Unknown Device: {}'.format(client.IPAddress))
            
            
        if cls.server.StartListen() != 'Listening':
            print('Port unavailable: 53212')

    def SetAudioGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -24,
            'Max': 24
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioGainCmdString = 'AfOut {0}\r'.format(value)
            self.__SetHelper('AudioGain', AudioGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioGain')

    def UpdateAudioGain(self, value, qualifier):
        self.__UpdateHelper('AudioGain', 'AfOut\r', value, qualifier)

    def __MatchAudioGain(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('AudioGain', value, None)

    def __MatchBatteryLevel(self, match, tag):

        ValueStateValues = {
            b'0':  'Low Battery',
            b'10': 'Low Battery',
            b'20': 'Low Battery',
            b'30': '30%',
            b'40': '40%',
            b'50': '50%',
            b'60': '60%',
            b'70': '70%',
            b'80': '80%',
            b'90': '90%',
            b'100': '100%',
            b'?': 'Unavailable'
            #b'?': 'Low Battery'
        }

        value = ValueStateValues[match.group(1)]
        if value != 'Unavailable':
            self.WriteStatus('BatteryLevel', value, None)
        else:
            if self.Commands['BatteryLevel']['Status']:
                BatStatus = self.Commands['BatteryLevel']['Status']['Live']
                #print('A BatStatus = ',BatStatus)
                if 'Last' not in BatStatus:
                    self.Commands['BatteryLevel']['Status']['Live'] ='Last Reading :\n'+BatStatus
                    #print('B BatStatus = ',BatStatus)
            #print('**********',self.Commands['BatteryLevel']['Status'])        

    def __MatchWarning(self, match, tag):

        ValueStateValues = {
            b'Low_Battery': 'Low Battery',
            b'OK': 'OK'
        }

        value = ValueStateValues[match.group(1)]
        if value != 'OK':
            self.WriteStatus('BatteryLevel', value, None)


    def SetEqualizer(self, value, qualifier):

        ValueStateValues = {
            'Flat': 'Equalizer 0\r',
            'Low Cut': 'Equalizer 1\r',
            'Low Cut and High Boost': 'Equalizer 2\r',
            'High Boost': 'Equalizer 3\r'
        }

        EqualizerCmdString = ValueStateValues[value]
        self.__SetHelper('Equalizer', EqualizerCmdString, value, qualifier)

    def UpdateEqualizer(self, value, qualifier):
        self.__UpdateHelper('Equalizer', 'Equalizer\r', value, qualifier)

    def __MatchEqualizer(self, match, tag):

        ValueStateValues={
            b'0': 'Flat',
            b'1': 'Low Cut',
            b'2': 'Low Cut and High Boost',
            b'3': 'High Boost'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Equalizer', value, None)

    def SetEqualizerSR(self, value, qualifier):

        Low = int(qualifier['Low'])
        LowMid = int(qualifier['Low Mid'])
        Mid = int(qualifier['Mid'])
        MidHigh = int(qualifier['Mid High'])
        High = int(qualifier['High'])

        Constraints = {
            'Min': -5,
            'Max': 5
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        if Constraints['Min'] <= Low <= Constraints['Max'] \
                and Constraints['Min'] <= LowMid <= Constraints['Max'] \
                and Constraints['Min'] <= Mid <= Constraints['Max'] \
                and Constraints['Min'] <= MidHigh <= Constraints['Max'] \
                and Constraints['Min'] <= High <= Constraints['Max']:
            EqualizerSRCmdString = 'Equalizer {0} {1} {2} {3} {4} {5}\r'.format(
                ValueStateValues[value], Low, LowMid, Mid, MidHigh, High)
            self.__SetHelper('EqualizerSR', EqualizerSRCmdString, value, qualifier)
        else:
            print('Invalid Command for SetEqualizerSR')

    def SetFrequency(self, value, qualifier):

        bank = int(qualifier['Bank'])
        channel = int(qualifier['Channel'])

        if 0 <= bank <= 26 and 0 <= channel <= 64 and 516 <= value <= 865:
            frequency = int(value * 1000)
            FrequencyCmdString = 'Frequency {0} {1} {2}\r'.format(
                frequency, bank, channel)
            self.__SetHelper('Frequency', FrequencyCmdString, value,
                             qualifier)
        else:
            print('Invalid Command for SetFrequency')

    def UpdateFrequency(self, value, qualifier):

        FrequencyCmdString = 'Frequency\r'
        self.__UpdateHelper('Frequency', FrequencyCmdString, value, qualifier)

    def __MatchFrequency(self, match, tag):

        #qualifier = {'Bank': match.group(2).decode(),
        #             'Channel': match.group(3).decode()}
        qualifier = None
        valueTmp  = int(match.group(1).decode())
        valueTmp  = Decimal(valueTmp)/Decimal(1000)
        value = '{0:.3f} MHz\nB.Ch:  {1}.{2}'.format(valueTmp,match.group(2).decode(),match.group(3).decode())
        #FreqString = match.group(1).decode()
        #FreqStringLeft   = FreqString[:-3]
        #FreqStringRight  = FreqString.strip(FreqStringLeft)
        #value = '{0}.{1} MHz'.format(FreqStringLeft,FreqStringRight)
        #print('!@!@!@!@!@ Frequency', value, qualifier)
        self.WriteStatus('Frequency', value, qualifier)

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Mono': 'Mode 0\r',
            'Stereo': 'Mode 1\r'
        }

        ModeCmdString = ValueStateValues[value]
        self.__SetHelper('Mode', ModeCmdString, value, qualifier)

    def UpdateMode(self, value, qualifier):

        ModeCmdString = 'Mode\r'
        self.__UpdateHelper('Mode', ModeCmdString, value, qualifier)

    def __MatchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Mono',
            '1': 'Stereo'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mode', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute 1\r',
            'Off': 'Mute 0\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):
        self.__UpdateHelper('Mute', 'Mute\r', value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Mute', value, None)

    '''
    def UpdateName(self, value, qualifier):

        self.__UpdateHelper('Name', 'Name\r', value, qualifier)
    '''
    def __MatchName(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('Name', value, None)



    def SetPush(self, value, qualifier):
        self.__SetHelper('Push', 'Push 0 100 1\r', value, qualifier)

    def SetSensitivity(self, value, qualifier):

        ValueConstraints = {
            'Min': -42,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SensitivityCmdString = 'Sensitivity {0}\r'.format(value)
            self.__SetHelper('Sensitivity', SensitivityCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSensitivity')

    def UpdateSensitivity(self, value, qualifier):

        SensitivityCmdString = 'Sensitivity\r'
        self.__UpdateHelper('Sensitivity', SensitivityCmdString, value, qualifier)

    def __MatchSensitivity(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Sensitivity', value, None)

    def SetSquelch(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            '5 dB': '5',
            '7 dB': '7',
            '9 dB': '9',
            '11 dB': '11',
            '13 dB': '13',
            '15 dB': '15',
            '17 dB': '17',
            '19 dB': '19',
            '21 dB': '21',
            '23 dB': '23',
            '25 dB': '25'
        }

        SquelchCmdString = 'Squelch ' + ValueStateValues[value] + '\r'
        self.__SetHelper('Squelch', SquelchCmdString, value, qualifier)

    def UpdateSquelch(self, value, qualifier):

        self.__UpdateHelper('Squelch', 'Squelch\r', value, qualifier)

    def __MatchSquelch(self, match, tag):

        ValueStateValues = {
            b'0': 'Off',
            b'5': '5 dB',
            b'7': '7 dB',
            b'9': '9 dB',
            b'11': '11 dB',
            b'13': '13 dB',
            b'15': '15 dB',
            b'17': '17 dB',
            b'19': '19 dB',
            b'21': '21 dB',
            b'23': '23 dB',
            b'25': '25 dB'
        }

        value=ValueStateValues[match.group(1)]
        self.WriteStatus('Squelch', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)
        #print('Radio Mic commandstring =',commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            elif self.counter > self.connectionCounter:
                self.counter = self.connectionCounter+1

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        errors = {
            b'0': 'Invalid Command',
            b'1': 'Invalid Parameter',
            b'2': 'Value out of range',
            b'3': 'Relative parameter not supported',
            b'4': 'Invalid number of parameters',
            b'5': 'Incorrect termination'
        }

        try:
            err_string = errors[match.group('errno')]
            cmd = match.group('command')
            print('{0} : {1}'.format(cmd, err_string))
        except KeyError:
            print('Unknown Error')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command=self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command]={'method': {}}

            Subscribe=self.Subscription[command]
            Method=Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method=Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]]={}
                            Method=Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback']=callback
            Method['qualifier']=qualifier
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        #print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& 1 Status =',Status)
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    return None
        try:
            return Status['Live']
        except:
            return None

    def ReceiveDataHandler(self, data):#the data is passed to this function from the server in the @classmethod
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        #print('{0} {1} _ReceiveBuffer = {2}'.format(self.Name,self.IPAddress,self._ReceiveBuffer))
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback,
                                                'para': arg}


   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer=self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        if b'\r' in self._ReceiveBuffer:
            self._ReceiveBuffer = self._ReceiveBuffer.rsplit(b'\r',1)[-1] 
        return True


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType='Ethernet'
        DeviceEthernetClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
