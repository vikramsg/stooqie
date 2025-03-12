import logging

# TODO: Have a development mode locally where everything is printed.
# For release use module name only.
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s")
logger = logging.getLogger()
