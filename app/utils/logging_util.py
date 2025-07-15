# import logging
# import sys
# import os

# class StdoutFilter(logging.Filter):
#     """Filter to only allow records below ERROR level to stdout"""
#     def filter(self, record):
#         return record.levelno < logging.ERROR

# def setup_logging(level=logging.INFO, format_string=None, gcp_log_name="python-app"):
#     # Prevent duplicate handlers
#     root_logger = logging.getLogger()

#     # --- Local console logging setup ---
#     if root_logger.handlers: # Check again in case of GCP fallback or multiple calls
#         return
    
#     # Create formatters
#     if format_string is None:
#         format_string = '%(asctime)s: %(levelname)s: [%(funcName)s]: %(message)s'

#     formatter = logging.Formatter(format_string)

#     # Create handlers
#     stdout_handler = logging.StreamHandler(sys.stdout)
#     stderr_handler = logging.StreamHandler(sys.stderr)
    
#     # Set levels
#     stdout_handler.setLevel(logging.DEBUG)
#     stderr_handler.setLevel(logging.ERROR)

#     # Set formatters
#     stdout_handler.setFormatter(formatter)
#     stderr_handler.setFormatter(formatter)
    
#     # Add filters to prevent duplicate messages
#     stdout_handler.addFilter(StdoutFilter())
#     # stderr_handler doesn't need a filter since it only gets ERROR+

#     # Configure root logger
#     root_logger.setLevel(level)
#     root_logger.addHandler(stdout_handler)
#     root_logger.addHandler(stderr_handler)
