from model_building.ConfigLoader import ConfigLoader
from model_building.DataLoader import DataLoader
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
import pandas as pd
import joblib
import numpy as np


class ModelBuilder:
    def __init__(self, config_file: str, meta_data: bool = False, seed = 42):
        np.random.seed(seed)
        self.config_loader = ConfigLoader(config_file)
        self.DataLoader = DataLoader(self.config_loader, meta_data=meta_data)
        self.df = self.DataLoader.get_df()
        self.edges_file = self.config_loader.get_edges_file()
        self.edges = []
        self.load_edges()
        self.build_model()
        self.fit_model()
        self.save_model()
        self.plot_graph()


    def load_edges(self):
        if self.config_loader.create_edge_file():
            self.create_edges_file()
            print('***************************************************************************************')
            print(f'Please edit \"{self.edges_file}\".')
            print('The rows defines the start nodes and the columns the end nodes. Place a X or x in the correspondig cells.')
            print('You can use for example Excel to modify the file. CAVE: the file type must be \".csv\"!')
            input(f'Press ENTER if you\'re declared all edges in \"{self.edges_file}\"')
        edges_df = pd.read_csv(self.edges_file, index_col=0)

        self.edges = []
        for _, start in edges_df.iterrows():
            start.dropna(inplace=True)
            if start.empty:
                continue
            self.edges += [(start.name, target_node) for target_node in start.index]
            

    def create_edges_file(self) -> None:
        nodes = self.config_loader.get_node_names()
        pd.DataFrame(columns=nodes, index=nodes).to_csv(self.edges_file)


    def get_state_names(self):
        state_names = {}
        for col in self.df.columns:                     
            state_names[col] = list(self.df[col].dropna().unique())
        return state_names


    def build_model(self) -> None:
        self.model = DiscreteBayesianNetwork(self.edges)


    def fit_model(self) -> None:
        state_names = self.get_state_names()
        self.model.fit(self.df[self.config_loader.get_node_names()], estimator=BayesianEstimator, state_names=state_names)


    def save_model(self) -> None:
        file_path, file_type = self.config_loader.get_save_path_and_file_type()
        joblib.dump(self.model, file_path)


    def get_model(self) -> DiscreteBayesianNetwork:
        return self.model
    
    
    def plot_graph(self) -> None:
        model_graphviz = self.model.to_graphviz()
        path, file_type = self.config_loader.get_save_plot_path().split('.')
        model_graphviz.draw(f'{path}_dot.{file_type}', prog="dot")
        model_graphviz.draw(f'{path}_fdp.{file_type}', prog="fdp")