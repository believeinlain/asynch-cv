"""Simple test of pmd_consumer functionality from a live source"""

from async_cv.play_file import play_file
from async_cv.event_processing.pmd_consumer import pmd_consumer

play_file('', 50, pmd_consumer)
