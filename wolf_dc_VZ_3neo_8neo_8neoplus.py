from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'VZ-8neo': self.wolf_16_2517_normal,
            'VZ-3neo': self.wolf_16_2517_normal,
            'VZ-8neo+': self.wolf_16_2517_plus,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioVolume': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'ColorMode': {'Status': {}},
            'Detail': {'Status': {}},
            'DigitalZoom': {'Status': {}},
            'EraseMemory': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Freeze': {'Status': {}},
            'Iris': {'Parameters': ['Speed'], 'Status': {}},
            'Keylock': {'Status': {}},
            'Light': {'Status': {}},
            'MainResolution': {'Status': {}},
            'MemoryRecall': {'Status': {}},
            'MemorySave': {'Status': {}},
            'MenuControl': {'Status': {}},
            'Menu': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PositiveNegativeBlue': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetStore': {'Status': {}},
            'Snapshot': {'Status': {}},
            'Source': {'Status': {}},
            'StreamingMode': {'Status': {}},
            'VideoPlayback': {'Parameters': ['Speed'], 'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            }

        self.UpdateRegex = re.compile(b'([\x00|\x08][\x00-\xFF][\x00-\x04][\x00-\x05][\x00-\x64]{0,3})|(\x80[\x0A|\x31|\\x29|\x80|\x56|\xA0|\x98|\\x5D|\x1F|\x54|\x30|\x65|\x75|\x9E|\x6D|\x53|\x75][\x01-\x09])')
        self.SetRegex = re.compile(b'(\x01[\x00-\xFF]\x00)|(\x81[\x0A|\x31|\\x29|\x80|\x56|\xA0|\x98|\x5D|\x1F|\x54|\x30|\x65|\x75|\x9E|\x6D|\x53|\x80|\x75][\x01-\x09])')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\x01\x0A\x01\x00',
            '4:3': b'\x01\x0A\x01\x01'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'\x00': '16:9',
            b'\x01': '4:3'
        }

        AspectRatioCmdString = b'\x00\x0A\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio : Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x09\x04\x02\x01\x01',
            'Off': b'\x09\x04\x02\x01\x00'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AudioMuteCmdString = b'\x08\x04\x02\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4:5]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAudioVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioVolumeCmdString = pack('6B', 0x09, 0x04, 0x03, 0x02, 0x00, value)
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):

        AudioVolumeCmdString = b'\x08\x04\x03\x00'
        res = self.__UpdateHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[5])
                self.WriteStatus('AudioVolume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Audio Volume: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x31\x01\x01',
            'Off': b'\x01\x31\x01\x00'
        }

        AutoFocusCmdString = ValueStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        AutoFocusCmdString = b'\x00\x31\x00'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus : Invalid/unexpected response'])

    def SetColorMode(self, value, qualifier):

        ValueStateValues = {
            'Black/White': b'\x01\x6D\x01\x00',
            'Presentation': b'\x01\x6D\x01\x01',
            'Natural': b'\x01\x6D\x01\x02',
            'Video Conference': b'\x01\x6D\x01\x03',
            'Manual': b'\x01\x6D\x01\x04'
        }

        ColorModeCmdString = ValueStateValues[value]
        self.__SetHelper('ColorMode', ColorModeCmdString, value, qualifier)

    def UpdateColorMode(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Black/White',
            b'\x01': 'Presentation',
            b'\x02': 'Natural',
            b'\x03': 'Video Conference',
            b'\x04': 'Manual'
        }

        ColorModeCmdString = b'\x00\x6D\x00'
        res = self.__UpdateHelper('ColorMode', ColorModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('ColorMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Color Mode : Invalid/unexpected response'])

    def SetDetail(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x01\x53\x01\x00',
            'Medium': b'\x01\x53\x01\x02',
            'High': b'\x01\x53\x01\x03'
        }

        DetailCmdString = ValueStateValues[value]
        self.__SetHelper('Detail', DetailCmdString, value, qualifier)

    def UpdateDetail(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Off',
            b'\x02': 'Medium',
            b'\x03': 'High'
        }

        DetailCmdString = b'\x00\x53\x00'
        res = self.__UpdateHelper('Detail', DetailCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Detail', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Detail : Invalid/unexpected response'])

    def SetDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            '2x': b'\x01\x29\x01\x01',
            'Off': b'\x01\x29\x01\x00'
        }

        DigitalZoomCmdString = ValueStateValues[value]
        self.__SetHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)

    def UpdateDigitalZoom(self, value, qualifier):

        ValueStateValues = {
            b'\x01': '2x',
            b'\x00': 'Off',
            b'\x02': '4x'
        }

        DigitalZoomCmdString = b'\x00\x29\x00'
        res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('DigitalZoom', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Digital Zoom : Invalid/unexpected response'])

    def SetEraseMemory(self, value, qualifier):

        EraseMemoryCmdString = b'\x01\x92\x01\x20'
        self.__SetHelper('EraseMemory', EraseMemoryCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far': 0x01,
            'Near': 0x02,
        }
        focusspeed = int(qualifier['Speed'])
        if 1 <= focusspeed <= 15:
            if value == 'Stop':
                FocusCmdString = pack('>4B', 0x01, 0x2F, 0x01, 0x00)
            else:
                FocusCmdString = pack('>6B', 0x01, 0x21, 0x03, ValueStateValues[value], 0x00, focusspeed)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x56\x01\x01',
            'Off': b'\x01\x56\x01\x00'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        FreezeCmdString = b'\x00\x56\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze : Invalid/unexpected response'])

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Open': 0x01,
            'Close': 0x02
        }

        SpeedStateValues = {
            'Normal': 0x01,
            'Fast': 0x02
        }
        Irisspeed = qualifier['Speed']
        if Irisspeed in SpeedStateValues:
            if value == 'Stop':
                IrisCmdString = pack('>4B', 0x01, 0x2F, 0x01, 0x00)
            else:
                IrisCmdString = pack('>6B', 0x01, 0x22, 0x03, ValueStateValues[value], 0x00, SpeedStateValues[Irisspeed])
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetKeylock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x80\x01\x01',
            'Off': b'\x01\x80\x01\x00'
        }

        KeylockCmdString = ValueStateValues[value]
        self.__SetHelper('Keylock', KeylockCmdString, value, qualifier)

    def UpdateKeylock(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        KeylockCmdString = b'\x00\x80\x00'
        res = self.__UpdateHelper('Keylock', KeylockCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Keylock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Keylock : Invalid/unexpected response'])

    def SetLight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\xA0\x01\x01',
            'Off': b'\x01\xA0\x01\x00',
            'Slidebox On': b'\x01\xA0\x01\x03'
        }

        LightCmdString = ValueStateValues[value]
        self.__SetHelper('Light', LightCmdString, value, qualifier)

    def UpdateLight(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
        }

        LightCmdString = b'\x00\xA0\x00'
        res = self.__UpdateHelper('Light', LightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Light', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Light : Invalid/unexpected response'])

    def SetMainResolution(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x51\x04\x00\x00\x00\x00',
            'SVGA/60': b'\x01\x51\x04\x00\x00\x3C\x01',
            'XGA/60': b'\x01\x51\x04\x00\x00\x3C\x04',
            'SXGA/60': b'\x01\x51\x04\x00\x00\x3C\x0A',
            'UXGA/60': b'\x01\x51\x04\x00\x00\x3C\x0D',
            '720p/60': b'\x01\x51\x04\x00\x00\x3C\x16',
            '1080p/30': b'\x01\x51\x04\x00\x00\x1E\x18',
            '1080p/60': b'\x01\x51\x04\x00\x00\x3C\x18',
            'WUXGA/60': b'\x01\x51\x04\x00\x00\x3C\x1C',
            'WXGA*/60': b'\x01\x51\x04\x00\x00\x3C\x1E'
        }

        MainResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('MainResolution', MainResolutionCmdString, value, qualifier)

    def UpdateMainResolution(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00': 'Auto',
            b'\x3C\x01': 'SVGA/60',
            b'\x3C\x04': 'XGA/60',
            b'\x3C\x0A': 'SXGA/60',
            b'\x3C\x0D': 'UXGA/60',
            b'\x3C\x16': '720p/60',
            b'\x1E\x18': '1080p/30',
            b'\x3C\x18': '1080p/60',
            b'\x3C\x1C': 'WUXGA/60',
            b'\x3C\x1E': 'WXGA*/60'
        }

        MainResolutionCmdString = b'\x00\x51\x00'
        res = self.__UpdateHelper('MainResolution', MainResolutionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5:7]]
                self.WriteStatus('MainResolution', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Main Resolution : Invalid/unexpected response'])

    def SetMemoryRecall(self, value, qualifier):

        if 1 <= int(value) <= 9:
            MemoryRecallCmdString = pack('>BBBB', 0x01, 0x91, 0x01, int(value))
            self.__SetHelper('MemoryRecall', MemoryRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMemoryRecall')

    def SetMemorySave(self, value, qualifier):

        if 1 <= int(value) <= 9:
            MemorySaveCmdString = pack('>BBBB', 0x01, 0x92, 0x01, int(value))
            self.__SetHelper('MemorySave', MemorySaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMemorySave')

    def SetMenuControl(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x99\x01\x02',
            'Down': b'\x01\x99\x01\x08',
            'Left': b'\x01\x99\x01\x04',
            'Right': b'\x01\x99\x01\x06',
            'Enter': b'\x01\x99\x01\x05',
            'Help': b'\x01\x99\x01\x10',
            'Reset': b'\x01\x99\x01\x90'
        }

        MenuControlCmdString = ValueStateValues[value]
        self.__SetHelper('MenuControl', MenuControlCmdString, value, qualifier)

    def SetMenu(self, value, qualifier):

        ValueStateValues = {
            'Menu Off': b'\x01\x98\x01\x00',
            'Standard Menu On': b'\x01\x98\x01\x03',
            'Extra Menu On': b'\x01\x98\x01\x04',
            'Memory Menu On': b'\x01\x98\x01\x05',
            'USB Menu On': b'\x01\x98\x01\x06',
        }

        MenuCmdString = ValueStateValues[value]
        self.__SetHelper('Menu', MenuCmdString, value, qualifier)

    def UpdateMenu(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Menu Off',
            b'\x01': 'Standard Menu On',
            b'\x02': 'Extra Menu On',
            b'\x03': 'View Menu'
        }

        MenuCmdString = b'\x00\x98\x00'
        res = self.__UpdateHelper('Menu', MenuCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Menu', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Menu : Invalid/unexpected response'])

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x5D\x01\x01',
            'Off': b'\x01\x5D\x01\x00'
        }

        PIPCmdString = ValueStateValues[value]
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PIPCmdString = b'\x00\x5D\x00'
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP : Invalid/unexpected response'])

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Side by Side': b'\x01\x1F\x01\x01',
            'PIP': b'\x01\x1F\x01\x00',
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Side by Side',
            b'\x00': 'PIP',
        }

        PIPModeCmdString = b'\x00\x1F\x00'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PIP Mode : Invalid/unexpected response'])

    def SetPositiveNegativeBlue(self, value, qualifier):

        ValueStateValues = {
            'Positive': b'\x01\x54\x01\x00',
            'Negative': b'\x01\x54\x01\x01',
            'Blue': b'\x01\x54\x01\x02'
        }

        PositiveNegativeBlueCmdString = ValueStateValues[value]
        self.__SetHelper('PositiveNegativeBlue', PositiveNegativeBlueCmdString, value, qualifier)

    def UpdatePositiveNegativeBlue(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Positive',
            b'\x01': 'Negative',
            b'\x02': 'Blue'
        }

        PositiveNegativeBlueCmdString = b'\x00\x54\x00'
        res = self.__UpdateHelper('PositiveNegativeBlue', PositiveNegativeBlueCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('PositiveNegativeBlue', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Positive Negative Blue : Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x30\x01\x01',
            'Off': b'\x01\x30\x01\x00'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        PowerCmdString = b'\x00\x30\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power : Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x01\x40\x01\x01',
            '2': b'\x01\x40\x01\x02',
            '3': b'\x01\x40\x01\x03'
        }

        if self.model == 'VZ-8neo+':
            PresetRecallCmdString = ValueStateValues[value]
        else:
            PresetRecallCmdString = b'\x01\x40\x01\x01'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetStore(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x01\x41\x01\x01',
            '2': b'\x01\x41\x01\x02',
            '3': b'\x01\x41\x01\x03'
        }

        if self.model == 'VZ-8neo+':
            PresetStoreCmdString = ValueStateValues[value]
        else:
            PresetStoreCmdString = b'\x01\x41\x01\x01'
        self.__SetHelper('PresetStore', PresetStoreCmdString, value, qualifier)

    def SetSnapshot(self, value, qualifier):

        SnapshotCmdString = b'\x01\x95\x01\x00'
        self.__SetHelper('Snapshot', SnapshotCmdString, value, qualifier)

    def SetSource(self, value, qualifier):

        ValueStateValues = {
            'Live': b'\x01\x9E\x01\x00',
            'Mem': b'\x01\x9E\x01\x01',
            'USB': b'\x01\x9E\x01\x02',
            'Extern': b'\x01\x9E\x01\x03',
            'Net': b'\x01\x9E\x01\x05'
        }

        SourceCmdString = ValueStateValues[value]
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Live',
            b'\x01': 'Mem',
            b'\x02': 'USB',
            b'\x03': 'Extern',
            b'\x05': 'Net',
            b'\x04': 'Extern 2'
        }

        SourceCmdString = b'\x00\x9E\x00'
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source : Invalid/unexpected response'])

    def SetStreamingMode(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x01\x75\x01\x00',
            'Continuous': b'\x01\x75\x01\x02'
        }

        StreamingModeCmdString = ValueStateValues[value]
        self.__SetHelper('StreamingMode', StreamingModeCmdString, value, qualifier)

    def UpdateStreamingMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Auto',
            b'\x00': 'Off',
            b'\x02': 'Continuous'
        }

        StreamingModeCmdString = b'\x00\x75\x00'
        res = self.__UpdateHelper('StreamingMode', StreamingModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('StreamingMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Streaming Mode : Invalid/unexpected response'])

    def SetVideoPlayback(self, value, qualifier):

        videospeed = int(qualifier['Speed'])
        if 1 <= videospeed <= 15:
            if value == 'Fast Forward Stop':
                VideoPlaybackCmdString = b'\x01\x99\x02\x01\x00'
            elif value == 'Pause/Resume':
                VideoPlaybackCmdString = b'\x01\x99\x01\x91'
            else:
                VideoPlaybackCmdString = pack('>5B', 0x01, 0x99, 0x02, 0x01, videospeed)
            self.__SetHelper('VideoPlayback', VideoPlaybackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoPlayback')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x01\x65\x01\x00',
            'Manual': b'\x01\x65\x01\x02',
            'Perform WB': b'\x01\x65\x01\x10'
        }

        WhiteBalanceCmdString = ValueStateValues[value]
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            b'\x00': 'Auto',
            b'\x02': 'Manual',
        }

        WhiteBalanceCmdString = b'\x00\x65\x00'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3:4]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance : Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
           'Wide': 0x01,
           'Tele': 0x02,
        }
        zoomspeed = int(qualifier['Speed'])
        if 1 <= zoomspeed <= 15:
            if value == 'Stop':
                ZoomCmdString = pack('>4B', 0x01, 0x2F, 0x01, 0x00)
            else:
                ZoomCmdString = pack('>6B', 0x01, 0x20, 0x03, ValueStateValues[value], 0x00, zoomspeed)

            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        CommandAction = {
            b'\x80': 'Get',
            b'\x81': 'Set'
            }
        CommandList = {
            b'\x0A': 'Aspect Ratio',
            b'\x31': 'Auto Focus',
            b'\x29': 'Digital Zoom',
            b'\x56': 'Freeze',
            b'\xA0': 'Light',
            b'\x9E': 'Source',
            b'\x98': 'Menu On Off',
            b'\x5D': 'PIP',
            b'\x1F': 'PIP Mode',
            b'\x54': 'Positive Negative Blue',
            b'\x30': 'Power',
            b'\x65': 'White Balance',
            b'\x75': 'Streaming Mode',
            b'\x6D': 'Color Mode',
            b'\x53': 'Detail',
            b'\x80': 'Keylock',
            b'\x51': 'Main Resolution'
            }
        ErrorType = {
            b'\x01': 'Time Out',
            b'\x02': 'Invalid Cmd',
            b'\x03': 'Invalid Parameter',
            b'\x04': 'Invalid Length',
            b'\x05': 'FiFo Full',
            b'\x06': 'Firmware Update Error',
            b'\x07': 'Access Denied',
            b'\x08': 'AUTH Required',
            b'\x09': 'Busy'
            }
        if response:
            if response[0:1] in CommandAction and response[1:2] in CommandList and response[2:3] in ErrorType:
                self.Error(['{0} {1} Error: {2}'.format(CommandList[response[1:2]], CommandAction[response[0:1]], ErrorType[response[2:3]])])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                self.Error(['{} : Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def wolf_16_2517_plus(self):
        self.model = 'VZ-8neo+'
        
    def wolf_16_2517_normal(self):
        self.model = 'VZ-8neo'

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
        
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
        
            Method['callback'] = callback
            Method['qualifier'] = qualifier    
        else:
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

