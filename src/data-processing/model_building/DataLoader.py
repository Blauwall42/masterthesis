from model_building.ConfigLoader import ConfigLoader
import pandas as pd


class DataLoader:
    def __init__(self, config_loader: ConfigLoader, meta_data: bool = True):
        """Initializes the DataLoader class.

        Args:
            config_loader (ConfigLoader): path to config file
        """
        self.config_loader = config_loader
        self.meta_data = meta_data
        self.df: pd.DataFrame
        self._load_df()

    
    def _load_df(self) -> None:
        """Loads data defined in the config file.

        Returns:
            pd.DataFrame: loaded data
        """
        file = self.config_loader.get_file()
        table_cols = self.config_loader.get_table_cols()
        self.df = pd.read_csv(file, usecols=table_cols)

        self.rename_nodes()
        self.df.to_csv('with_nan.csv')
        if self.config_loader.drop_nan():
            self.df = self.df.dropna().reset_index(drop=True)
            self.df.to_csv('without_nan.csv')
    

    def get_df(self) -> pd.DataFrame:
        """Returns the loaded dataset

        Returns:
            pd.DataFrame: Loaded dataset
        """
        return self.df
    
    
    def rename_nodes(self):
        """Renames columns
        """
        self.df.rename(columns=self.config_loader.get_mapped_cols_and_node_names(), inplace=True)