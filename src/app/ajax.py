from flask import Blueprint, jsonify, request, Response
from . import model_manager
import time
import copy

bp = Blueprint('ajax', __name__, url_prefix='/ajax')


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/<model_name>', methods=('GET', 'POST'))
def index(model_name = None) -> str | Response:
    """Ajax route for starting a inference process and retrieving the inference result.

    Returns:
        str | Response: Returns inference results if accessed via POST, else it returns a string.
    """
    if request.method == 'POST':
        request_data = request.get_json()
        evidence = request_data['evidence']
        print('request_data', request_data)
        print('Evidence 0', evidence)

        if request_data['replace_evidence']:
            replaced_evidence = replace_evidence(copy.deepcopy(evidence), request_data['replace_evidence'])
            print('Evidence 1', evidence)

        ig_results = {}
        if 'case0' in evidence.keys():
            start_time = time.time()
            if request_data['replace_evidence']:
                for model in model_manager.models:
                    if model_name == model.get_name():
                        ig_results[model.get_name()] = model.get_information_gain_of_all_nodes(replaced_evidence['case0'].copy())
                        print('Evidence 2', replaced_evidence['case0'].copy())
                    else:
                        print('Evidence 3', evidence)
                        ig_results[model.get_name()] = model.get_information_gain_of_all_nodes(evidence['case0'].copy())           
            else:
                ig_results = model_manager.get_information_gain(evidence['case0'].copy())
            print(f'IG: {time.time()-start_time}')
        start_time = time.time()
        print(model_name)
        results = {}
        if request_data['replace_evidence']:
            for case in evidence.keys():
                results[case] = {}
                for model in model_manager.models:
                    print(case, model.get_name())
                    if model_name == model.get_name():
                        result = model.get_inference(replaced_evidence[case])
                    else:
                        result = model.get_inference(evidence[case].copy())        
                    results[case][model.get_name()] = result
        else:
            results = model_manager.get_inference(evidence)
        answer= {
            'results': results,
            'information_gain': ig_results
            }
        print(f'Inference: {time.time()-start_time}')

        print('Done')
        return jsonify(answer)
    return 'Nur POST-Anfrage möglich'



def replace_evidence(evidence, replace_evidence):
    case_id = replace_evidence['case_id']
    feature_name = replace_evidence['feature']
    feature_value = replace_evidence['value']
    evidence[case_id][feature_name] = feature_value
    return evidence