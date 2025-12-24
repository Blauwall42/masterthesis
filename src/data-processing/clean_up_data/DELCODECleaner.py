import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
import numpy as np
from typing import TypedDict
import time

class SheetSettings(TypedDict):
    name: str
    cols: None | list[str]
    parse_dates: bool | list[str]

class FileSettings(TypedDict):
    path: str
    sheets: list[SheetSettings]
    


class DELCODECleaner:
    columns = {
        'prmdiag': {'bin': False, 'replace': {0: 'CN', 1: 'CN', 2: 'MCI', 5: 'AD'}, 'round': False},
        # General
        'AGE': {'bin': 5, 'replace': False, 'round': False},
        'bmi': {'bin': [0, 18.4, 24.9, 29.9, 34.9, np.inf], 'replace': False, 'round': False},
        'sex': {'replace': {'m': 'Männlich', 'f': 'Weiblich'}, 'bin': False, 'round': False},

        'hearing': {'bin': False, 'replace': {0: 'Keine Beeinträchtigung', 1: 'Beeinträchtigt',
                                              2: 'Beeinträchtigt', 3: 'Beeinträchtigt'}, 'round': False},
        'vision': {'bin': [0, 0.5, 1.5, np.inf], 'replace': False, 'round': False},
        'visus': {'bin': 4, 'replace': False, 'round': False},
        'living': {'bin': False, 'replace': {1: 'Privathaushalt, allein', 2: 'Zweipersonenhaushalt', 3: 'Mehr-Personenhaushalt',
                                             4: 'Seniorenheim / Pflegeheim',999: np.nan}, 'round': False},
        'maristat': {'replace': {1: 'ledig', 2: 'verheiratet oder in Partnerschaft', 3: 'geschieden oder getrennt lebend',
                                 4: 'geschieden oder getrennt lebend', 5: 'verwitwet', 6: 'verheiratet oder in Partnerschaft',
                                 999: pd.NA}, 'bin': False, 'round': False},
        'graduat': {'bin': False, 'replace': {997: np.nan, 1: 'Kein Schulabschluss - max. 7 Jahre', 2: 'Volksschulabschluss', 
                                              3: 'Hauptschulabschluss', 4: 'Mittlerer Schulabschluss - Mittlere Reife', 
                                              5: 'Anderer Schulabschluss', 6: 'Fachabitur', 7: 'Abitur',
                                              8: 'Anderer Schulabschluss'}, 'round': False},

        # Risks
        'Rauchen': {'bin': False, 'replace': False, 'round': False},
        'Raucherjahre': {'bin': [0, 0.5, 5, 10, 20, 30], 'replace': False, 'round': False},
        'Pack_Years': {'bin': [0, 0.5, 5, 10, 20, 30], 'replace': False, 'round': False},
        'Zigaretten_pro_Tag': {'bin': [0, 0.5, 5, 10, 20, 30], 'replace': False, 'round': False},
        
        'alcconsm': {'bin': False, 'replace': {0: 'Nein', 1: 'Ja'}, 'round': False},
        'alcabuse': {'bin': False, 'replace': {np.nan: 'Nein', 0: 'Nein', 1: 'Ja'}, 'round': False},

        # Neuro
        'vfatot': {'bin': 4, 'replace': False, 'round': False},
        'mmstot': {'bin': [-np.inf, 19, 26, 30], 'replace': False, 'round': False},

        'wmslm1b': {'bin': 4, 'replace': False, 'round': False},
        'wmslm2b': {'bin': 4, 'replace': False, 'round': False},
        'wmsdsf': {'bin': 4, 'replace': False, 'round': False},
        'wmsdsb': {'bin': 4, 'replace': False, 'round': False},
        'wmstot': {'bin': 4, 'replace': False, 'round': False},

        
        'sdmtot': {'bin': 4, 'replace': False, 'round': False},
        'sdmctot': {'bin': 4, 'replace': False, 'round': False},
        'sdmtpct': {'bin': 4, 'replace': False, 'round': False},
        'sdmir01': {'bin': 4, 'replace': False, 'round': False},
        'sdmir02': {'bin': 4, 'replace': False, 'round': False},

        'clockdw': {'bin': 4, 'replace': False, 'round': False},
        'clockcpy': {'bin': 4, 'replace': False, 'round': False},

        'tmta': {'bin': 4, 'replace': False, 'round': False},
        'tmtb': {'bin': 4, 'replace': False, 'round': False},
        'tmtba': {'bin': 4, 'replace': False, 'round': False},
        
        'cercp': {'bin': [0, 7, 9, 11], 'replace': False, 'round': False},
    

        'AD11SUM': {'bin': 5, 'replace': False, 'round': {'digits': 2, 'to_half': False}},
        'AD13SUM': {'bin': 5, 'replace': False, 'round': {'digits': 2, 'to_half': False}},
    
        'fcsfree': {'bin': 5, 'replace': False, 'round': False},
        'fcscued': {'bin': 5, 'replace': False, 'round': False},
        'fcstot': {'bin': 5, 'replace': False, 'round': False},   

        'mwttot': {'bin': 5, 'replace': False, 'round': False},

        
        # APOE
        'APOE2': {'bin': [0, 0.5, 1.5, 3.5], 'replace': False, 'round': False},
        'APOE3': {'bin': [0, 0.5, 1.5, 3.5], 'replace': False, 'round': False},
        'APOE4': {'bin': [0, 0.5, 1.5, 3.5], 'replace': False, 'round': False},


        # Liquor
        'Abeta38': {'bin': 5, 'replace': False, 'round': False},
        'Abeta40': {'bin': 5, 'replace': False, 'round': False},
        'Abeta42': {'bin': [0, 500, 600, 2000], 'replace': False, 'round': False},
        'totaltau': {'bin': 5, 'replace': False, 'round': False},
        'phosphotau181': {'bin': 5, 'replace': False, 'round': False},
        'ratio_Abeta42_40': {'bin': 5, 'replace': False, 'round': False},
        'ratio_Abeta42_phosphotau181': {'bin': 5, 'replace': False, 'round': False},

        # Imageing
        'Amygdala': {'bin': 5, 'replace': False, 'round': False},
        'CC_total': {'bin': 5, 'replace': False, 'round': False},
        'Lateral-Ventricles': {'bin': 5, 'replace': False, 'round': False},
        'Lateral-Inferior-Ventricles': {'bin': 5, 'replace': False, 'round': False},
        'Ventricles': {'bin': 5, 'replace': False, 'round': False},
        'Entorhinal': {'bin': 5, 'replace': False, 'round': False},
        'MidTemp': {'bin': 5, 'replace': False, 'round': False},
        'Fusiform': {'bin': 5, 'replace': False, 'round': False},
        'Thalamus': {'bin': 5, 'replace': False, 'round': False},
        'Hippocampus': {'bin': 5, 'replace': False, 'round': False},
        'Putamen': {'bin': 5, 'replace': False, 'round': False},
        'Caudate': {'bin': 5, 'replace': False, 'round': False},
        'Pallidum': {'bin': 5, 'replace': False, 'round': False},
        'Accumbens-area': {'bin': 5, 'replace': False, 'round': False},
        'Cerebellum': {'bin': 5, 'replace': False, 'round': False},
        'Brain-Stem': {'bin': 5, 'replace': False, 'round': False},
        'WM-hypointensities': {'bin': 5, 'replace': False, 'round': False},
        'Optic-Chiasm': {'bin': 5, 'replace': False, 'round': False},
        'CortexVol': {'bin': 5, 'replace': False, 'round': False},
        'CerebralWhiteMatterVol': {'bin': 5, 'replace': False, 'round': False},
        'EstimatedTotalIntraCranialVol': {'bin': 5, 'replace': False, 'round': False},
        'BrainSegVolNotVent': {'bin': 5, 'replace': False, 'round': False},
    }

    

    ratio_columns = {
        'Accumbens-area_ICV': {'dividend': 'Accumbens-area', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Amygdala_ICV': {'dividend': 'Amygdala', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Brain-Stem_ICV': {'dividend': 'Brain-Stem', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Caudate_ICV': {'dividend': 'Caudate', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Cerebellum_ICV': {'dividend': 'Cerebellum', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'CC_total_ICV': {'dividend': 'CC_total', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Entorhinal_ICV': {'dividend': 'Entorhinal', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Fusiform_ICV': {'dividend': 'Fusiform', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Hippocampus_ICV': {'dividend': 'Hippocampus', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Lateral-Ventricles_ICV': {'dividend': 'Lateral-Ventricles', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Lateral-Inferior-Ventricles_ICV': {'dividend': 'Lateral-Inferior-Ventricles', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'MidTemp_ICV': {'dividend': 'MidTemp', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Pallidum_ICV': {'dividend': 'Pallidum', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Putamen_ICV': {'dividend': 'Putamen', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Thalamus_ICV': {'dividend': 'Hippocampus', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'Ventricles_ICV': {'dividend': 'Hippocampus', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'CortexVol_ICV': {'dividend': 'CortexVol', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'BrainSegVolNotVent_ICV': {'dividend': 'BrainSegVolNotVent', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
        'CerebralWhiteMatterVol_ICV': {'dividend': 'CerebralWhiteMatterVol', 'divisor': 'EstimatedTotalIntraCranialVol', 'bin': 5, 'replace': False, 'round': {'digits': 6, 'to_half': False}},
    }
    
    def __init__(self, files: list[FileSettings], clean_file_path: str, add_ratios: bool = True, bin_data: bool = False, impute: bool = False):
        self.files = files
        self.clean_file_path = clean_file_path
        self.df: pd.DataFrame = None
        self.df_train: pd.DataFrame = None
        self.df_test: pd.DataFrame = None
        self.load_data()
        self.clean_up()
        self.replace_categories()
        if add_ratios:
            self.add_ratios()
        self.df = self.df[self.columns.keys()]
        if not impute:
            self.df_nans = self.df[self.df.isna().any(axis=1)]
            self.df.dropna(inplace=True)
        self.split_data()
        if impute:
            self.impute()
            self.impute_test()
        if bin_data:
            self.bin_data()



    def load_data(self) -> None:
        na_values = ['.', ' ']
        
        dfs: list[pd.DataFrame] = []
        for file in self.files:
            for sheet in file['sheets']:
                dfs.append(pd.read_excel(file['path'], sheet['name'], skiprows=1, na_values=na_values, decimal=',',
                           parse_dates=sheet['parse_dates'], usecols=sheet['cols'], index_col='Repseudonym'))
        df = pd.concat(dfs, axis=1, join='outer')
        df.to_csv(f'{time.time()}.csv', index=True)
        self.df = df[df['prmdiag'] != 100]

    def clean_up(self) -> None:
        
        self.df['AGE'] = (self.df['visdat'].dt.year - self.df['brthdat'].dt.year + (self.df['visdat'].dt.month - self.df['brthdat'].dt.month)/12).round(1)
        self.df['APOE2'] = self.df['ApoE'].str.count('2')
        self.df['APOE3'] = self.df['ApoE'].str.count('3')
        self.df['APOE4'] = self.df['ApoE'].str.count('4')
        self.df = self.df[self.df['prmdiag'] != 100]

        smoke_conditions = [(self.df['smoke'] == 1), self.df['smokef'] == 1]
        smoke_options = ['Aktuell', 'Ehemalig']
        self.df['Rauchen'] = np.select(smoke_conditions, smoke_options, 'Nie')
        self.df['Raucherjahre'] = self.df['smoyrs'].fillna(0) + self.df['smoyrsf'].fillna(0)
        self.df['Pack_Years'] = self.df['packyrs'].fillna(0) + self.df['packyrsf'].fillna(0)
        self.df['Zigaretten_pro_Tag'] = self.df['cigpdy'].fillna(0) + self.df['cigpdyf'].fillna(0)
        self.df['Hippocampus'] = self.df['Left-Hippocampus'] + self.df['Right-Hippocampus']
        self.df['Entorhinal'] = self.df['lh_entorhinal_volume'] + self.df['rh_entorhinal_volume']
        self.df['Fusiform'] = self.df['lh_fusiform_volume'] + self.df['rh_fusiform_volume']
        self.df['MidTemp'] = self.df['lh_middletemporal_volume'] + self.df['rh_middletemporal_volume']
        self.df['Lateral-Ventricles'] = self.df['Left-Lateral-Ventricle'] + self.df['Right-Lateral-Ventricle'] 
        self.df['Lateral-Inferior-Ventricles'] = self.df['Left-Inf-Lat-Vent'] + self.df['Right-Inf-Lat-Vent']
        self.df['Ventricles'] = (self.df['Left-Inf-Lat-Vent'] + self.df['Right-Inf-Lat-Vent']
                                 + self.df['Left-Lateral-Ventricle'] + self.df['Right-Lateral-Ventricle']
                                 + self.df['3rd-Ventricle'] + self.df['4th-Ventricle'] + self.df['5th-Ventricle']
                                )
        self.df['CC_total'] = (self.df['CC_Posterior'] + self.df['CC_Mid_Posterior']
                                 + self.df['CC_Central'] + self.df['CC_Mid_Anterior']
                                 + self.df['CC_Anterior'])
        self.df['Amygdala'] = self.df['Left-Amygdala'] + self.df['Right-Amygdala']
        self.df['Thalamus'] = self.df['Left-Thalamus-Proper'] + self.df['Right-Thalamus-Proper']
        self.df['Putamen'] = self.df['Left-Putamen'] + self.df['Right-Putamen']
        self.df['Caudate'] = self.df['Left-Caudate'] + self.df['Right-Caudate']
        self.df['Pallidum'] = self.df['Left-Pallidum'] + self.df['Right-Pallidum']
        self.df['Accumbens-area'] = self.df['Left-Accumbens-area'] + self.df['Right-Accumbens-area']
        self.df['Cerebellum'] = (self.df['Left-Cerebellum-White-Matter'] + self.df['Left-Cerebellum-Cortex']
                                 + self.df['Right-Cerebellum-White-Matter'] + self.df['Right-Cerebellum-Cortex'])


    def impute(self, n: int = 5) -> None:
        """Imputes NAN values in the training pd.Dataframe.
        Rows with NAN values in nominal columns gets ignored.
        Nominal data gets encoded. Then the data gets scaled and NAN values gets imputed.

        Args:
            n (int, optional): Amount of neighbors for KNNImputer. Defaults to 5.
        """
        dont_impute_cols = ['prmdiag', 'sex', 'hearing', 'living', 'maristat', 'graduat', 'Rauchen', 'alcconsm', 'alcabuse']
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
        self.df_train.dropna(inplace=True)

    def impute_test(self, n: int = 5) -> None:
        """Imputes NAN values in the training pd.Dataframe.
        Rows with NAN values in nominal columns gets ignored.
        Nominal data gets encoded. Then the data gets scaled and NAN values gets imputed.

        Args:
            n (int, optional): Amount of neighbors for KNNImputer. Defaults to 5.
        """
        dont_impute_cols = ['prmdiag', 'sex', 'hearing', 'living', 'maristat', 'graduat', 'Rauchen', 'alcconsm', 'alcabuse']
        impute_cols = [col for col in self.columns.keys() if col not in dont_impute_cols]
        mask = self.df_test[dont_impute_cols].notna().all(axis=1)
        df_numeric = self.df_test.loc[mask, impute_cols]
        df_nominal = self.df_test.loc[mask, dont_impute_cols]

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
            
        self.df_test.loc[mask, impute_cols] = df_imputed_numeric
        self.df_test.dropna(inplace=True)


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


    def bin_data(self) -> None:
        for col, settings in self.columns.items():
            bins = settings['bin']

            if not bins:
                continue
            if not isinstance(bins, list):
                _, bins = pd.qcut(self.df_train[col], q=bins, retbins=True, duplicates='drop')
            bins[0] = -np.inf
            bins[-1] = np.inf
            self.df_train[f'{col}_bin'] = pd.cut(self.df_train[col],  bins=bins, include_lowest=True)


    def replace_categories(self) -> None:
        """Replaces selected values within the main pd.Dataframe.
        """
        for col, replace_dict in [(key, value['replace']) for key, value in self.columns.items() if value['replace']]:
            self.df[col] = self.df[col].replace(replace_dict)


    def split_data(self) -> None:
        """Splits data into training and testing data.
        """
        self.df_train, self.df_test = train_test_split(self.df, test_size=0.2, random_state=42)
        self.df_train.reset_index(inplace=True, drop=True)


    def save_data(self, train: bool = True, test: bool = True, whole: bool = False, drop_nans = False, nan_df: bool = False) -> None:
        """Saves selected pd.Dataframes.

        Args:
            train (bool, optional): Save trainings data. Defaults to True.
            test (bool, optional): Save testing data. Defaults to True.
            whole (bool, optional): Save whole data. Defaults to False.
        """
        if train:
            if drop_nans:
                self.df_train.dropna().to_csv(f'{self.clean_file_path}/delcode_train.csv', index=False)
            else:
                self.df_train.to_csv(f'{self.clean_file_path}/delcode_train.csv')
        if test:
            if drop_nans:
                self.df_test.dropna().to_csv(f'{self.clean_file_path}/delcode_test.csv', index=True)
            else:
                self.df_test.to_csv(f'{self.clean_file_path}/delcode_test.csv', index=True)
        if whole:
            if drop_nans:
                self.df.dropna().to_csv(f'{self.clean_file_path}/delcode.csv', index=False)
            else:
                self.df.to_csv(f'{self.clean_file_path}/delcode.csv', index=False)
        if nan_df:
            self.df_nans.to_csv(f'{self.clean_file_path}/delcode_nan.csv', index=True)
    
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
    


    # def bin_data(self) -> None:
    #     for col, settings in self.columns.items():
    #         bins = settings['bin']
    #         if not bins:
    #             continue
    #         if type(bin) == list:
    #             self.df_train[f'{col}_bin'] = pd.cut(self.df_train[col],  bins=bins, include_lowest=True)
    #             continue
    #         self.self.df_train[f'{col}_bin'] = pd.qcut(self.df_train[col], q=bins)


if __name__ == '__main__':
    files: list[FileSettings] = [
        {'path': '40_Realisation/000_raw_data/DELCODE/Antrag 205_integritycholinergicforebrain_20200914_BL_repseudonymisiert.xlsx',
         'sheets': [{'name': 'Baseline', 'cols': None, 'parse_dates': ['visdat', 'brthdat']},
                    {'name': 'MRT-Analyseergebnisse', 'cols': None, 'parse_dates': False}]},
        {'path': '40_Realisation/000_raw_data/DELCODE/Antrag 222_Dyrba_disease spreading_20201125_DELCODE BL.xlsx',
         'sheets': [{'name': 'Baseline', 'cols': ['Repseudonym', 'mmstot'], 'parse_dates': False}]}
    ]
    clean_file_path = '40_Realisation/100_clean_data/DELCODE/impute'
    delcode_cleaner = DELCODECleaner(files, clean_file_path, bin_data=True)
    delcode_cleaner.save_data(True, False, False, False)