import os
from flask import Flask, render_template, jsonify
from .models import ModelManager
import json
import re

BASE_DIR = os.path.dirname(__file__)

model_settings = {
    'ADNI': 'ADNI',
    'DELCODE': 'DELCODE'
}
model_manager = ModelManager(model_settings)


def create_app(test_config: any =None) -> Flask:
    """Entry point for flask app.

    Returns:
        Flask: Flask app
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from . import ajax
    app.register_blueprint(ajax.bp)


    @app.template_filter('clean_id')
    def clean_id(s):
        if not s: return ""
        s = str(s).strip()
        s = re.sub(r'[^a-zA-Z0-9]', '_', s)
        return s.strip('_').lower()


    # routes
    @app.route("/")
    def home() -> str:
        """Base page route

        Returns:
            str: rendered html template
        """
        

        with open(f'{BASE_DIR}/data/categories.json', 'r', encoding='utf-8') as file:
            category_list = json.load(file)
        for model in model_manager.models:
            print(f'"{model.get_name()}": ' + '{')
            for node in sorted(model.get_nodes()):
                for state in model.get_state_names(node):
                    if state not in category_list[model.get_name()][node]:
                        print(node, state)
                # print(f'"{node}": {sorted(model.get_state_names(node))},')


        with open(f'{BASE_DIR}/data/criteria_settings.json', 'r', encoding='utf-8') as file:
            criteria = json.load(file)

        with open(f'{BASE_DIR}/data/cards.json', 'r', encoding='utf-8') as file:
            cards = json.load(file)
        network_structure = {}
        for model in model_manager.models:
            network_structure[model.get_name()] = model.get_network_structure()

        return render_template('index.html', criteria=criteria,
                               cases=list(range(1, 6)),
                               network=network_structure, category_list=category_list, cards=cards)

    return app