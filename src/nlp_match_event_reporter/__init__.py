"""
NLP Match Event Reporter

Real-time soccer match event reporting system using natural language processing
and voice interaction for hands-free operation during live matches.
"""

__version__ = "0.1.0"
__author__ = "PitchConnect"
__email__ = "info@pitchconnect.se"
__license__ = "MIT"

from .core.config import settings
from .core.exceptions import (
    NLPReporterError,
    VoiceProcessingError,
    FOGISIntegrationError,
    EventProcessingError,
)

__all__ = [
    "settings",
    "NLPReporterError",
    "VoiceProcessingError", 
    "FOGISIntegrationError",
    "EventProcessingError",
]
