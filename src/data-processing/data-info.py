import pandas as pd


def get_statistics(files):
    for file in files:
        multi_col_start = '\multirow{4}{*}{\\rotatebox{90}{'
        multi_col_end = '}}'
        print('\\hline')
        print('\\hline')
        print(f'{multi_col_start}{file['title']}{multi_col_end}')
        df = pd.read_csv(file['path'])
        dx_col = 'DX'
        gender_col = 'PTGENDER'
        age_col = 'AGE'
        mmse_col = 'MMSE'
        if 'prmdiag' in df.columns:
            dx_col = 'prmdiag'
            gender_col = 'sex'
            age_col = 'AGE'
            mmse_col = 'mmstot'

        count = len(df)
        gender = round(len(df[df[gender_col] == 'Männlich']) / len(df) * 100)
        age_mean = round(df[age_col].mean(), 1)
        age_std = round(df[age_col].std(), 1)
        age_min = df[age_col].min()
        age_max = df[age_col].max()

        mmse_mean = round(df[mmse_col].mean(), 1)
        mmse_std = round(df[mmse_col].std(), 1)
        mmse_min = df[mmse_col].min()
        mmse_max = df[mmse_col].max()
        print(f'& Gesamt & ${count}$ & ${gender} \%$ M & ${age_mean}\pm{age_std}$ $[{age_min}, {age_max}]$ & ${mmse_mean}\pm{mmse_std}$ $[{mmse_min}, {mmse_max}]$\\\\')
        for diagnosis in ['CN', 'MCI', 'AD']:
            selected_df = df[df[dx_col] == diagnosis]
            count = len(selected_df)
            gender = round(len(selected_df[selected_df[gender_col] == 'Männlich']) / len(selected_df) * 100)
            age_mean = round(selected_df[age_col].mean(), 1)
            age_std = round(selected_df[age_col].std(), 1)
            age_min = selected_df[age_col].min()
            age_max = selected_df[age_col].max()

            mmse_mean = round(selected_df[mmse_col].mean(), 1)
            mmse_std = round(selected_df[mmse_col].std(), 1)
            mmse_min = selected_df[mmse_col].min()
            mmse_max = selected_df[mmse_col].max()
            print(f'& {diagnosis} & ${count}$ & ${gender} \%$ M & ${age_mean}\pm{age_std}$ $[{age_min}, {age_max}]$ & ${mmse_mean}\pm{mmse_std}$ $[{mmse_min}, {mmse_max}]$\\\\')



if __name__ == '__main__':
    files = [
        {'title': 'ADNI', 'path': '40_Realisation/100_clean_data/ADNI/adni.csv', 'nan': False},
        {'title': 'DELCODE', 'path': '40_Realisation/100_clean_data/DELCODE/delcode.csv','nan': False},
        {'title': 'DELCODE', 'path': '40_Realisation/100_clean_data/DELCODE/impute/delcode imputed ohne nan.csv','nan': False},
    ]

    get_statistics(files)