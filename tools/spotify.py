import pyautogui


def spotify_play_pause() -> str:
    pyautogui.press("playpause")
    return "Toggled Spotify play/pause."


def spotify_next_track() -> str:
    pyautogui.press("nexttrack")
    return "Skipped to next track."


def spotify_previous_track() -> str:
    pyautogui.press("prevtrack")
    return "Went to previous track."


def spotify_volume_up() -> str:
    pyautogui.press("volumeup")
    return "Increased volume."


def spotify_volume_down() -> str:
    pyautogui.press("volumedown")
    return "Decreased volume."


def spotify_mute() -> str:
    pyautogui.press("volumemute")
    return "Toggled mute."