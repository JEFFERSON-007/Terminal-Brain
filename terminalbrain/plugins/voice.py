"""Optional voice module for Terminal Brain.

Provides speech-to-text voice commands.
Install with: terminal-brain install voice

"""


def init():
    """Initialize voice module."""
    return {
        "name": "voice",
        "backends": ["system_audio"],
        "description": "Voice command input for Terminal Brain",
    }


class VoiceInput:
    """Voice command input handler."""
    
    def __init__(self):
        self.audio_device = None
    
    async def listen(self, timeout: int = 5) -> str:
        """Listen for voice input and return transcribed text."""
        # This would use system audio APIs (PulseAudio, ALSA, etc.)
        # For now, placeholder showing architecture
        raise NotImplementedError("Voice input requires system audio configuration")
    
    def configure_audio(self, device: str) -> None:
        """Configure audio input device."""
        self.audio_device = device
