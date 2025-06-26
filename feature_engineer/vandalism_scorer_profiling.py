import sys, os

# Automatically add the project root (1 level up) to the Python path
project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from feature_engineer import VandalismScorer
import pandas as pd

df = pd.read_csv(project_root + "/Data/train.csv")
scorer = VandalismScorer()

scorer.fit(df, df['isvandalism'])
df_transformed = scorer.transform(df)