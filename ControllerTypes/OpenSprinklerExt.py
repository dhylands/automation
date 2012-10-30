# OpenSprinkler extension board connected to some GPIO pins

from ControllerType import ControllerType

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

_open_sprinkler_ext_controller = OpenSprinklerExt()
