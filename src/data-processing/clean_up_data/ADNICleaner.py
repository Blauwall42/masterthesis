import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from clean_up_data.CustomDictTypes import ColumnSettings


class ADNICleaner:
    columns: dict[str, ColumnSettings] = {
        'PTID': {'replace': False, 'bin': False, 'round': False},
        'ABETA': {'bin': [0, 500, 600, 2000], 'replace': {'<200': 199, '>1700': 1701}, 'round': {'digits': 1, 'to_half': False}},
        'ADAS11': {'bin': 5, 'replace': False, 'round': {'digits': 2, 'to_half': False}},
        'ADAS13': {'bin': 5, 'replace': False, 'round': {'digits': 2, 'to_half': False}},
        'AGE': {'bin': 5, 'replace': False, 'round': {'digits': 1, 'to_half': False}},
        'APOE4': {'bin': [0, 0.5, 1.5, 3.5], 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'AV45': {'bin': 5, 'replace': False, 'round': {'digits': 4, 'to_half': False}},
        'CDRSB': {'bin': [0, 0.5, 2.5, 4, np.inf], 'replace': False, 'round': {'to_half': True}},
        'DX': {'bin': False, 'replace': {'Dementia': 'AD'}, 'round': False},
        'EcogPtTotal': {'bin': [1, 1.5, 2, 2.5, 3, 3.5], 'replace': False, 'round': {'digits': 5, 'to_half': False}},
        'EcogSPTotal': {'bin': [1, 1.5, 2, 2.5, 3, 3.5, 4], 'replace': False, 'round': {'digits': 5, 'to_half': False}},
        'Entorhinal': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'FAQ': {'bin': [0, 8, 30], 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'Fusiform': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'Hippocampus': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'ICV': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'LDELTOTAL': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'MidTemp': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'MMSE': {'bin': [19, 26, 30], 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'MOCA': {'bin': [9, 17, 25, 30], 'replace': False, 'round': {'digits': 1, 'to_half': False}},
        'PTAU': {'bin': 5, 'replace': {'<8': 7, '>120': 121}, 'round': {'digits': 2, 'to_half': False}},
        'PTGENDER': {'replace': {'Male': 'Männlich', 'Female': 'Weiblich'}, 'bin': False, 'round': False},
        'PTMARRY': {'replace': {'Married': 'verheiratet oder in Partnerschaft', 'Divorced': 'geschieden oder getrennt lebend', 'Widowed': 'verwitwet', 'Never married': 'ledig', 'Unknown': pd.NA},
                    'bin': False, 'round': False},
        'PTEDUCAT': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'RAVLT_forgetting': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'RAVLT_immediate': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'RAVLT_learning': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'TAU': {'bin': 5, 'replace': {'<80': 79, '>1300': 1301}, 'round': {'digits': 2, 'to_half': False}},
        'TRABSCOR': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'Ventricles': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
        'WholeBrain': {'bin': 5, 'replace': False, 'round': {'digits': 0, 'to_half': False}},
    }


    ratio_columns = {
        'Ventricles_ICV': {'dividend': 'Ventricles', 'divisor': 'ICV', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Hippocampus_ICV': {'dividend': 'Hippocampus', 'divisor': 'ICV', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Entorhinal_ICV': {'dividend': 'Entorhinal', 'divisor': 'ICV', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Fusiform_ICV': {'dividend': 'Fusiform', 'divisor': 'ICV', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'MidTemp_ICV': {'dividend': 'MidTemp', 'divisor': 'ICV', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
    }

    
    def __init__(self, adni_merge_file: str, clean_file_path: str, add_ratios: bool = True, bin_data: bool = False):
        self.adni_merge_file = adni_merge_file
        self.clean_file_path = clean_file_path
        self.df: pd.DataFrame = None
        self.df_train: pd.DataFrame = None
        self.df_test: pd.DataFrame = None
        self.load_data()
        self.replace_categories()
        if add_ratios:
            self.add_ratios()
        self.df_nans = self.df[self.df.isna().any(axis=1)]
        self.df.dropna(inplace=True)
        self.split_data()
        if bin_data:
            self.bin_data()


    def load_data(self) -> None:
        """Loads the data from the self.file_name path and filters for the baseline visit.
        Additionally NAN values in the DX columns gets rejected and not in self.columns declared
        columns gets removed.
        """
        df = pd.read_csv(self.adni_merge_file, low_memory=False)
        df = df.loc[(df['VISCODE'] == 'bl') & pd.notna(df['DX'])]
        self.df = df[self.columns.keys()]


    def add_ratios(self) -> None:
        """Adds in self.ratio_columns predefined to the self.df (pd.DataFrame).
        """
        for key, value in self.ratio_columns.items():
            dividend = value['dividend']
            divisor = value['divisor']
            self.df[key] = (self.df[dividend]/self.df[divisor])
            self.columns[key] = {'bin': value['bin'], 'replace': value['replace'], 'round': value['round']}
            if value['replace']:
                self.df[key].replace(value['replace'])


    def impute(self, n: int = 5) -> None:
        """Imputes NAN values in the training pd.Dataframe.
        Rows with NAN values in nominal columns gets ignored.
        Nominal data gets encoded. Then the data gets scaled and NAN values gets imputed.

        Args:
            n (int, optional): Amount of neighbors for KNNImputer. Defaults to 5.
        """

        dont_impute_cols = ['DX', 'PTGENDER', 'PTMARRY']
        impute_cols = [col for col in self.columns.keys() if col not in dont_impute_cols]
        mask = self.df_train[dont_impute_cols].notna().all(axis=1)
        df_numeric = self.df_train.loc[mask, impute_cols]
        df_nominal = self.df_train.loc[mask, dont_impute_cols]

        ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        df_nominal_encoded = ohe.fit_transform(df_nominal)
        df_nominal_encoded = pd.DataFrame(df_nominal_encoded, columns=ohe.get_feature_names_out(),
                                          index=df_numeric.index)
        df_combined = pd.concat([df_numeric, df_nominal_encoded], axis=1)

        scaler = MinMaxScaler()
        imputer = KNNImputer(n_neighbors=5)

        scaled_data = scaler.fit_transform(df_combined)
        imputed_scaled_data = imputer.fit_transform(scaled_data)
        imputed_original_scale = scaler.inverse_transform(imputed_scaled_data)
        df_imputed = pd.DataFrame(
            imputed_original_scale, 
            columns=df_combined.columns, 
            index=df_combined.index
        )
        df_imputed_numeric = df_imputed[impute_cols]

        for col in [col for col in self.columns.keys() if self.columns[col]['round']]:
            if self.columns[col]['round']['to_half']:
                df_imputed_numeric.loc[:, col] = (df_imputed_numeric[col] * 2).round(0) / 2
            else:
                round_digits = self.columns[col]['round']['digits']
                df_imputed_numeric.loc[:, col] = df_imputed_numeric[col].round(round_digits)
            
        self.df_train.loc[mask, impute_cols] = df_imputed_numeric


    def replace_categories(self) -> None:
        """Replaces selected values within the main pd.Dataframe.
        """
        for col, replace_dict in [(key, value['replace']) for key, value in self.columns.items() if value['replace']]:
            if col in ['DX', 'PTGENDER', 'PTMARRY']:
                self.df[col] = self.df[col].replace(replace_dict)
            else:
                self.df[col] = self.df[col].replace(replace_dict).astype(float)


    def split_data(self) -> None:
        """Spilts data into training and testing data.
        """
        self.df_train, self.df_test = train_test_split(self.df, test_size=0.2, random_state=42)
        self.df_train.reset_index(inplace=True, drop=True)
        self.df_test.reset_index(inplace=True, drop=True)


    def save_data(self, train: bool = True, test: bool = True, whole: bool = False, drop_nans = False, nan_df: bool = False) -> None:
        """Saves selected pd.Dataframes.

        Args:
            train (bool, optional): Save trainings data. Defaults to True.
            test (bool, optional): Save testing data. Defaults to True.
            whole (bool, optional): Save whole data. Defaults to False.
        """
        if train:
            if drop_nans:
                self.df_train.dropna().to_csv(f'{self.clean_file_path}/adni_train.csv', index=False)
            else:
                self.df_train.to_csv(f'{self.clean_file_path}/adni_train.csv')
        if test:
            if drop_nans:
                self.df_test.dropna().to_csv(f'{self.clean_file_path}/adni_test.csv', index=False)
            else:
                self.df_test.to_csv(f'{self.clean_file_path}/adni_test.csv', index=False)
        if whole:
            if drop_nans:
                self.df.dropna().to_csv(f'{self.clean_file_path}/adni.csv', index=False)
            else:
                self.df.to_csv(f'{self.clean_file_path}/adni.csv', index=False)
        if nan_df:
            self.df_nans.to_csv(f'{self.clean_file_path}/adni_nan.csv', index=False)

    
    def get_statistics(self):
        print('whole')
        print(self.df.describe())

        print('training')
        print(self.df_train.describe())
    
    
    def get_train_df(self) -> pd.DataFrame:
        """Returns training pd.Dataframe.

        Returns:
            pd.DataFrame: Training data
        """
        return self.df_train
    
    
    def get_test_df(self) -> pd.DataFrame:
        """Returns testing pd.Dataframe.

        Returns:
            pd.DataFrame: Testing data
        """
        return self.df_test
        
    

    def bin_data(self) -> None:
        for col, settings in self.columns.items():
            bins = settings['bin']

            if not bins:
                continue
            if not isinstance(bins, list):
                _, bins = pd.qcut(self.df_train[col], q=bins, retbins=True)
            bins[0] = -np.inf
            bins[-1] = np.inf
            self.df_train[f'{col}_bin'] = pd.cut(self.df_train[col],  bins=bins, include_lowest=True)



if __name__ == '__main__':
    adni_merge = '40_Realisation/000_raw_data/ADNI/ADNIMERGE.csv'
    adni_Cleaner = ADNICleaner(adni_merge, '.', impute=False, bin_data=True)
    adni_Cleaner.save_data(True, False, drop_nans=True)
