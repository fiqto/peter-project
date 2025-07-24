"""
Speech recognition service implementation.
"""

import speech_recognition as sr
from typing import Optional
import logging

from ..core.exceptions import SpeechRecognitionError
from ..config.settings import ConfigManager


class SpeechRecognitionService:
    """Service for handling speech recognition functionality."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize speech recognition components
        self.recognizer = sr.Recognizer()
        self.microphone: Optional[sr.Microphone] = None
        
        self._initialize_microphone()
    
    def _initialize_microphone(self) -> None:
        """Initialize microphone and adjust for ambient noise."""
        try:
            self.microphone = sr.Microphone()
            
            # Adjust microphone for ambient noise
            with self.microphone as source:
                self.logger.info("Adjusting microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
            self.logger.info("Speech recognition service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize microphone: {e}")
            raise SpeechRecognitionError(f"Microphone initialization failed: {e}")
    
    def listen_for_command(self) -> Optional[str]:
        """Listen for voice commands and return recognized text."""
        if not self.microphone:
            raise SpeechRecognitionError("Microphone not initialized")
        
        try:
            settings = self.config_manager.config.settings
            
            with self.microphone as source:
                self.logger.debug("Listening for command...")
                
                # Listen for audio with configured timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=settings.speech_timeout,
                    phrase_time_limit=settings.phrase_time_limit
                )
            
            # Recognize speech using Google Speech Recognition
            command = self.recognizer.recognize_google(
                audio,
                language=settings.language
            )
            
            self.logger.info(f"Command recognized: {command}")
            return command.lower().strip()
            
        except sr.WaitTimeoutError:
            # Normal timeout, return None to continue listening
            self.logger.debug("Speech recognition timeout")
            return None
            
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return None
            
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            raise SpeechRecognitionError(f"Speech recognition service error: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in speech recognition: {e}")
            raise SpeechRecognitionError(f"Unexpected speech recognition error: {e}")
    
    def test_microphone(self) -> bool:
        """Test if microphone is working properly."""
        try:
            if not self.microphone:
                return False
            
            with self.microphone as source:
                # Try to listen for a very short duration
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=1)
                return audio is not None
                
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
    
    def get_microphone_info(self) -> dict:
        """Get information about available microphones."""
        try:
            microphone_list = sr.Microphone.list_microphone_names()
            return {
                'available_microphones': microphone_list,
                'default_microphone': microphone_list[0] if microphone_list else None,
                'total_count': len(microphone_list)
            }
        except Exception as e:
            self.logger.error(f"Failed to get microphone info: {e}")
            return {'error': str(e)}
    
    def set_microphone_sensitivity(self, energy_threshold: int) -> None:
        """Set microphone sensitivity."""
        try:
            self.recognizer.energy_threshold = energy_threshold
            self.logger.info(f"Set microphone energy threshold to: {energy_threshold}")
        except Exception as e:
            self.logger.error(f"Failed to set microphone sensitivity: {e}")
            raise SpeechRecognitionError(f"Failed to set microphone sensitivity: {e}")
    
    def calibrate_microphone(self, duration: float = 2.0) -> None:
        """Recalibrate microphone for ambient noise."""
        if not self.microphone:
            raise SpeechRecognitionError("Microphone not initialized")
        
        try:
            with self.microphone as source:
                self.logger.info(f"Calibrating microphone for {duration} seconds...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                
            self.logger.info("Microphone calibration completed")
            
        except Exception as e:
            self.logger.error(f"Microphone calibration failed: {e}")
            raise SpeechRecognitionError(f"Microphone calibration failed: {e}")
    
    def get_recognition_stats(self) -> dict:
        """Get speech recognition statistics."""
        return {
            'energy_threshold': self.recognizer.energy_threshold,
            'dynamic_energy_threshold': self.recognizer.dynamic_energy_threshold,
            'dynamic_energy_adjustment_damping': self.recognizer.dynamic_energy_adjustment_damping,
            'dynamic_energy_ratio': self.recognizer.dynamic_energy_ratio,
            'pause_threshold': self.recognizer.pause_threshold,
            'operation_timeout': self.recognizer.operation_timeout,
            'phrase_threshold': self.recognizer.phrase_threshold,
            'non_speaking_duration': self.recognizer.non_speaking_duration
        }