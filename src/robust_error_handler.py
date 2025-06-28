"""
Robust error handling for file parsing operations
"""

import logging
import traceback
from typing import Any, Dict, List, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class RobustErrorHandler:
    """Handles errors gracefully with fallback strategies"""
    
    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable, error_context: str = ""):
        """Execute primary function with fallback on failure"""
        try:
            result = primary_func()
            if result:
                return result
        except Exception as e:
            logger.warning(f"{error_context} - Primary method failed: {e}")
        
        try:
            logger.info(f"{error_context} - Attempting fallback method")
            return fallback_func()
        except Exception as e:
            logger.error(f"{error_context} - Fallback method also failed: {e}")
            return None
    
    @staticmethod
    def safe_execute(func: Callable, default_return: Any = None, context: str = ""):
        """Safely execute function with error logging"""
        try:
            return func()
        except Exception as e:
            logger.error(f"{context} failed: {e}")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(traceback.format_exc())
            return default_return
    
    @staticmethod
    def create_default_zones(file_path: str = "", context: str = "") -> List[Dict]:
        """NO FALLBACK ZONES - REAL PARSING ONLY"""
        logger.error(f"Attempted to create fallback zones for {context} - DISABLED")
        return []  # Return empty list - no fake zones

def robust_parser(error_context: str = ""):
    """Decorator for robust parsing with error handling - NO FALLBACKS"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                logger.error(f"{error_context} - {func.__name__} failed: {e}")
                
            # NO FALLBACKS - return None if parsing fails
            return None
        return wrapper
    return decorator