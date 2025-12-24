import joblib
from pgmpy.inference import VariableElimination, ApproxInference
import os
from pgmpy.models import DiscreteBayesianNetwork
import pandas as pd
import json
import numpy as np
from scipy.stats import entropy
import math
import time


class ModelManager:
    """Class for managing all bayesian network models
    """
    def __init__(self, models: dict[str, str]):
        """Initializes class
        """
        BASE_DIR = os.path.dirname(__file__)
        self.models: list[Model] = []
        for (key, filename) in models.items():
            self.models.append(Model(key, f'{BASE_DIR}/models/{filename}.pkl'))
        self.all_features = []
        self.load_all_features()


    def load_all_features(self) -> None:
        """Loads all (unique) features/nodes of all registered models.
        """
        for model in self.models:
            for feature in model.get_nodes():
                if feature in self.all_features:
                    continue
                self.all_features.append(feature)


    def get_all_features(self) -> list[str]:
        """Returns all feature/node names.

        Returns:
            list[str]: All features/node names.
        """
        return self.all_features
    

    def get_inference(self, evidence: dict[str, dict]) -> dict[str, dict]:
        results = {}
        for case in evidence.keys():
            results[case] = {}
            for model in self.models:
                results[case][model.get_name()] = model.get_inference(evidence[case])
        return results
    
    
    def get_network_structures(self) -> dict[str, dict]:
        """Returns the structure of all register bayesian networks.

        Returns:
            dict[str, dict]: Bayesian network structures
        """
        structures = {}
        for model in self.models:
            structures[model.get_name()] = model.get_network_structure()
        return structures
    
    
    def get_information_gain(self, evidence: dict, target_node: str = 'Diagnose'):
        ig = {}
        for model in self.models:
            start_time = time.time()
            ig[model.get_name()] = model.get_information_gain_of_all_nodes(evidence.copy(), target_node)
            print(f'{model.get_name()}: {time.time() - start_time}')
        return ig


