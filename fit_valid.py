"""apprentissage et validation
"""
from msilib.sequence import tables
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression, ElasticNet, LogisticRegression
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from rich import print
from rich.table import Table
from rich.console import Console

one_hot_encoder = Pipeline(
  steps=[
    ('one_hot', OneHotEncoder(handle_unknown='ignore'))
  ]
)

preprocessor = ColumnTransformer(
  transformers=[
    ('categorical', one_hot_encoder, ['lieux', 'diff', 'theme']),
  ]
)

models_names = ["Linear Regression", "ElasticNet","Random Forest"]

pipelines = [
    Pipeline(steps=[('preprocessor', preprocessor), ('Reg', LinearRegression())]),
    Pipeline(steps=[('preprocessor', preprocessor), ('Reg', ElasticNet())]),
    Pipeline(steps=[('preprocessor', preprocessor), ('Reg', RandomForestRegressor())])
]

allgrid = [
    {"Reg__fit_intercept": [True, False]},
    {
        "Reg__fit_intercept": [True, False],
        "Reg__alpha": [0.1, 1., 10.],
        "Reg__l1_ratio": [0.1, 0.5, 0.9],
        "Reg__max_iter": [10000],
    },
    {"Reg__n_estimators": range(50, 300, 20)}
]

def _import_and_split(df:str):
    df = pd.read_pickle("my_dataframe.pkl")
    X = df.drop(["description", "prix"], axis = 1)
    y = df["prix"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y)
    return X_tr, X_te, y_tr, y_te

def _fit_and_dictResult(df:str)->dict:
    X_tr, X_te, y_tr, y_te = _import_and_split(df)
    results = dict()
    for pipe, grid, name in zip(pipelines, allgrid, models_names):
        g = GridSearchCV(pipe, param_grid= grid)
        g.fit(X_tr, y_tr)
        results[name]=g
    return results

def _print_table(df):
    X_tr, X_te, y_tr, y_te = _import_and_split(df)
    results = _fit_and_dictResult(df)
    tbl = Table(
        title="Résumé des résultats de crossvalidation.",
        show_header=True,
    )
    tbl.add_column("Nom")
    tbl.add_column("Score Cross validation")
    tbl.add_column("Score entrainement")
    tbl.add_column("Choix Hyperparamètres")
    for nom, modele in results.items():
        tbl.add_row(
            nom, 
            f"{modele.best_score_:.2f}", 
            f"{modele.score(X_tr, y_tr):.2f}",
            str(modele.best_params_),
        )
    return tbl

df=input("Quel est le nom du fichier ? ")
tbl = _print_table(df)
console = Console()
console.print(tbl)