import yaml

class ConfigLoader:
    """Class for loading yaml files for the configuration of bayesian network models

    """
    def __init__(self, config_file: str):
        """Initializes the ConfigLoader class.

        Args:
            config_file (str): path to config file. Currently only yaml-files are supported.
        """
        self.config_file = config_file
        self.loaded_config_data = {}
        self._load_yaml_config()


    def _load_yaml_config(self) -> None:
        """Reads the initialized config file and stores it's content. 
        """
        with open(self.config_file, 'r') as file:
            self.loaded_config_data = yaml.safe_load(file)

    
    def get_config_data(self) -> dict:
        """Returns the config data.

        Returns:
            dict: config data
        """
        return self.loaded_config_data
    
    
    def get_file(self) -> str:
        """Returns path to file.

        Returns:
            str: Path to file.
        """
        return self.loaded_config_data['file_name']
    
    
    def get_table_cols(self, diagnosis_nodes: bool = True, data_nodes: bool =  True) -> list[str]:
        """Returns the column names of the given table.

        Args:
            diagnosis_nodes (bool, optional): If True: columns of diagnosis node get returned. Defaults to True.
            data_nodes (bool, optional): If True: columns of data node get returned. Defaults to True.

        Returns:
            list[str]: List of column names
        """
        cols = []
        
        if diagnosis_nodes:
            cols += [key for key in self.loaded_config_data['diagnosis_nodes'].keys()]
        if data_nodes:
            cols += [key for key in self.loaded_config_data['data_nodes'].keys()]
        return cols
    

    def get_node_names(self, diagnosis_nodes: bool = True, data_nodes: bool =  True) -> list[str]:
        """Returns the node names.

        Args:
            diagnosis_nodes (bool, optional): If True: node names of diagnosis node get returned. Defaults to True.
            data_nodes (bool, optional): If True: node names of data node get returned. Defaults to True.

        Returns:
            list[str]: List of node names
        """
        cols = []
        if not self.loaded_config_data['rename_nodes']:
            return self.get_table_cols()
            
        if diagnosis_nodes:
            cols += [value for value in self.loaded_config_data['diagnosis_nodes'].values()]
        if data_nodes:
            cols += [value for value in self.loaded_config_data['data_nodes'].values()]
        return cols
    

    def get_mapped_cols_and_node_names(self) -> dict[str]:
        if not self.loaded_config_data['rename_nodes']:
            return False
        mapping = {}
        for key, node_name in self.loaded_config_data['diagnosis_nodes'].items():
            mapping[key] = node_name
        
        for key, node_name in self.loaded_config_data['data_nodes'].items():
            mapping[key] = node_name
        return mapping

    
    def drop_nan(self) -> bool:
        """Returns whether Nan values should be dropped.

        Returns:
            bool: Returns whether Nan values should be dropped.
        """
        return self.loaded_config_data['drop_nan']
    

    def get_edges_file(self) -> str:
        """Returns the path to the file with the definition of the edges.

        Returns:
            str: Path to the edges definition file.
        """
        return self.loaded_config_data['edges']['file_name']
    

    def create_edge_file(self) -> bool:
        """Returns whether a new edges definition file should be created.

        Returns:
            bool: Returns whether a new edges definition file should be created.
        """
        return self.loaded_config_data['edges']['create_file']


    def get_save_path_and_file_type(self) -> tuple[str, str]:
        """Return a path and file type to save a model.

        Returns:
            tuple[str, str]: Tuple of file path and file type
        """
        return self.loaded_config_data['save_model_path'], self.loaded_config_data['save_model_path'].split('.')[-1]
    

    def get_save_plot_path(self) -> str:
        """Returns the path for saving a graph plot.

        Returns:
            str: Path to file location
        """
        return self.loaded_config_data['save_plot_path']