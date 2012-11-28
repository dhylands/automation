import AutomationConfig
import Actuator
import string

_controllers = {}

def Add(controller):
    global _controllers
    _controllers[controller.Name()] = controller
    AutomationConfig.Write()

def Delete(controller_name, write_config=True):
    global _controllers
    if controller_name in _controllers:
        del _controllers[controller_name]
    if write_config:
        AutomationConfig.Write()

def Find(name):
    if name in _controllers:
        return _controllers[name]

def DumpControllers():
    for controller_name in _controllers:
        _controllers[controller_name].Dump()

def GetNames():
    return sorted(_controllers.keys())

def ControllersAsArray():
    return _controllers.values()

def ControllerCategories():
    result = set()
    for controller_name in _controllers:
        controller = _controllers[controller_name]
        if controller.Category():
            result.add(controller.Category())
    return sorted(result)

def OrderedControllers(category=None):
    controllers = ControllersAsArray()
    if category:
        controllers = filter(lambda c: c.Category() == category, controllers)
    return sorted(controllers, key=lambda c: c.Name())

class Controller:

    def __init__(self, controller_type, config_dict):
        self.controller_type = controller_type
        self.config_dict = config_dict
        Add(self)

    def Dump(self):
        """Print an ASCII representation of a controller (for debugging)"""
        print "Controller:", self.Name()
        for name in self.ConfigItems():
            print "  %s: %s" %(name, self.GetConfig(name))

    def Edit(self, new_config_dict):
        Delete(self, write_config=False)
        config_items = self.Type().ControllerAllConfigItems()
        for item in new_config_dict:
            if item in config_items:
                print 'Edit: Setting item', item, 'to', new_config_dict[item]
                self.config_dict[item] = new_config_dict[item]
        Add(self)

    def Name(self):
        return self.GetConfig('Name')

    def ID(self):
        return self.Type().ControllerID(self)

    def Category(self):
        return self.GetConfig('Category')

    def ConfigItems(self):
        return self.Type().ControllerAllConfigItems()

    def ConfigItemDefaults(self):
        return self.Type().ControllerAllConfigItemDefaults()

    def ActuatorConfigItems(self):
        return self.Type().ActuatorAllConfigItems()

    def ActuatorConfigItemDefaults(self):
        return self.Type().ActuatorAllConfigItemDefaults()

    def ActuatorID(self, actuator):
        return self.Type().ActuatorID(actuator)

    def ActuatorCount(self):
        return Actuator.ActuatorCountForController(self)

    def Actuators(self):
        return Actuator.ActuatorsForController(self)

    def Validate(self, config_dict, error_dict):
        return self.controller_type.ValidateController(self, config_dict, error_dict)

    def ValidateActuator(self, actuator, new_config_dict, error_dict):
        return self.controller_type.ValidateActuator(self, actuator, new_config_dict, error_dict)

    def ValidateNewActuator(self, config_dict, error_dict):
        return self.controller_type.ValidateNewActuator(self, config_dict, error_dict)

    def GetConfigDict(self):
        return self.config_dict

    def GetConfig(self, name):
        if name in self.config_dict:
            return self.config_dict[name]
        return ''

    def CreateActuator(self, config_dict):
        return self.Type().CreateActuator(self, config_dict)

    def SetActuator(self, actuator, value):
        self.Type().SetActuator(actuator, value)

    def Type(self):
        return self.controller_type

    def TypeStr(self):
        return self.Type().Name()