class Model:
    """Class managing a single bayesian network model.
    """
    def __init__(self, name: str, path: str):
        """Initializes a model.

        Args:
            name (str): Name of model
            path (str): Path to stored model (saved with joblib/as '.pkl')
        """
        self.name = name
        self.path = path
        self.model: DiscreteBayesianNetwork = joblib.load(path)
        self.infer = VariableElimination(self.model)
        self.approx_infer = ApproxInference(self.model)
        self.intervals = {}
        self.load_all_intervals()


    def __str__(self) -> str:
        """Returns a string which represents the model.

        Returns:
            str: Model representation
        """
        return f'{self.name}: {self.path}'
    
    
    def get_nodes(self) -> list[str]:
        """Returns all nodes of the model.

        Returns:
            list[str]: Model nodes
        """
        return list(self.model.nodes())
    

    def get_state_names(self, node: str) -> list[str]:
        return self.model.get_cpds(node).state_names[node]
    
    
    def convert_numeric_value_to_interval(self, node: str, value: int | float) -> str|None:
        """Converts a numeric value to the associated interval.

        Args:
            node (str): Node with intervals
            value (int | float): Number which should be converted

        Returns:
            str|None: Returns the pandas.Interval as string. If no interval fits it returns None
        """
        for interval in self.intervals[node]:
            if value in interval:
                return str(interval)
        return None
    # ToDo: add option for nearest interval    
    # if value <= self.intervals[node][0].left:
    #     return str(self.intervals[node][0])
    # if value >= self.intervals[node][-1].right:
    #     return str(self.intervals[node][-1])
    

    def load_all_intervals(self) -> None:
        """Loads all intervals of the model as pandas.Interval.
        """
        for node in self.get_nodes():
            self.intervals[node] = []
            for state_name in self.get_state_names(node):
                if '(' not in str(state_name) and '[' not in str(state_name):
                    break
                self.intervals[node].append(string_to_pandas_interval(state_name))


    def get_intervals(self) -> dict[str, list[pd.Interval]]:
        """Returns all interval of the models as pandas.Interval.

        Returns:
            dict[str, list[pd.Interval]]: All intervals structured by node
        """
        return self.intervals


    def get_inference(self, evidence: dict, target_node: None | str = None) -> dict[str, dict]:
        """Returns the probabilities of all nodes with respect to given evidence.

        Args:
            evidence (dict): Evidence for prediction

        Returns:
            dict[str, dict]: Inference results grouped by nodes
        """
        # start_time = time.time()
        evidence_filtered = {key: value for key, value in evidence.items() if key in self.get_nodes()}
        
        infer_nodes = [node for node in self.get_nodes() if node not in evidence_filtered.keys()]
        
        for node in [node for node in self.intervals.keys() if node not in infer_nodes and self.intervals[node] != []]:
            if ', ' in evidence[node]:
                continue
            interval = self.convert_numeric_value_to_interval(node, float(evidence[node]))
            if interval is None:
                evidence_filtered.pop(node)
            else:
                evidence_filtered[node] = self.convert_numeric_value_to_interval(node, float(evidence[node]))

        # print(f'Evidence clean up: {time.time()-start_time}')
        if target_node is not None:
            infer_nodes = [target_node]

        infer_results = {}
        for node in infer_nodes:
            result = self.infer.query(variables=[node], evidence=evidence_filtered)
            if target_node is not None:
                return result
            infer_results[node] = dict(zip(result.state_names[node], result.values.round(4)*100))
        # print(f'Inference: {time.time()-start_time}')
        
        for key, value in evidence_filtered.items():
            infer_results[key] = {value: 100}

        return infer_results
    
    def filter_evidence(self, evidence: dict, ignore_nodes: list[str]):
        evidence_filtered = {key: value for key, value in evidence.items() if key in self.get_nodes()}
        for node in [node for node in self.intervals.keys() if node in evidence.keys() and self.intervals[node] != []]:
            if ', ' in evidence[node]:
                continue
            interval = self.convert_numeric_value_to_interval(node, float(evidence[node]))
            if interval is None:
                evidence_filtered.pop(node)
            else:
                evidence_filtered[node] = self.convert_numeric_value_to_interval(node, float(evidence[node]))
        return evidence_filtered


    def get_single_inference(self, filtered_evidence: dict, infer_node: str) -> dict[str, dict]:
        """Returns the probabilities of all nodes with respect to given evidence.

        Args:
            evidence (dict): Evidence for prediction

        Returns:
            dict[str, dict]: Inference results grouped by nodes
        """

        result = self.infer.query(variables=[infer_node], evidence=filtered_evidence)
        return result
    
    
    def get_name(self) -> str:
        """Returns the name of the model.

        Returns:
            str: Model name
        """
        return self.name
    
    
    def get_network_structure(self) -> dict[str, list[dict]]:
        """Returns the structure of the bayesian network.

        Returns:
            dict[str, list[dict]]: Structure of the bayesian model grouped by nodes and edges/links
        """
        BASE_DIR = os.path.dirname(__file__)
        with open(f'{BASE_DIR}/data/criteria_settings.json') as f:
            additional_network_data = json.load(f)
        
        return {
            'nodes': [{"id": node, 'group_name': get_group_name(node, additional_network_data)} for node in self.model.nodes()],
            'links': [{"source": u, "target": v} for u, v in self.model.edges()]
        }
    

    def get_information_gain_of_all_nodes(self, evidence: dict, target_node: str = 'Diagnose'):
        filtered_evidence = self.filter_evidence(evidence, [])
        ig = {}
        base_prob = self.get_single_inference(filtered_evidence, target_node)
        base_entropy = entropy(base_prob.values, base=2)
        for node in [node for node in self.get_nodes()]:
            if node == target_node or node in filtered_evidence:
                ig[node] = 0
                continue
            ig[node] = self.get_information_gain_of_node(filtered_evidence, node, base_entropy, target_node)
        return ig


    def get_information_gain_of_node(self, filtered_evidence: dict, node: str, base_entropy, target_node: str = 'Diagnose'):
        if node in filtered_evidence.keys(): return 0
        
        node_prob = self.get_single_inference(filtered_evidence, node)

        expected_conditional_entropy = 0
        for state_index, state_prob in enumerate(node_prob.values):
            if state_prob < 0.00001:
                continue
            hypothetical_evidence = filtered_evidence.copy()
            hypothetical_evidence[node] = self.get_state_names(node)[state_index]
            posterior = self.get_single_inference(hypothetical_evidence, target_node)
            
            cond_entropy = entropy(posterior.values, base=2)
            if math.isnan(cond_entropy) and state_prob == 0:
                expected_conditional_entropy +=  0
            else:
                expected_conditional_entropy += state_prob * cond_entropy
        return base_entropy - expected_conditional_entropy
    

def get_group_name(feature_name: str, network_data):
    if feature_name == 'Diagnose':
        return 'Diagnose'
    for group in network_data:
        for feature in group.get("features", []):
            if feature.get("name") == feature_name:
                return group.get("group_name")

 

def string_to_pandas_interval(interval: str) -> pd.Interval:
    """Converts a interval string to a pandas.Interval

    Args:
        s (str): Interval as string

    Returns:
        pd.Interval: Interval as pandas.Interval
    """
    interval = interval.strip()
    left_bracket = interval[0]
    right_bracket = interval[-1]

    nums = interval[1:-1].split(",")
    if nums[0] == '-inf':
        left = -np.inf
    else:
        left = float(nums[0].strip())
    if nums[1] == 'inf':
        right = np.inf
    else:
        right = float(nums[1].strip())
    
    if left_bracket == "[" and right_bracket == "]":
        closed = "both"
    elif left_bracket == "(" and right_bracket == ")":
        closed = "neither"
    elif left_bracket == "[" and right_bracket == ")":
        closed = "left"
    elif left_bracket == "(" and right_bracket == "]":
        closed = "right"
    else:
        closed = "right"
    return pd.Interval(left=left, right=right, closed=closed)