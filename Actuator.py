import string
import AutomationConfig

_order = 1000
_actuators = {}
_aliases = {}

def Add(actuator):
    global _actuators
    global _aliases
    potential_aliases = NameToNames(actuator.config_dict['Name'])
    actual_aliases = []
    for alias in potential_aliases:
        if alias not in _aliases:
            _aliases[alias] = actuator
            actual_aliases.append(alias)
    actuator.config_dict['Names'] = actual_aliases
    actuator.config_dict['Name'] = NamesToName(actual_aliases)
    _actuators[actuator.Name()] = actuator
    actuator.SetOrderIfNeeded()
    AutomationConfig.Write()

def Delete(actuator, write_config=True):
    global _actuators
    global _aliases
    if actuator.Name() in _actuators:
        del _actuators[actuator.Name()]
    for alias in actuator.Names():
        if alias in _aliases:
            del _aliases[alias]
    if write_config:
        AutomationConfig.Write()

def Find(name):
    if name in _actuators:
        return _actuators[name]
    if name in _aliases:
        return _aliases[name]

def NameToNames(name):
    return name.replace(',', ' ').split()

def NamesToName(names):
    return ', '.join(names)

def NextOrder():
    global _order
    next_order = _order
    _order = _order + 100
    return next_order

def DumpActuators():
    for actuator_name in _actuators:
        _actuators[actuator_name].Dump()

def ActuatorsAsArray():
    return _actuators.items()

def OrderedActuators(category=None):
    actuators = ActuatorsAsArray()
    if category:
        actuators = filter(lambda a: a[1].Category() == category, actuators)
    return sorted(actuators, key=lambda a: a[1].Order())

def AliasesAsArray():
    return _aliases.items()

def OrderedAliases(category=None):
    aliases = AliasesAsArray()
    if category:
        aliases = filter(lambda a: a[1].Category() == category, aliases)
    return sorted(aliases, key=lambda a: a[1].Order())

def ActuatorCategories():
    result = set()
    for actuator_name in _actuators:
        actuator = _actuators[actuator_name]
        if actuator.Category():
            result.add(actuator.Category())
    return sorted(result)

def ActuatorCountForController(controller):
    actuatorCount = 0
    for actuator_name in _actuators:
        actuator = _actuators[actuator_name]
        if actuator.controller == controller:
            actuatorCount = actuatorCount + 1
    return actuatorCount

def ActuatorsForController(controller):
    actuators = []
    for actuator_name in _actuators:
        actuator = _actuators[actuator_name]
        if actuator.controller == controller:
            actuators.append(actuator)
    return sorted(actuators, key=lambda actuator: actuator.Order())

class Actuator:
    """Represents a sprinkler actuator, which is something that can be turned on or off."""

    def __init__(self, controller, config_dict):
        global _order
        self.controller = controller
        self.config_dict = config_dict
        self.state = 0
        self.SetOrderIfNeeded()
        Add(self)

    def Edit(self, new_config_dict):
        Delete(self, write_config=False)
        config_items = self.Controller().ActuatorConfigItems()
        for item in new_config_dict:
            if item in config_items:
                self.config_dict[item] = new_config_dict[item]
        Add(self)

    def SetOrderIfNeeded(self):
        global _order
        if not 'Order' in self.config_dict:
            self.config_dict['Order'] = ''
        if self.Order() == '':
            self.config_dict['Order'] = NextOrder()
        if _order < int(self.config_dict['Order']):
            _order = int(self.config_dict['Order']) + 100

    def Name(self):
        return self.GetConfig('Name')

    def Names(self):
        return self.GetConfig('Names')

    def NamesAsStr(self):
        return string.join(self.Names(), ', ')

    def Category(self):
        return self.GetConfig('Category')

    def Controller(self):
        return self.controller

    def ControllerName(self):
        return self.Controller().Name()

    def ConfigItems(self):
        return self.Controller().ActuatorConfigItems()

    def GetConfig(self, name):
        if name in self.config_dict:
            return self.config_dict[name]
        return ''

    def GetConfigDict(self):
        return self.config_dict

    def ID(self):
        return self.Controller().ActuatorID(self)

    def Description(self):
        return self.GetConfig('Description')

    def Order(self):
        return self.GetConfig('Order')

    def State(self):
        return self.state

    def SetState(self,onOff):
        self.state = onOff

    def ToggleState(self):
        self.SetState(not self.State())

    def StateStr(self):
        return 'On' if self.State() else 'Off';

    def Validate(self, config_dict, error_dict):
        return self.Controller().ValidateActuator(self, config_dict, error_dict)

    def Dump(self):
        print "Actuator:", self.Name()
        for name in self.ConfigItems():
            print "  %s: %s" % (name, self.GetConfig(name))

