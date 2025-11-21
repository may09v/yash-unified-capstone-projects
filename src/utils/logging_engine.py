import logging
import os
def setup_logger(name, log_file):
   os.makedirs(os.path.dirname(log_file), exist_ok=True)
   level = logging.DEBUG
   formatter = logging.Formatter('%(message)s | %(asctime)s | %(levelname)s')
   handler = logging.FileHandler(log_file)
   handler.setFormatter(formatter)
   logger = logging.getLogger(name)
   logger.setLevel(level)
   logger.addHandler(handler)
   return logger