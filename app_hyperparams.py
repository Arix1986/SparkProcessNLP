import optuna
import torch
import torch.nn as nn
from app_training import *


class HyperparameterOptimization:
    def __init__(self, bert_numpy,w2v_numpy, labels,name_study='hyperparameter_optimization', num_trials=40, num_epochs=35):
        
        self.input_bert_dim = bert_numpy.shape[1]
        self.w2v_dim=w2v_numpy.shape[1]
        self.num_trials = num_trials
        self.num_epochs = num_epochs
        self.name_study = name_study
        self.bert_numpy=bert_numpy
        self.w2v_numpy=w2v_numpy
        self.labels=labels
        self.criterion=nn.CrossEntropyLoss()
        self.activation_functions_dict = {
            "GeLU": nn.GELU(),
            "PReLU": nn.PReLU(),
            "SiLU": nn.SiLU(),
            "Mish": nn.Mish() 
        }

    def objective(self, trial):
        lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
        weight_decay = trial.suggest_float("weight_decay", 1e-6, 1e-3, log=True)
        dropout=trial.suggest_float("dropout", 0.3,0.5)
        activation_name = trial.suggest_categorical("activation_function", list(self.activation_functions_dict.keys()))
        activation_function = self.activation_functions_dict[activation_name]
        optimizer_name = trial.suggest_categorical("optimizer", ["AdamW", "SGD"])
        optimizer_dict = {
            "AdamW": torch.optim.AdamW,
            "SGD": torch.optim.SGD,
        }
        selected_optimizer = optimizer_dict[optimizer_name]


        trainer = Trainer(
        input_bert_dim=self.input_bert_dim,
        w2v_dim=self.w2v_dim,
        bert_numpy=self.bert_numpy,
        w2v_numpy=self.w2v_numpy,
        labels=self.labels,
        criterion=self.criterion,
        fun_activation=activation_function,
        optimizer=selected_optimizer,
        epochs=self.num_epochs,
        batch_size=32,
        learning_rate=lr,
        weight_decay=weight_decay,
        dropout=dropout
        )
        trainer.train()

        val_loss = trainer.val_losses

        return val_loss[-1]

    def optimize(self):
        study = optuna.create_study(
            direction="minimize",
            storage="sqlite:///optuna_study.db",
            study_name=self.name_study,
            load_if_exists=True
        )
        study.optimize(self.objective, n_trials=self.num_trials)
        return study