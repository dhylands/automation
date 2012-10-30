# A ControllerType abstracts a type of Controller.
#
# ControllerType objects are things like an Open Sprinkler extension board,
# an Open Sprinkler board, a gpio pin, etc.
#
# You can also think of a ControllerType as having the logic portion of a Controller.
# The Controller object has the data portion.

import Controller
import Actuator

_controller_type = {}

def Add(c):
    _controller_type[c.Name()] = c

def Find(name):
    if name in _controller_type:
        return _controller_type[name]

def GetTypes():
    return _controller_type.keys()

def Dump():
    for name in _controller_type:
        controller_type = _controller_type[name]
        controller_type.Dump()

class ControllerType:
    """Base class for a ControllerType objects."""

    def __init__(self, name):
        self.name = name
        Add(self)

    def Dump(self):
        print "ControllerType:", self.name

    def Name(self):
        return self.name

    def ActuatorAllConfigItems(self):
        """Return all config items (core + actuator specific) for this ControllerType"""
        return self.ActuatorCoreConfigItems() + self.ActuatorConfigItems()

    def ActuatorAllConfigItemDefaults(self):
        """Return defaults for all config items (core + actuator specific) for this ControllerType"""
        return dict(self.ActuatorCoreConfigItemDefaults().items() + self.ActuatorConfigItemDefaults().items())

    def ActuatorConfigItems(self):
        """Return the Actuator config items"""
        return []

    def ActuatorConfigItemDefaults(self):
        """Return defaults for the Actuator config items"""
        return {}

    def ActuatorCoreConfigItems(self):
        """Return the core Actuator config items (items required for all actuators"""
        return ['Controller', 'Name', 'Category', 'Description', 'Order']

    def ActuatorCoreConfigItemDefaults(self):
        """Return defaults for the core Actuator config items"""
        return {'Category': 'None', 'Description': '', 'Order': ''}

    def ControllerAllConfigItems(self):
        """Return all config items (core + controller specific)"""
        return self.ControllerCoreConfigItems() + self.ControllerConfigItems()

    def ControllerAllConfigItemDefaults(self):
        """Return defaults for all config items (core + controller specific)"""
        return dict(self.ControllerCoreConfigItemDefaults().items() + self.ControllerConfigItemDefaults().items())

    def ControllerConfigItems(self):
        """Return the Controller specific config items"""
        return []

    def ControllerConfigItemDefaults(self):
        """Return defaults for the Controller specific config items"""
        return {}

    def ControllerCoreConfigItems(self):
        """Return core config items (items required for all controllers)"""
        return ['Type', 'Name', 'Category']

    def ControllerCoreConfigItemDefaults(self):
        """Return defaults for the core config items (items required for all controllers)"""
        return {'Category': 'None'}

    def CreateController(self, config_dict):
        """Constructs a controller for this type of controller"""
        return Controller.Controller(self, config_dict)

    def CreateActuator(self, controller, config_dict):
        """Constructs a actuator for this type of controller"""
        return Actuator.Actuator(controller, config_dict)

    def ControllerID(self, controller):
        """Returns an ID string to distinguish controllers belonging to the same ControllerType"""
        items = []
        for config in controller.ConfigItems():
            items.append(config + ': ' + controller.GetConfig(config))
        return ', '.join(items)

    def ValidateController(self, controller):
        """Make sure that all of the required configration is present in a controller."""
        return

    def ValidateNewController(self, config_dict, error_dict):
        """Make sure that the name and parameters are valid"""
        controller_name = config_dict['Name']
        if controller_name == '':
            error_dict['Name'] = 'Must provide a controller name.'
        elif Controller.Find(controller_name):
            error_dict['Name'] = 'Controller ' + controller_name + ' already exists.'
        self.ValidateControllerParams(config_dict, error_dict)

    def ValidateControllerParams(self, config_dict, error_dict):
        """Make sure that all of the required configuration is present and valid"""
        return True

    def ValidateNewActuator(self, config_dict, error_dict):
        """Make sure that the name and parameters are valid"""
        actuator_names = config_dict['Names']
        if len(actuator_names) == 0:
            error_dict['Names'] = 'Must provide actuator name(s).'
        else:
            actuator_name = ' '.join(actuator_names)
            if Actuator.Find(actuator_name):
                error_dict['Names'] = 'Actuator "' + actuator_names + '" already exists.'
            else:
                for alias in actuator_names:
                    if Actuator.Find(alias):
                        error_dict['Names'] = 'Actuator "' + alias + '" already exists.'
        self.ValidateActuatorParams(config_dict, error_dict)

    def ValidateActuatorParams(self, config_dict, error_dict):
        """Make sure that all of the required configration is present in an actuator."""
        return

    def ActuatorID(self, actuator):
        """Returns an ID string to distinguish actuators belonging to the same ControllerType"""
        return ''

    def SetActuator(self, actuator, value):
        """Turns an actuator on or off"""
        return

