from pyb import RTC
import os
from util.airpy_config_utils import load_config_file

AIRPY_SYSTEM = 4
AIRPY_ERROR = 3
AIRPY_WARNING = 2
AIRPY_DEBUG = 1
AIRPY_INFO = 0

LOGGER_GLOBAL_REF = 0


class airpy_logger:

    def __init__(self, priority, caching_enabled=False):
        """
        Logger entry point
        :param priority: logger default priority
        :param caching_enabled: caching toggle
        :return:
        """
        self.__LOGGER_PRIORITY = priority
        self.__CACHING_ENABLED = caching_enabled
        self.__CACHE = []
        self.__CACHE_MAX_LENGTH = 5
        self.__RTC = RTC()
        datetime = self.__RTC.datetime()
        self.__AIR_PY_LOG = ("log/airpy-air-py-log-%02d-%02d-%02d-%02d.txt" % (datetime[1], datetime[2], datetime[4], datetime[5]))
        self.__SYSTEM_LOG = ("log/airpy-system-log-%02d-%02d-%02d-%02d.txt" % (datetime[1], datetime[2], datetime[4], datetime[5]))
        self.__FILESYSTEM_AVAILABLE = False
        try:
            app_config = load_config_file("app_config.json")
            info("Filla ***************** {}".format(app_config))
            self.__FILESYSTEM_AVAILABLE = app_config['serial_only']
        except:
            pass

        try:
            os.mkdir("log")
        except OSError:
            pass

    def __validate_priority(self, priority):
        """
        Determines if log can be printed
        :param priority: priority to be matched
        :return:
        """
        return priority >= self.__LOGGER_PRIORITY

    def __write_on_sd(self, priority, text):
        """
        Writes on sd
        :param priority: selected log priority
        :param text: text to be written
        :return:
        """

        try:
            if priority == AIRPY_SYSTEM and self.__FILESYSTEM_AVAILABLE:
                system_log = open(self.__SYSTEM_LOG, "a")
                system_log.write("%s\n" % text)
                system_log.close()
            if not self.__FILESYSTEM_AVAILABLE:
                print("Logger print:{}".format(text))
            else:
                self.__cache_log(text)
        except OSError:
            pass

    def __cache_log(self, text):
        """
        Caches log
        :param text: text to be cached
        :return:
        """
        if len(self.__CACHE) == self.__CACHE_MAX_LENGTH:
            self.flush()
        self.__CACHE.append(text)
        if not self.__CACHING_ENABLED:
            self.flush()

    def flush(self):
        """
        Flushes the content of cache to file log
        """
        air_py_log = open(self.__AIR_PY_LOG, "a")
        for text in self.__CACHE:
            air_py_log.write("%s\n" % text)
        air_py_log.close()
        self.__CACHE = []

    def airpy_log(self, priority, text):
        """
        Final gateway before writing the log
        :param priority: text priority
        :param text: text to be written
        :return:
        """
        if not self.__validate_priority(priority):
            return
        datetime = self.__RTC.datetime()
        time = ("%02d-%02d-%02d:%03d" % (datetime[4], datetime[5], datetime[6], datetime[7]))
        log_line = ("%s\t%s" % (time, text))
        self.__write_on_sd(priority, log_line)

    def set_logger_priority(self, priority):
        """
        Sets logging priority
        :param priority: new priority value
        :return:
        """
        self.__LOGGER_PRIORITY = priority


def init(priority, caching_enabled=False):
    """
    Initialize logger
    :param priority: priority to assign to airpy logger
    :param caching_enabled: caching toggle
    :return:
    """
    global LOGGER_GLOBAL_REF
    if not LOGGER_GLOBAL_REF:
        LOGGER_GLOBAL_REF = airpy_logger(priority, caching_enabled)

def system(text):
    """
    Prints text with system priority
    :param text: text that will e printed
    :return:
    """
    global LOGGER_GLOBAL_REF
    if LOGGER_GLOBAL_REF:
        LOGGER_GLOBAL_REF.airpy_log(AIRPY_SYSTEM, "SYSTEM\t{}".format(text))

def error(text):
    """
    Prints text with error priority
    :param text: text that will e printed
    :return:
    """
    global LOGGER_GLOBAL_REF
    if LOGGER_GLOBAL_REF:
        LOGGER_GLOBAL_REF.airpy_log(AIRPY_ERROR, "ERROR\t{}".format(text))


def warning(text):
    """
    Prints text with warning priority
    :param text: text that will e printed
    :return:
    """
    global LOGGER_GLOBAL_REF
    if LOGGER_GLOBAL_REF:
        LOGGER_GLOBAL_REF.airpy_log(AIRPY_WARNING, "WARNING\t{}".format(text))


def debug(text):
    """
    Prints text with debug priority
    :param text: text that will e printed
    :return:
    """
    global LOGGER_GLOBAL_REF
    if LOGGER_GLOBAL_REF:
        LOGGER_GLOBAL_REF.airpy_log(AIRPY_DEBUG, "DEBUG\t{}".format(text))


def info(text):
    """
    Prints text with info priority
    :param text: text that will e printed
    :return:
    """
    global LOGGER_GLOBAL_REF
    if LOGGER_GLOBAL_REF:
        LOGGER_GLOBAL_REF.airpy_log(AIRPY_INFO, "INFO\t{}".format(text))
