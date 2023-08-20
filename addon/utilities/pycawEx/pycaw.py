"""
Python wrapper around the Core Audio Windows API.
"""
# import here all newly split up modules,
# to keep backwards compatibility

# flake8: noqa
# yes, the imports are unused

from .api.audioclient import IAudioClient, ISimpleAudioVolume
from .api.audioclient.depend import WAVEFORMATEX
from .api.audiopolicy import (
    IAudioSessionControl,
    IAudioSessionControl2,
    IAudioSessionEnumerator,
    IAudioSessionEvents,
    IAudioSessionManager,
    IAudioSessionManager2,
    IAudioSessionNotification,
    IAudioVolumeDuckNotification,
)
from .api.endpointvolume import (
    IAudioEndpointVolume,
    IChannelAudioVolume,
    IAudioEndpointVolumeCallback,
    IAudioMeterInformation,
)
from .api.endpointvolume.depend import (
    AUDIO_VOLUME_NOTIFICATION_DATA,
    PAUDIO_VOLUME_NOTIFICATION_DATA,
)
from .api.mmdeviceapi import (
    IMMDevice,
    IMMDeviceCollection,
    IMMDeviceEnumerator,
    IMMEndpoint,
    IMMNotificationClient,
)
from .api.mmdeviceapi.depend import IPropertyStore
from .api.mmdeviceapi.depend.structures import (
    PROPERTYKEY,
    PROPVARIANT,
    PROPVARIANT_UNION,
)
from .constants import (
    AUDCLNT_SHAREMODE,
    DEVICE_STATE,
    STGM,
    AudioDeviceState,
    EDataFlow,
    ERole,
    CLSID_MMDeviceEnumerator,
)
from .utils import AudioDevice, AudioSession, AudioUtilities
from .callbacks import MMNotificationClient
