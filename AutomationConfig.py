import ConfigParser
import copy
import imp
import os
import sys
from DefaultDict import DefaultDict, ErrorFound, PrintErrors

_config = None
_config_name = 'automation.config'

_config_section = "Config"
_config_being_read = False

class MissingControllerType(Exception):
    """No controller type specified"""
    pass

class UnknownControllerType(Exception):
    """Unknown controller type specified"""
    pass

class MissingActuatorController(Exception):
    """No controller specified for Actuator"""
    pass

class UnknownActuatorController(Exception):
    """Unknown controller type specified"""
    pass

class InvalidControllerConfig(Exception):
    """Something is messed up in the .config file"""
    pass

class InvalidActuatorConfig(Exception):
    """Something is messed up in the .config file"""
    pass

def Config():
    return _config

def SetConfigFilename(configFilename):
    global _config_name
    _config_name = configFilename
    print 'Config Filename set to', _config_name

def Read():
    """Reads the configuration file and creates all of the various objects."""
    global _config_being_read
    _config_being_read = True
    _ReadConfigFile()
    _ReadGlobals()
    _ReadControllerTypes()
    _ReadControllers()
    _ReadActuators()
    _config_being_read = False

def Write():
    """Writes the configuration file from the state of all of the various objects"""
    global _config
    if _config_being_read:
        return
    _config = ConfigParser.ConfigParser()
    _WriteGlobals()
    _WriteControllers()
    _WriteActuators()
    _WriteConfigFile()

def GetBoolean(section, option, default):
    if _config.has_option(section, option):
        return _config.getboolean(section, option)
    return default

def SetBoolean(section, option, value):
    _config.set(section, option, 'true' if value else 'false')

def Set(section, option, value):
    _config.set(section, option, value)

def _ReadConfigFile():
    """Reads the sprinkler config file, if required"""
    global _config
    _config = ConfigParser.ConfigParser()
    _config.read(_config_name)
    return _config

def _WriteConfigFile():
    with open(_config_name, 'wb') as config_file:
        _config.write(config_file)

def _ReadGlobals():
    """Sets up globals which are read from the config file"""
    global print_config_summary
    global print_config_detail
    print_config_summary = GetBoolean(_config_section, 'print_config_summary', False)
    print_config_detail = GetBoolean(_config_section, 'print_config_detail', False)

def _WriteGlobals():
    """Writes the globals back into the config file"""
    _config.add_section(_config_section)
    SetBoolean(_config_section, 'print_config_summary', print_config_summary)
    SetBoolean(_config_section, 'print_config_detail', print_config_detail)

def _ReadControllerTypes():
    """Loads all of the *.py files from the ControllerTypes subdirectory."""
    automation_config_dir = imp.find_module("AutomationConfig")[1]
    controller_types_dir = os.path.join(os.path.dirname(automation_config_dir), "ControllerTypes")
    controller_type_files = [fname[:-3] for fname in os.listdir(controller_types_dir) if fname.endswith(".py")]
    if not controller_types_dir in sys.path:
        sys.path.insert(0, controller_types_dir)
    for controller_type_file in controller_type_files:
        if print_config_summary:
            print '[Config] Create ControllerType:', controller_type_file
        __import__(controller_type_file)

def _ReadControllers():
    """Reads in the Configuration file and creates the Controller objects"""
    import ControllerType
    for section in _config.sections():
        if section[0:11] == 'Controller:':
            controller_name = section[11:].strip()
            if not _config.has_option(section, 'Type'):
                raise MissingControllerType("Controller: '%s' missing controller type" % controller_name)
            controller_type_name = _config.get(section, 'Type')
            controller_type = ControllerType.Find(controller_type_name)
            if not controller_type:
                raise UnknownControllerType("Controller: '%s' unknown controller type: '%s'" % (controller_name, controller_type_name))

            config_dict = DefaultDict(controller_type.ControllerAllConfigItemDefaults())
            config_dict['Name'] = controller_name

            for item in controller_type.ControllerAllConfigItems():
                if _config.has_option(section, item):
                    config_dict[item] = _config.get(section, item)

            if print_config_summary:
                print '[Config] Create Controller:', controller_name, 'Type:', controller_type_name
            if print_config_detail:
                for item in config_dict:
                    print '[Config]   ', item, '=', config_dict[item]

            error_dict = DefaultDict()
            controller_type.ValidateNewController(config_dict, error_dict)
            if ErrorFound(error_dict):
                PrintErrors(error_dict)
                raise InvalidControllerConfig('Errors encountered parsing config file')
            else:
                controller = controller_type.CreateController(config_dict)

def _WriteControllers():
    """Writes all of the Controller objects into the config file"""
    import Controller
    controllers = Controller.OrderedControllers()
    for controller in controllers:
        if print_config_summary:
            print '[Config] Writing Controller:', controller.Name(), 'Type:', controller.TypeStr()
        if print_config_detail:
            for item in controller.ConfigItems():
                print '[Config]   ', item, '=', controller.GetConfig(item)

        section = 'Controller: ' + controller.Name()
        _config.add_section(section)
        for name in controller.ConfigItems():
            if name != 'Name':
                Set(section, name, controller.GetConfig(name))

def _ReadActuators():
    """Reads in the Configuration file and creates the Actuator objects"""
    import Controller
    import Actuator
    for section in _config.sections():
        if section[0:9] == 'Actuator:':
            actuator_name = section[9:].strip()
            actuator_names = Actuator.NameToNames(actuator_name)
            print 'ReadActuators: actuator_name =', actuator_name
            print 'ReadActuators: actuator_names =', actuator_names
            if not _config.has_option(section, 'controller'):
                raise MissingActuatorController("Actuator: '%s' missing controller" % actuator_name)
            controller_name = _config.get(section, 'controller')
            controller = Controller.Find(controller_name)
            if not controller:
                raise UnknownActuatorController("Controller: '%s' unknown controller: '%s'" % (actuator_name, controller_name))

            config_dict = DefaultDict(controller.ActuatorConfigItemDefaults())
            config_dict['Name'] = actuator_name
            config_dict['Names'] = actuator_names
            for item in controller.ActuatorConfigItems():
                if _config.has_option(section, item):
                    config_dict[item] = _config.get(section, item)

            if print_config_summary:
                print '[Config] Create Actuator:', actuator_name, 'Controller:', controller_name
            if print_config_detail:
                for item in config_dict:
                    print '[Config]   ', item, '=', config_dict[item]

            error_dict = DefaultDict()
            controller.ValidateNewActuator(config_dict, error_dict)
            if ErrorFound(error_dict):
                PrintErrors(error_dict)
                raise InvalidActuatorConfig('Errors encountered parsing config file')
            else:
                actuator = controller.CreateActuator(config_dict)

def _WriteActuators():
    """Writes all of the Actuator objects into the configuration file"""
    import Actuator
    actuators = Actuator.OrderedActuators()
    for item in actuators:
        actuator = item[1]
        if print_config_summary:
            print '[Config] Writing Actuator:', actuator.Name(), 'Type:', actuator.ControllerName()
        if print_config_detail:
            for item in actuator.ConfigItems():
                print '[Config]   ', item, '=', actuator.GetConfig(item)

        section = 'Actuator: ' + actuator.Name()
        _config.add_section(section)
        for name in actuator.ConfigItems():
            if name != 'Name':
                Set(section, name, actuator.GetConfig(name))

# Don't be tempted to put a main test here and call read
# Instead, do it from another module (That's why TestConfig.py exists)
#
# This is due to circular imports. If I can figure out a decent way to get rid of the
# circular imports, then this restriction will go away.
