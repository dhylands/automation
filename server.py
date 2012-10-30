from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask import flash
from flask import url_for
from redirect_back import get_redirect_target, redirect_back
import jinja2

import collections

import automation

import logging
from DefaultDict import DefaultDict, ErrorFound

debug = True

app = Flask(__name__)
app.secret_key = 'automation secret'

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
    param = DefaultDict(request.form)
    controller_type = automation.FindControllerType(controller_type_name)
    if not controller_type:
        flash("No controller type named '" + controller_type_name + "'", 'error')
        return redirect(url_for('automation_controllers'))
    if request.method == 'POST':
        if 'add' in request.form:
            del param['add']
            controller_type.ValidateNewController(param, error_dict)
            if ErrorFound(error_dict):
                return render_template('automation-add-controller.html', controller_type=controller_type, error=error_dict, param=param)
            param['type'] = controller_type_name
            automation.AddController(param)
            flash('Added Controller: ' + param['name'])
        return redirect(url_for('automation_controllers'))
    param['Type'] = controller_type_name
    return render_template('automation-add-controller.html', controller_type=controller_type, error=error_dict, param=param)

@app.route('/automation/controllers/edit/<controller_name>', methods=['POST', 'GET'])
def automation_edit_controller(controller_name):
    if debug: print 'automation_edit_controller'
    next = get_redirect_target()
    controller = automation.FindController(controller_name)
    if not controller:
        flash("No controller named '" + controller_name + "'")
        return redirect(url_for('automation_controllers'))
    if request.method == 'POST':
        print 'method == POST'
        if 'save' in request.form:
            controller_name = request.form['Name']
            config_dict = request.form.copy()
            del config_dict['save']
            automation.EditController(controller, config_dict)
            flash('Updated Controller ' + controller_name)
        return redirect(url_for('automation_controllers'))
        #return redirect_back('automation_controllers')
    return render_template('automation-edit-controller.html', controller=controller, next=next)

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
    param = DefaultDict(request.form)
    controller = automation.FindController(controller_name)
    if not controller:
        flash('Unable to find controller named ' + controller_name)
        return redirect_back('automation_actuators')
    if request.method == 'POST':
        if 'add' in request.form:
            print "param =", param
            flash(request.form)
            del param['add']
            param['Names'] = param['Names'].split(", ")
            controller.ValidateNewActuator(param, error_dict)
            if ErrorFound(error_dict):
                return render_template('automation-add-actuator.html', controller=controller, next=next, error=error_dict, param=param)
            automation.AddActuator(controller, param)
            flash('Added Actuator: ' + ' '.join(param['names']))
        return redirect_back('automation_actuators')
    param['Controller'] = controller.Name()
    param['Order'] = automation.NextOrder()
    return render_template('automation-add-actuator.html', controller=controller, next=next, error=error_dict, param=param)

@app.route('/automation/actuators/edit/<actuator_name>', methods=['POST', 'GET'])
def automation_edit_actuator(actuator_name):
    if debug: print 'automation_edit_actuator'
    next = get_redirect_target()
    actuator = automation.FindActuator(actuator_name)
    if not actuator:
        flash("No actuator named '" + actuator_name + "'")
        return redirect(url_for('automation_actuators'))
    print 'actuator non-NULL'
    if request.method == 'POST':
        print 'method == POST'
        if 'save' in request.form:
            actuator_name = request.form['Name']
            config_dict = request.form.copy()
            del config_dict['save']
            automation.EditActuator(actuator, config_dict)
            flash('Updated Actuator ' + actuator_name)
        return redirect(url_for('automation_actuators'))
    print 'not POST'
    return render_template('automation-edit-actuator.html', actuator=actuator, next=next)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
