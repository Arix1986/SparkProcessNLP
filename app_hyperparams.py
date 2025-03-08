import optuna
import torch
import torch.nn as nn
from app_training import *


class HyperparameterOptimization:
    def __init__(self, bert_numpy, tfidf_numpy, labels,name_study='hyperparameter_optimization', num_trials=40, num_epochs=35):
       
        self.input_tfidf_dim = tfidf_numpy.shape[1]
        self.input_bert_dim = bert_numpy.shape[1]
        self.num_trials = num_trials
        self.num_epochs = num_epochs
        self.name_study = name_study
        self.bert_numpy=bert_numpy
        self.tfidf_numpy=tfidf_numpy
        self.labels=labels
        self.criterion=nn.CrossEntropyLoss()


    def objective(self, trial):
        lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
        weight_decay = trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True)
        dropout=trial.suggest_float("dropout", 0.3,0.5)
        batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])
        optimizer_name = trial.suggest_categorical("optimizer", ["Adam", "AdamW", "SGD"])
        optimizer_dict = {
            "Adam": torch.optim.Adam,
            "AdamW": torch.optim.AdamW,
            "SGD": torch.optim.SGD,
        }
        selected_optimizer = optimizer_dict[optimizer_name]


        trainer = Trainer(
        input_tfidf_dim=self.input_tfidf_dim,
        input_bert_dim=self.input_bert_dim,
        bert_numpy=self.bert_numpy,
        tfidf_numpy=self.tfidf_numpy,
        labels=self.labels,
        criterion=self.criterion,
        optimizer=selected_optimizer,
        epochs=self.num_epochs,
        batch_size=batch_size,
        learning_rate=lr,
        weight_decay=weight_decay,
        dropout=dropout
        )


        val_losses = trainer.train()

        return val_losses[-1]

    def optimize(self):
        study = optuna.create_study(
            direction="minimize",
            storage="sqlite:///optuna_study.db",
            study_name=self.name_study,
            load_if_exists=True
        )
        study.optimize(self.objective, n_trials=self.num_trials)
        return study