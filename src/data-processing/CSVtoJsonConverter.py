import pandas as pd
import re
import json


class CSVtoJsonConverter:
    delcode_map = {
        'prmdiag': 'Diagnose',
        'AGE': 'Alter',
        'bmi': 'BMI',
        'sex': 'Geschlecht',
        'hearing': 'Gehör',
        'vision': 'Sehvermögen',
        'visus': 'Visus',
        'living': 'Haushalt',
        'maristat': 'Familienstand',
        'graduat': 'Schulabschluss',
        'Rauchen': 'Rauchen',
        'Raucherjahre': 'Raucherjahre',
        'Pack_Years': 'Pack Years',
        'Zigaretten_pro_Tag': 'Zigaretten pro Tag',
        'alcconsm': 'Alkoholkonsum',
        'alcabuse': 'Alkoholmissbrauch',
        'AD11SUM': 'ADAS11',
        'AD13SUM': 'ADAS13',
        'mmstot': 'MMSE',
        'tmta': 'TMT A',
        'tmtb': 'TMT B',
        'tmtba': 'TMT B/A',
        'fcsfree': 'FCSRT - Free Recall',
        'fcscued': 'FCSRT - Cued Recall',
        'fcstot': 'FCSRT - Total Recall',
        'mwttot': 'MWT-B',
        'wmslm1b': 'WMS-4 LM I',
        'wmslm2b': 'WMS-4 LM II',
        'wmsdsf': 'WMS-R - Vorwärts',
        'wmsdsb': 'WMS-R - Rückwärts',
        'wmstot': 'WMS-R - Gesamt',
        'clockdw': 'Uhren zeichen',
        'clockcpy': 'Uhren abzeichnen',
        'sdmtot': 'SDMT - gegebene Antworten',
        'sdmctot': 'SDMT - richtige Antworten',
        'sdmtpct': 'SDMT - Verhältnis korrekt/bearbeitet',
        'sdmir01': 'SDMT - Erinnerte Symbole',
        'sdmir02': 'SDMT - Symbol-Zahlen-Paare',
        'cercp': 'Figuren abzeichnen',
        'vfatot': 'Verbale Flüssigkeit',
        'APOE2': 'ApoE2',
        'APOE3': 'ApoE3',
        'APOE4': 'ApoE4',
        'Abeta38': 'Beta-Amyloid 38',
        'Abeta40': 'Beta-Amyloid 40',
        'Abeta42': 'Beta-Amyloid 42',
        'totaltau': 'Gesamt-Tau',
        'phosphotau181': 'Phospho-Tau-181',
        'ratio_Abeta42_40': 'Ratio Beta-Amyloid 42/40',
        'ratio_Abeta42_phosphotau181': 'Ratio Beta-Amyloid 42/P-tau181',
        'Accumbens-area': 'Nucleus accumbens',
        'Accumbens-area_ICV': 'Ratio Nucleus accumbens-ICV',
        'Amygdala': 'Amygdala',
        'Amygdala_ICV': 'Ratio Amygdala-ICV',
        'Brain-Stem': 'Hirnstamm',
        'Brain-Stem_ICV': 'Ratio Hirnstamm-ICV',
        'Caudate': 'Caudate',
        'Caudate_ICV': 'Ratio Caudate-ICV',
        'CC_total': 'Corpus callosum',
        'CC_total_ICV': 'Ratio Corpus callosum-ICV',
        'Cerebellum': 'Cerebellum',
        'Cerebellum_ICV': 'Ratio Cerebellum-ICV',
        'CortexVol': 'Cortex',
        'CortexVol_ICV': 'Ratio Cortex-ICV',
        'CerebralWhiteMatterVol': 'Cerebrum - W. Substanz',
        'CerebralWhiteMatterVol_ICV': 'Ratio Cerebrum - W. Substanz-ICV',
        'Entorhinal': 'Entorhinal',
        'Entorhinal_ICV': 'Ratio Entorhinal-ICV',
        'Fusiform': 'Fusiform',
        'Fusiform_ICV': 'Ratio Fusiform-ICV',
        'Hippocampus': 'Hippocampus',
        'Hippocampus_ICV': 'Ratio Hippocampus-ICV',
        'EstimatedTotalIntraCranialVol': 'ICV',
        'Lateral-Ventricles': 'Laterale Ventrikel',
        'Lateral-Ventricles_ICV': 'Ratio Laterale Ventrikel-ICV',
        'Lateral-Inferior-Ventricles': 'Lat.-inf. Ventrikel',
        'Lateral-Inferior-Ventricles_ICV': 'Ratio Lat.-inf. Ventrikel-ICV',
        'MidTemp': 'MidTemp',
        'MidTemp_ICV': 'Ratio MidTemp-ICV',
        'Optic-Chiasm': 'Chiasma opticum',
        'Pallidum': 'Pallidum',
        'Pallidum_ICV': 'Ratio Pallidum-ICV',
        'Putamen': 'Putamen',
        'Putamen_ICV': 'Ratio Putamen-ICV',
        'Thalamus': 'Thalamus',
        'Thalamus_ICV': 'Ratio Thalamus-ICV',
        'Ventricles': 'Ventrikel',
        'Ventricles_ICV': 'Ratio Ventrikel-ICV',
        'BrainSegVolNotVent': 'Gesamtgehirn',
        'BrainSegVolNotVent_ICV': 'Ratio Gesamtgehirn-ICV',
        'WM-hypointensities': 'White Matter Hypointensities'
    }
    adni_map = {
        'DX': 'Diagnose',
        'AGE': 'Alter',
        'PTGENDER': 'Geschlecht',
        'PTMARRY': 'Familienstand',
        'PTEDUCAT': 'Bildungsjahre',
        'ADAS11': 'ADAS11',
        'ADAS13': 'ADAS13',
        'EcogPtTotal': 'EcogPtTotal',
        'EcogSPTotal': 'EcogSPTotal',
        'CDRSB': 'CDRSB',
        'FAQ': 'FAQ',
        'MMSE': 'MMSE',
        'MOCA': 'MOCA',
        'RAVLT_forgetting': 'RAVLT-forgetting',
        'RAVLT_immediate': 'RAVLT-immediate',
        'RAVLT_learning': 'RAVLT-learning',
        'TRABSCOR': 'TMT B',
        'LDELTOTAL': 'LDELTOTAL',
        'ABETA': 'Beta-Amyloid 42',
        'PTAU': 'Phospho-Tau-181',
        'TAU': 'Gesamt-Tau',
        'APOE4': 'ApoE4',
        'AV45': 'AV45',
        'Entorhinal': 'Entorhinal',
        'Entorhinal_ICV': 'Ratio Entorhinal-ICV',
        'Fusiform': 'Fusiform',
        'Fusiform_ICV': 'Ratio Fusiform-ICV',
        'Hippocampus': 'Hippocampus',
        'Hippocampus_ICV': 'Ratio Hippocampus-ICV',
        'ICV': 'ICV',
        'MidTemp': 'MidTemp',
        'MidTemp_ICV': 'Ratio MidTemp-ICV',
        'Ventricles': 'Ventrikel',
        'Ventricles_ICV': 'Ratio Ventrikel-ICV',
        'WholeBrain': 'Gesamtgehirn'
    }
    group_map = {
        'Alter': 'Allgemein',
        'Geschlecht': 'Allgemein',
        'BMI': 'Allgemein',
        'Haushalt': 'Allgemein',
        'Familienstand': 'Allgemein',
        'Bildungsjahre': 'Allgemein',
        'Schulabschluss': 'Allgemein',

        'Gehör': 'Sensorik',
        'Sehvermögen': 'Sensorik',
        'Visus': 'Sensorik',

        'Rauchen': 'Risikofaktoren',
        'Raucherjahre': 'Risikofaktoren',
        'Pack Years': 'Risikofaktoren',
        'Zigaretten pro Tag': 'Risikofaktoren',
        'Alkoholkonsum': 'Risikofaktoren',
        'Alkoholmissbrauch': 'Risikofaktoren',

        'ADAS11': 'Neuropsychologische Tests',
        'ADAS13': 'Neuropsychologische Tests',
        'EcogPtTotal': 'Neuropsychologische Tests',
        'EcogSPTotal': 'Neuropsychologische Tests',
        'CDRSB': 'Neuropsychologische Tests',
        'FAQ': 'Neuropsychologische Tests',
        'MOCA': 'Neuropsychologische Tests',
        'RAVLT-forgetting': 'Neuropsychologische Tests',
        'RAVLT-immediate': 'Neuropsychologische Tests',
        'RAVLT-learning': 'Neuropsychologische Tests',
        'LDELTOTAL': 'Neuropsychologische Tests',
        'MMSE': 'Neuropsychologische Tests',
        'TMT A': 'Neuropsychologische Tests',
        'TMT B': 'Neuropsychologische Tests',
        'TMT B/A': 'Neuropsychologische Tests',
        'FCSRT - Free Recall': 'Neuropsychologische Tests',
        'FCSRT - Cued Recall': 'Neuropsychologische Tests',
        'FCSRT - Total Recall': 'Neuropsychologische Tests',
        'MWT-B': 'Neuropsychologische Tests',
        'WMS-4 LM I': 'Neuropsychologische Tests',
        'WMS-4 LM II': 'Neuropsychologische Tests',
        'WMS-R - Vorwärts': 'Neuropsychologische Tests',
        'WMS-R - Rückwärts': 'Neuropsychologische Tests',
        'WMS-R - Gesamt': 'Neuropsychologische Tests',
        'Uhren zeichen': 'Neuropsychologische Tests',
        'Uhren abzeichnen': 'Neuropsychologische Tests',
        'SDMT - gegebene Antworten': 'Neuropsychologische Tests',
        'SDMT - richtige Antworten': 'Neuropsychologische Tests',
        'SDMT - Verhältnis korrekt/bearbeitet': 'Neuropsychologische Tests',
        'SDMT - Erinnerte Symbole': 'Neuropsychologische Tests',
        'SDMT - Symbol-Zahlen-Paare': 'Neuropsychologische Tests',
        'Figuren abzeichnen': 'Neuropsychologische Tests',
        'Verbale Flüssigkeit': 'Neuropsychologische Tests',

        'ApoE2': 'Genanalyse',
        'ApoE3': 'Genanalyse',
        'ApoE4': 'Genanalyse',

        'Beta-Amyloid 38': 'Liquoranalyse',
        'Beta-Amyloid 40': 'Liquoranalyse',
        'Beta-Amyloid 42': 'Liquoranalyse',
        'Gesamt-Tau': 'Liquoranalyse',
        'Phospho-Tau-181': 'Liquoranalyse',
        'Ratio Beta-Amyloid 42/40': 'Liquoranalyse',
        'Ratio Beta-Amyloid 42/P-tau181': 'Liquoranalyse',

        'Nucleus accumbens': 'Bildgebung',
        'Ratio Nucleus accumbens-ICV': 'Bildgebung',
        'Amygdala': 'Bildgebung',
        'Ratio Amygdala-ICV': 'Bildgebung',
        'Hirnstamm': 'Bildgebung',
        'Ratio Hirnstamm-ICV': 'Bildgebung',
        'Caudate': 'Bildgebung',
        'Ratio Caudate-ICV': 'Bildgebung',
        'Corpus callosum': 'Bildgebung',
        'Ratio Corpus callosum-ICV': 'Bildgebung',
        'Cerebellum': 'Bildgebung',
        'Ratio Cerebellum-ICV': 'Bildgebung',
        'Cortex': 'Bildgebung',
        'Ratio Cortex-ICV': 'Bildgebung',
        'Cerebrum - W. Substanz': 'Bildgebung',
        'Ratio Cerebrum - W. Substanz-ICV': 'Bildgebung',
        'Entorhinal': 'Bildgebung',
        'Ratio Entorhinal-ICV': 'Bildgebung',
        'Fusiform': 'Bildgebung',
        'Ratio Fusiform-ICV': 'Bildgebung',
        'Hippocampus': 'Bildgebung',
        'Ratio Hippocampus-ICV': 'Bildgebung',
        'ICV': 'Bildgebung',
        'Laterale Ventrikel': 'Bildgebung',
        'Ratio Laterale Ventrikel-ICV': 'Bildgebung',
        'Lat.-inf. Ventrikel': 'Bildgebung',
        'Ratio Lat.-inf. Ventrikel-ICV': 'Bildgebung',
        'MidTemp': 'Bildgebung',
        'Ratio MidTemp-ICV': 'Bildgebung',
        'Chiasma opticum': 'Bildgebung',
        'Pallidum': 'Bildgebung',
        'Ratio Pallidum-ICV': 'Bildgebung',
        'Putamen': 'Bildgebung',
        'Ratio Putamen-ICV': 'Bildgebung',
        'Thalamus': 'Bildgebung',
        'Ratio Thalamus-ICV': 'Bildgebung',
        'Ventrikel': 'Bildgebung',
        'Ratio Ventrikel-ICV': 'Bildgebung',
        'Gesamtgehirn': 'Bildgebung',
        'Ratio Gesamtgehirn-ICV': 'Bildgebung',
        'White Matter Hypointensities': 'Bildgebung',
        'AV45': 'Bildgebung'  
    }
    def __init__(self, todo: list, target: str):
        self.target = target
        for task in todo:
            self.df = pd.read_csv(task['file'])
            if 'adni' in task['file']:
                self.study = 'ADNI'
                self.pid_col = 'PTID'
                self.df.rename(columns=self.adni_map, inplace=True)
            else:
                self.study = 'DELCODE'
                self.pid_col = 'Repseudonym'
                self.df.rename(columns=self.delcode_map, inplace=True)
            for pid in task['pids']:
                data = self.convert(pid)
                self.save_json(data)

    def convert(self, pid):
        patient = self.df[self.df[self.pid_col] == pid]
        data = {
            'patient_id': pid,
            'patient_surname': self.study,
            'patient_name': patient['Diagnose'].iloc[0],
            'patient_bday': '',
            'patient_gender': patient['Geschlecht'].iloc[0],
            'interaction_data': {
                "case_counter": 1,
                "case_list": [0]
            },
            'cases_data': [{}]
        }
        for col in patient.columns:
            if col in ['Repseudonym', 'PTID', 'Diagnose']:
                continue
            group = self.group_map[col]
            id = clean_id(f'case0_{group}_{col}')
            data['cases_data'][0][id] = patient[col].iloc[0]
        return data
    
    def save_json(self, data: dict):
        print(data)
        with open(f'{self.target}/{data['patient_id']}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)    

def clean_id(s):
    if not s: return ""
    s = str(s).strip()
    s = re.sub(r'[^a-zA-Z0-9]', '_', s)
    return s.strip('_').lower()


if __name__ == '__main__':
    todo = [
        {'file': '40_Realisation/100_clean_data/DELCODE/delcode_test.csv',
         'pids': ['d23ebb73d']
        }]
    converter = CSVtoJsonConverter(todo, '40_Realisation/examples')