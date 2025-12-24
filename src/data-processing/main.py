import pandas as pd
import numpy as np
from model_building.ModelBuilder import ModelBuilder
from clean_up_data.ADNICleaner import ADNICleaner
from clean_up_data.DELCODECleaner import DELCODECleaner
from model_building.ConfigLoader import ConfigLoader
from model_building.Model import Model
from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve, auc, f1_score, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import matplotlib.pyplot as plt


def process_adni_data():
    print('process adni data')
    adni_merge = 'data/0 rawADNI/ADNIMERGE.csv'
    clean_file_path = 'data/1 processed/ADNI'
    adni_Cleaner = ADNICleaner(adni_merge, clean_file_path, bin_data=True)
    adni_Cleaner.save_data(True, False, drop_nans=True)
    adni_Cleaner.save_data(False, True, True, drop_nans=False, nan_df=True)

def process_delcode_data():
    print('process delcode data')
    files = [
        {'path': 'data/0 rawDELCODE/Antrag 205_integritycholinergicforebrain_20200914_BL_repseudonymisiert.xlsx',
         'sheets': [{'name': 'Baseline', 'cols': None, 'parse_dates': ['visdat', 'brthdat']},
                    {'name': 'MRT-Analyseergebnisse', 'cols': None, 'parse_dates': False}]},
        {'path': 'data/0 raw/DELCODE/Antrag 222_disease spreading_20201125_DELCODE BL.xlsx',
         'sheets': [{'name': 'Baseline', 'cols': ['Repseudonym', 'mmstot'], 'parse_dates': False}]}
    ]
    clean_file_path = '40_Realisation/100_clean_data/DELCODE'
    delcode_cleaner = DELCODECleaner(files, clean_file_path, bin_data=True)
    delcode_cleaner.save_data(train=True, test=False, whole=False, drop_nans=True)
    delcode_cleaner.save_data(train=False, test=True, whole=True, drop_nans=False, nan_df=True)

    print('process delcode data')
    files = [
        {'path': 'data/0 raw/Antrag 205_integritycholinergicforebrain_20200914_BL_repseudonymisiert.xlsx',
         'sheets': [{'name': 'Baseline', 'cols': None, 'parse_dates': ['visdat', 'brthdat']},
                    {'name': 'MRT-Analyseergebnisse', 'cols': None, 'parse_dates': False}]},
        {'path': '40_Realisation/000_raw_data/DELCODE/Antrag 222_disease spreading_20201125_DELCODE BL.xlsx',
         'sheets': [{'name': 'Baseline', 'cols': ['Repseudonym', 'mmstot'], 'parse_dates': False}]}
    ]
    clean_file_path = 'data/1 processed/DELCODE/impute'
    delcode_cleaner = DELCODECleaner(files, clean_file_path, bin_data=True, impute=True)
    delcode_cleaner.save_data(train=True, test=False, whole=False, drop_nans=True)
    delcode_cleaner.save_data(train=False, test=True, whole=True, drop_nans=False)


def test_model(name: str, config_path: str, test_data_path: str,
               index_col: list[str], image_path: str) -> None:
    config = ConfigLoader(config_path)
    model = Model(name, config.get_save_path_and_file_type()[0])
    mapped_cols_nodes = {}
   
    for col, node in config.get_mapped_cols_and_node_names().items():
        if '_bin' in col:
            mapped_cols_nodes[col[:-4]] = node
        else:
            mapped_cols_nodes[col] = node
    
    test_data = pd.read_csv(test_data_path, index_col=index_col)
    test_data = test_data.rename(columns=mapped_cols_nodes)

    if 'DX' in mapped_cols_nodes.keys():
        del mapped_cols_nodes['DX']
    if 'prmdiag' in mapped_cols_nodes.keys():
        del mapped_cols_nodes['prmdiag']

    y_true = []
    y_pred = []
    y_score = []
    for index, row in test_data.iterrows():
        evidence = row.loc[mapped_cols_nodes.values()].dropna().to_dict()
        y_true.append(row['Diagnose'])
        prediction = model.get_inference(evidence, target_node='Diagnose')
        max_index = np.argmax(prediction.values)
        y_pred.append(prediction.state_names['Diagnose'][max_index])

        y_score.append({key: value for key, value in zip(prediction.state_names['Diagnose'], prediction.values)})
    y_score_df = pd.DataFrame(y_score)
    y_score_df = y_score_df.reindex(sorted(y_score_df.columns), axis=1)
    print(f'Model: {name}')
    print(f'accuracy score: {accuracy_score(y_true, y_pred)}')
    print(f'F1 score - weighted: {f1_score(y_true, y_pred, average='weighted')}')
    print(f'F1 score - None: {f1_score(y_true, y_pred, average=None)}')
    print(f'F1 score - micro: {f1_score(y_true, y_pred, average='micro')}')
    print(f'F1 score - macro: {f1_score(y_true, y_pred, average='macro')}')
    auc_score = roc_auc_score(y_true, y_score_df, average='weighted', multi_class='ovr')
    print(f'ROC AUC Score: {auc_score}')
    print(f'CM: {confusion_matrix(y_true, y_pred)}')

    lb = LabelBinarizer()
    y_true_bin = lb.fit_transform(y_true)
    classes = lb.classes_

    cm = 1/2.54
    plt.figure(figsize=(11*cm, 11*cm))

    for i, class_name in enumerate(classes):
        y_score_class = y_score_df[class_name] 
        
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_score_class)
        roc_auc = auc(fpr, tpr)
        
        plt.plot(fpr, tpr, lw=2, label=f'Klasse {class_name} (AUC = {roc_auc:.2f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'Multi-Class ROC Kurve für {name}')
    plt.legend(loc="lower right")
    plt.savefig(f'{image_path}/{name} roc.svg', format='svg')


if __name__ == '__main__':
    net_configs = [
        'data/2 configs/ADNI.yaml',
        'data/2 configs/DELCODE.yaml',
        'data/2 configs/DELCODE impute.yaml',
    ]

    
    process_adni_data()

    process_delcode_data()


    for net_config in net_configs:
        print('build models')
        model_builder = ModelBuilder(net_config)
        # for cpds in model_builder.model.get_cpds():
        #     print(cpds)
    test_model(name='ADNI', config_path='40_Realisation/data-processing/config_files/ADNI.yaml',
               test_data_path='40_Realisation/100_clean_data/ADNI/adni_test.csv', index_col=['PTID'],
               image_path='40_Realisation/100_clean_data/ADNI')
    test_model(name='DELCODE', config_path='40_Realisation/data-processing/config_files/DELCODE.yaml',
               test_data_path='40_Realisation/100_clean_data/DELCODE/delcode_test.csv', index_col=['Repseudonym'],
               image_path='40_Realisation/100_clean_data/DELCODE')
    
    print('with nans')
    test_model(name='ADNI mit NaN-Daten', config_path='data/2 configs/ADNI.yaml',
               test_data_path='40_Realisation/100_clean_data/ADNI/adni_nan.csv', index_col=['PTID'],
               image_path='40_Realisation/100_clean_data/ADNI')
    test_model(name='data/2 configs/DELCODE.yaml',
               test_data_path='40_Realisation/100_clean_data/DELCODE/delcode_nan.csv', index_col=['Repseudonym'],
               image_path='40_Realisation/100_clean_data/DELCODE')

    test_model(name='DELCODE impute', config_path='data/2 configs/DELCODE impute.yaml',
            test_data_path='40_Realisation/100_clean_data/DELCODE/impute/delcode_test.csv', index_col=['Repseudonym'],
            image_path='40_Realisation/100_clean_data/DELCODE/impute')
