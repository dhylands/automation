import AutomationConfig
import Controller
import Actuator

AutomationConfig.SetConfigFilename('automation.config')
print '===== Reading Configuration ====='
AutomationConfig.Read()
print '===== Dumping Controllers ====='
Controller.DumpControllers()
print '===== Dumping Actuators ====='
Actuator.DumpActuators()
print '===== Writing Configuration ====='
AutomationConfig.Write()

