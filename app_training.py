import random
from torch.utils.data import DataLoader, TensorDataset
import torch
import numpy as np
from tqdm import tqdm
from app_model import *
from sklearn.model_selection import train_test_split




class Trainer:
    def __init__(self, input_bert_dim,w2v_dim,bert_numpy,w2v_numpy,labels,criterion, fun_activation,optimizer, epochs=10, batch_size=32, learning_rate=1e-4, weight_decay=1e-5, dropout=0.3, seed=42, patience=8):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.criterion = criterion
        self.epochs = epochs
        self.batch_size = batch_size
        self.seed = seed
        self.patience = patience
        self.model = SentimentClassifierNN(w2v_dim,input_bert_dim,dropout,fun_activation).to(self.device)
        self.optimizer = optimizer(self.model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        self.set_seed(seed)
        self.bert_numpy=bert_numpy
        self.w2v_numpy=w2v_numpy
        self.labels=labels
        self.train_losses = []
        self.val_losses = []
        self.train_accuracy=[]
        self.val_accuracy=[]


    def set_seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)




    def train(self):
        print("[INFO]: Entrenando red neuronal...")


        bert_tensor = torch.tensor(self.bert_numpy, dtype=torch.float32)
        w2v_tensor = torch.tensor(self.w2v_numpy, dtype=torch.float32)
        label_tensor = torch.tensor(self.labels, dtype=torch.long)


        X = list(zip(bert_tensor,  w2v_tensor))
        X_train, X_val, y_train, y_val = train_test_split(
            X, label_tensor, test_size=0.2, random_state=self.seed, stratify=label_tensor
        )

        bert_train, w2v_train = zip(*X_train)
        bert_val, w2v_val = zip(*X_val)


        train_dataset = TensorDataset(
            torch.stack([x.clone().detach().to(self.device) for x in bert_train]),
            torch.stack([x.clone().detach().to(self.device) for x in w2v_train]),
            y_train.clone().detach().to(self.device)
        )
        val_dataset = TensorDataset(
            torch.stack([x.clone().detach().to(self.device) for x in bert_val]),
            torch.stack([x.clone().detach().to(self.device) for x in w2v_val]),
            y_val.clone().detach().to(self.device)
        )


        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)

        best_val_loss = float('inf')
        best_model_state = None
        pbar = tqdm(range(self.epochs), desc='Training', unit='epoch',
                    postfix={'train_loss': 0.0, 'val_loss': 0.0,'train_accuracy': 0.0 , 'val_accuracy':0.0})
        val_losses = []
        for epoch in pbar:
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            total_train_samples = 0
            for bert_features, w2v_features, targets in train_loader:
                self.optimizer.zero_grad()
                outputs = self.model(bert_features, w2v_features)
                loss = self.criterion(outputs, targets)
                loss.backward()
                self.optimizer.step()

                train_loss += loss.item()
                train_correct += (outputs.argmax(dim=1) == targets).sum().item()
                total_train_samples += targets.size(0)
            train_loss /= len(train_loader)
            train_accuracy = train_correct / total_train_samples
            self.model.eval()
            val_loss = 0.0
            val_correct = 0
            total_val_samples = 0
            self.model.eval()
            with torch.no_grad():
                 for bert_features, w2v_features, targets in val_loader:
                    outputs = self.model(bert_features, w2v_features)
                    loss = self.criterion(outputs, targets)
                    val_loss += loss.item()
                    val_correct += (outputs.argmax(dim=1) == targets).sum().item()
                    total_val_samples += targets.size(0)

            val_loss /= len(val_loader)
            val_accuracy = val_correct / total_val_samples

            self.val_losses.append(val_loss)
            self.train_losses.append(train_loss)
            self.train_accuracy.append(train_accuracy)
            self.val_accuracy.append(val_accuracy)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = self.model.state_dict()
                patience_counter = 0
            else:
                patience_counter += 1


            if patience_counter >= self.patience:
                print(f"[INFO]: Early stopping activado en la época {epoch+1}")
                break


            pbar.set_postfix(train_loss=train_loss, val_loss=val_loss, train_accuracy=train_accuracy, val_accuracy=val_accuracy)

        print("[INFO]: Entrenamiento finalizado.")


        if best_model_state:
            model_path = f'./models/w2v/best_model_{best_val_loss}_.pth'
            torch.save(best_model_state, model_path)
            self.model.load_state_dict(best_model_state)
            print("[INFO]: Mejor modelo cargado con val_loss:", best_val_loss)