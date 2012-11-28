from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import flash
from flask import url_for
from redirect_back import get_redirect_target, redirect_back
import jinja2

import collections

import Actuator
import automation
import AutomationConfig
import os

import logging
from DefaultDict import DefaultDict, ErrorFound, StrippedCopy

debug = False

app = Flask(__name__)
app.secret_key = 'automation secret'
#app.config.from_object(__name__)

CONFIG_FILE = 'automation.config'
if 'CONFIG_FILE' in os.environ:
    CONFIG_FILE = os.environ['CONFIG_FILE'];

file_handler = logging.FileHandler('server.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))

app.logger.addHandler(file_handler)

# Make ControllerCategories and ActuatorCatgories functions available
# to automation-layout.html
app.jinja_env.globals.update(ControllerCategories=automation.ControllerCategories)
app.jinja_env.globals.update(ActuatorCategories=automation.ActuatorCategories)

def button_request(prefix, form):
    for item in form:
        if item[0:len(prefix)] == prefix:
            return item[len(prefix):]

@app.route('/')
def root():
    return redirect(url_for('automation_controllers'))

@app.route('/automation')
def automation_root():
    return redirect(url_for('automation_controllers'))

@app.route('/automation/config')
def automation_config():
    return render_template('automation-config.html', config=automation.Config())

@app.route('/automation/controllers/category/<category>', methods=['POST', 'GET'])
def automation_controllers_category(category):
    return automation_controllers(category)

@app.route('/automation/controllers', methods=['POST', 'GET'])
def automation_controllers(category=None):
    if debug: print 'automation_controllers, category =', category
    if request.method == 'POST':
        if 'add' in request.form:
            controller_type_name = request.form['controller_type_name']
            return redirect(url_for('automation_add_controller', controller_type_name=controller_type_name))
        edit_controller_name = button_request('edit-', request.form)
        if edit_controller_name:
            controller = automation.FindController(edit_controller_name)
            if controller:
                return redirect(url_for('automation_edit_controller', controller_name=edit_controller_name))
        del_controller_name = button_request('del-', request.form)
        if del_controller_name:
            automation.DeleteController(del_controller_name)
            flash('Deleted Controller: ' + del_controller_name)
    controllers = automation.OrderedControllers(category)
    return render_template('automation-controllers.html', controllers=controllers, category=category, controller_types=automation.GetControllerTypes())

@app.route('/automation/controller/<controller_name>', methods=['POST', 'GET'])
def automation_show_controller(controller_name):
    if debug: print 'automation_show_controller'
    controller = automation.FindController(controller_name)
    if not controller:
        flash("No controller named '" + controller_name + "'")
        return redirect(url_for('automation_controllers'))
    if request.method == 'POST':
        if 'edit' in request.form:
            return redirect(url_for('automation_edit_controller', controller_name=controller_name))
        actuator_name = button_request('toggle-', request.form)
        if actuator_name:
            actuator = automation.FindActuator(actuator_name)
            if actuator:
                actuator.ToggleState()
                flash('Actuator ' + actuator.Name() + ' turned ' + actuator.StateStr())
    return render_template('automation-controller.html', controller=controller)

@app.route('/automation/controllers/add/<controller_type_name>', methods=['POST', 'GET'])
def automation_add_controller(controller_type_name):
    if debug: print 'automation_add_controller'
    error_dict = DefaultDict()
    config_dict = StrippedCopy(request.form)
    param = DefaultDict(config_dict)
    controller_type = automation.FindControllerType(controller_type_name)
    if not controller_type:
        flash("No controller type named '" + controller_type_name + "'", 'error')
        return redirect(url_for('automation_controllers'))
    title = 'Add Controller for ' + controller_type.Name()
    param['action'] = 'Add'
    if request.method == 'POST':
        if 'action' in request.form:
            del config_dict['action']
            controller_type.ValidateNewController(config_dict, error_dict)
            if ErrorFound(error_dict):
                return render_template('automation-edit-controller.html', title=title, controller_type=controller_type, error=error_dict, param=param)
            controller = automation.AddController(controller_type, param)
            flash('Added Controller: ' + controller.Name())
        return redirect_back('automation_controllers')
    param['Type'] = controller_type.Name()
    return render_template('automation-edit-controller.html', title=title, controller_type=controller_type, error=error_dict, param=param)

@app.route('/automation/controllers/edit/<controller_name>', methods=['POST', 'GET'])
def automation_edit_controller(controller_name):
    if debug: print 'automation_edit_controller'
    next = get_redirect_target()
    controller = automation.FindController(controller_name)
    if not controller:
        flash("No controller named '" + controller_name + "'")
        return redirect(url_for('automation_controllers'))
    controller_type = controller.Type()
    title = 'Edit Controller - ' + controller.Name()
    error_dict = DefaultDict()
    if request.method == 'POST':
        if 'action' in request.form:
            config_dict = StrippedCopy(request.form)
            param = DefaultDict(config_dict)
            del config_dict['action']
            controller.Validate(config_dict, error_dict)
            if ErrorFound(error_dict):
                return render_template('automation-edit-controller.html', title=title, controller_type=controller_type, next=next, param=param, error=error_dict)
            automation.EditController(controller, config_dict)
            flash('Updated Controller: ' + controller.Name())
        return redirect(url_for('automation_controllers'))
        #return redirect_back('automation_controllers')
    param = controller.GetConfigDict()
    param['action'] = 'Update'
    return render_template('automation-edit-controller.html', title=title, controller_type=controller_type, next=next, param=param, error=error_dict)

@app.route('/automation/actuator/<actuatorname>/<state>')
def automation_actuator(actuatorname, state):
    if debug: print 'automation_actuator'
    actuator = automation.FindActuator(actuatorname)
    if actuator:
        stateMap = {'0':0, '1':1, 'on':1, 'off':0}
        if state in stateMap:
            actuator.SetState(stateMap[state])
            flash('Actuator ' + actuatorname + ' turned ' + actuator.StateStr())
    return redirect_back('automation_actuators')

@app.route('/automation/aliases/category/<category>', methods=['POST', 'GET'])
def automation_aliases_category(category):
    return automation_aliases(category)

@app.route('/automation/aliases', methods=['POST', 'GET'])
def automation_aliases(category=None):
    if debug: print 'automation_aliases'
    return automation_actuators_or_aliases('Aliases', category, automation.OrderedAliases)

@app.route('/automation/actuators/category/<category>', methods=['POST', 'GET'])
def automation_actuators_category(category):
    return automation_actuators(category)

@app.route('/automation/actuators', methods=['POST', 'GET'])
def automation_actuators(category=None):
    if debug: print 'automation_actuators'
    return automation_actuators_or_aliases('Actuators', category, automation.OrderedActuators)

def automation_actuators_or_aliases(title, category, actuator_func):
    if debug: print 'automation_actuators_or_aliases'
    if request.method == 'POST':
        if 'add' in request.form:
            controller_name = request.form['controller_name']
            return redirect(url_for('automation_add_actuator', controller_name=controller_name))
        actuator_name = button_request('toggle-', request.form)
        if actuator_name:
            actuator = automation.FindActuator(actuator_name)
            if actuator:
                actuator.ToggleState()
                flash('Actuator "' + actuator_name + '" turned ' + actuator.StateStr())
        edit_actuator_name = button_request('edit-',request.form)
        if edit_actuator_name:
            actuator = automation.FindActuator(edit_actuator_name)
            if actuator:
                return redirect(url_for('automation_edit_actuator', actuator_name=edit_actuator_name))
        del_actuator_name = button_request('del-',request.form)
        if del_actuator_name:
            automation.DeleteActuator(del_actuator_name)
            flash('Deleted Actuator: ' + del_actuator_name)
    controller_names = automation.GetControllerNames()
    return render_template('automation-actuators.html', title=title, category=category, actuators=actuator_func(category), controller_names=controller_names)

@app.route('/automation/actuators/add/<controller_name>', methods=['POST', 'GET'])
def automation_add_actuator(controller_name):
    if debug: print 'automation_add_actuator'
    next = get_redirect_target()
    error_dict = DefaultDict()
    config_dict = StrippedCopy(request.form)
    param = DefaultDict(config_dict)
    controller = automation.FindController(controller_name)
    if not controller:
        flash('Unable to find controller named ' + controller_name)
        return redirect_back('automation_actuators')
    title = 'Add Actuator for ' + controller.Name()
    param['action'] = 'Add'
    if request.method == 'POST':
        if 'action' in request.form:
            del config_dict['action']
            controller.ValidateNewActuator(config_dict, error_dict)
            if ErrorFound(error_dict):
                return render_template('automation-edit-actuator.html', title=title, controller=controller, next=next, error=error_dict, param=param)
            actuator = automation.AddActuator(controller, config_dict)
            flash('Added Actuator: ' + actuator.Names())
        return redirect_back('automation_actuators')
    param['Controller'] = controller.Name()
    param['Order'] = automation.NextOrder()
    return render_template('automation-edit-actuator.html', title=title, controller=controller, next=next, error=error_dict, param=param)

@app.route('/automation/actuators/edit/<actuator_name>', methods=['POST', 'GET'])
def automation_edit_actuator(actuator_name):
    if debug: print 'automation_edit_actuator'
    next = get_redirect_target()
    actuator = automation.FindActuator(actuator_name)
    if not actuator:
        flash("No actuator named '" + actuator_name + "'")
        return redirect(url_for('automation_actuators'))
    controller = actuator.Controller()
    title='Edit Actuator - ' + actuator.Name()
    error_dict = DefaultDict()
    if request.method == 'POST':
        if 'action' in request.form:
            config_dict = StrippedCopy(request.form)
            param = DefaultDict(config_dict)
            del config_dict['action']
            actuator.Validate(config_dict, error_dict)
            if ErrorFound(error_dict):
                return render_template('automation-edit-actuator.html', title=title, controller=controller, next=next, param=param, error=error_dict)
            automation.EditActuator(actuator, config_dict)
            flash('Updated Actuator ' + actuator.Name())
        return redirect(url_for('automation_actuators'))
    param = actuator.GetConfigDict()
    param['action'] = 'Update'
    return render_template('automation-edit-actuator.html', title=title, controller=controller, next=next, param=param, error=error_dict)

if __name__ == '__main__':
    AutomationConfig.SetConfigFilename(CONFIG_FILE)
    AutomationConfig.Read()
    app.run(host='0.0.0.0', debug=True)
