# The DummyController just prints the on/off commands to stdout

from ControllerType import ControllerType

class DummyController(ControllerType):

    def __init__(self):
        ControllerType.__init__(self, "DummyController")

    def Dump(self):
        print "Controller: DummyController"

    def ControllerConfigItems(self):
        return ['A', 'B']

    def ValidateControllerParams(self, config_dict, error_dict):
        """Make sure that all of the required configuration is present and valid"""
        if ('A' not in config_dict) or (config_dict['A'] == ''):
            error_dict['A'] = 'This parameter is required'
            return
        if not config_dict['A'].isdigit():
            error_dict['A'] = 'Must be numeric'
            return

    def ValidateActuatorParams(self, controller, config_dict, error_dict):
        """Make sure that all of the required configuration is present and valid"""
        if ('Id' not in config_dict) or (config_dict['Id'] == ''):
            error_dict['Id'] = 'This parameter is required'
            return
        if not config_dict['Id'].isdigit():
            error_dict['Id'] = 'Must be numeric'
            return

    def ActuatorConfigItems(self):
        return ['Id']

    def ActuatorID(self, actuator):
        """Returns an ID string to distinguish actuators belonging to the same ControllerType"""
        return 'ID: ' + actuator.GetConfig('Id')

    def SetActuator(self, actuator, value):
        print "Dummmy: SetActuator %s to %d" % (actuator.Id(), value)

_dummy_controller = DummyController()
