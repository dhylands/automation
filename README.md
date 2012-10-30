automation
==========

Home Automation Controol

This is the beginnings of a Home Automation Controller.

It uses the <http://flask.pocoo.org/> micro-framework. You can start the server using:

python server.py

and then browse to localhost:5000/automation

Classes
=======

Here's an overview of the basic classes.

Controller - A Controller can manipulate multiple Actuators.

Actuator - An actuator controls a solenoid, relay, or switch

ControllerType - base class for for a type of controller. Each controller type
may have multiple controllers, and each controller may control multiple actuators.

The ControllerType derived classes come from the ControllerTypes subdirectory.

An example of a ControllerType would be an OpenSprinkler <http://rayshobby.net/?page_id=160> board.
There would be a Controller instance for each OpenSprinkler board, and an Actuator for each
of the eight control lines that the OpenSprinkler controller can control.
