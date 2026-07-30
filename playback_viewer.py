import asyncio
import time

from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager,
    GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus
)

async def get_playback_info(session_id=None):
    if session_id is None:
        session_id = "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify" 

    manager = await MediaManager.request_async()
    sessions = manager.get_sessions()

    for session in sessions:
        if session.source_app_user_model_id.lower() == session_id.lower():
            playback_info = session.get_playback_info()
            playback_status = playback_info.playback_status
            props = await session.try_get_media_properties_async()
            # print(session.get_playback_info().playback_status) # PlaybackStatus.PLAYING or PlaybackStatus.PAUSED
            # print(session.try_toggle_play_pause_async()) # play/pause

            title = props.title
            artist = props.artist

            return {
                "title": title,
                "artist": artist,
                "status": playback_status.name,
                "position": session.get_timeline_properties().position.total_seconds(),
                "end_time": session.get_timeline_properties().end_time.total_seconds(),
            }

    return None

from volume_callback import main

def get_spotify_volume():
    main()


if __name__ == "__main__":
    info = asyncio.run(get_playback_info())
    print(info)
    get_spotify_volume()


