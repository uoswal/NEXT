from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask.ext.restful import abort, Api, Resource
from next.api import api_util
from next.api.keychain import KeyChain

keychain = KeyChain()

# Initialize flask.Flask application and restful.api objects
api = Blueprint('api', __name__)
api_interface = api_util.NextBackendApi(api)

# Format: Resource Class, get url, post url (when applicable)
from next.api.resources.experiment import Experiment
api_interface.add_resource(Experiment,
                           '/experiment',
                           '/experiment/<string:exp_uid>/<string:exp_key>')

# TODO: delete the API endpoints for
from next.api.app_handler import AppHandler
api_interface.add_resource(AppHandler,
                           '/experiment/<string:exp_uid>/<string:exp_key>/custom/function_name',
                           '/experiment/custom/<string:function_name>')

from next.api.resources.get_query import getQuery
api_interface.add_resource(getQuery,
                           '/experiment/<string:exp_uid>/<string:exp_key>/getQuery',
                           '/experiment/getQuery')

from next.api.resources.process_answer import processAnswer
api_interface.add_resource(processAnswer, '/experiment/processAnswer')

from next.api.resources.stats import Stats
api_interface.add_resource(Stats, '/experiment/stats')

from next.api.resources.predict import Predict
api_interface.add_resource(Predict, '/experiment/predict')

from next.api.resources.about import About
api_interface.add_resource(About, '/about', '/about/<string:app_id>')

from next.api.resources.logs import Logs
api_interface.add_resource(Logs,
                           '/experiment/<string:exp_uid>/<string:exp_key>/logs',
                           '/experiment/<string:exp_uid>/<string:exp_key>/logs/<log_type>')

from next.api.resources.participants import Participants
api_interface.add_resource(Participants,
                           '/experiment/<string:exp_uid>/<string:exp_key>/participants')

from next.api.resources.targets import Targets

api_interface.add_resource(Targets,
                           '/targets/<string:exp_uid>/<string:exp_key>',
                           '/targets/createtargetmapping')

from next.api.resources.widgets import Widgets
api_interface.add_resource(Widgets,'/widgets/getwidget')

from next.api.resources.widgets import WidgetKeys
api_interface.add_resource(WidgetKeys,'/widgets/temp-widget-keys')

from next.api.resources.database import DatabaseBackup, DatabaseRestore
api_interface.add_resource(DatabaseBackup,'/database/databasebackup')
api_interface.add_resource(DatabaseRestore,'/database/databaserestore')
