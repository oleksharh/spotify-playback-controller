import time
import comtypes
from pycaw.pycaw import AudioUtilities, IAudioSessionEvents


class SpotifyVolumeHandler(comtypes.COMObject):
    """COM Callback class that handles volume changes for an individual audio session."""
    _com_interfaces_ = [IAudioSessionEvents]

    def __init__(self):
        super().__init__()

    def OnSimpleVolumeChanged(self, NewVolume, NewMute, EventContext):
        """Called automatically by Windows when Spotify's volume or mute state changes."""
        new_level = round(NewVolume * 100)
        is_muted = bool(NewMute)
        
        print(f"[SPOTIFY] Volume changed -> {new_level}% | Muted: {is_muted}")

    # IAudioSessionEvents requires these methods to be defined, even if left empty.
    def OnDisplayNameChanged(self, NewDisplayName, EventContext): pass
    def OnIconPathChanged(self, NewIconPath, EventContext): pass
    def OnChannelVolumeChanged(self, ChannelCount, NewChannelVolumeArray, ChangedChannel, EventContext): pass
    def OnGroupingParamChanged(self, NewGroupingParam, EventContext): pass
    def OnStateChanged(self, NewState): pass
    def OnSessionDisconnected(self, DisconnectReason): pass


def get_spotify_session():
    """Search active WASAPI sessions for Spotify."""
    for session in AudioUtilities.GetAllSessions():
        if session.Process and session.Process.name().lower() == "spotify.exe":
            return session
    return None


def main():
    comtypes.CoInitialize()

    print("Searching for Spotify session...")
    session = get_spotify_session()

    if not session:
        print("Error: Spotify.exe is not running or hasn't created an audio session yet.")
        print("Tip: Make sure Spotify is open and has played audio at least once.")
        return

    simple_volume = session.SimpleAudioVolume
    
    initial_volume = round(simple_volume.GetMasterVolume() * 100)
    initial_mute = bool(simple_volume.GetMute())
    
    print(f"[INITIAL STATE] Spotify Volume -> {initial_volume}% | Muted: {initial_mute}")


    # Grab the low-level AudioSessionControl interface (_ctl)
    session_control = session._ctl

    # Instantiate and register the listener
    callback_handler = SpotifyVolumeHandler()
    session_control.RegisterAudioSessionNotification(callback_handler)

    print("Listening for Spotify volume changes... Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nUnregistering hook and exiting...")
    finally:
        session_control.UnregisterAudioSessionNotification(callback_handler)


if __name__ == "__main__":
    main()