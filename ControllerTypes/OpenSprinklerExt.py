# OpenSprinkler extension board connected to some GPIO pins

from ControllerType import ControllerType
from DefaultDict import ErrorFound

class OpenSprinklerExt(ControllerType):

    def __init__(self):
        ControllerType.__init__(self, "OpenSprinklerExt")

    def Dump(self):
        print "Controller: OpenSprinklerExt"

    def ControllerConfigItems(self):
        return ['Boards', 'Data', 'Clock', 'Latch', 'OE']

    def ActuatorConfigItems(self):
        return ['Station']

    def ActuatorID(self, actuator):
        """Returns an ID string to distinguish actuators belonging to the same ControllerType"""
        return 'Station: ' + actuator.GetConfig('Station')

    def SetActuator(self, actuator, value):
        print "OpenSprinklerExt: SetActuator %s to %d" % (actuator.Id(), value)

    def ValidateControllerParams(self, config_dict, error_dict):
        """Make sure that all of the required configuration is present and valid"""
        for item in self.ControllerConfigItems():
            if (item not in config_dict) or (not config_dict[item].isdigit()):
                error_dict[item] = item + ' must be numeric.'

    def ValidateActuatorParams(self, controller, config_dict, error_dict):
        print 'OpenSprinklerExt ValidatectuatorParams'
        for item in self.ActuatorConfigItems():
            if (item not in config_dict) or (not config_dict[item].isdigit()):
                error_dict[item] = item + ' must be numeric.'
        if not ErrorFound(error_dict):
            station_id = int(config_dict['Station'])
            if station_id < 1:
                error_dict['Station'] = 'Station must be >= 1'
            else:
                num_boards = int(controller.GetConfig('Boards'))
                max_stations = num_boards * 8
                if station_id > max_stations:
                    error_dict['Station'] = 'Station must be <= ' + str(max_stations) + ' (for ' + str(num_boards) + ' boards)'

_open_sprinkler_ext_controller = OpenSprinklerExt()
