import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

class ContrastiveEncoder(nn.Module):
    def __init__(self, in_features, embed_dim=16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(in_features, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, embed_dim)
        )
        self.projector = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim)
        )

    def forward(self, x):
        h = self.encoder(x)
        z = self.projector(h)
        return h, z

class SelfSupervisedContrastiveClassifier(BaseEstimator, ClassifierMixin):
    """
    Self-Supervised Contrastive Representation Learning (SCARF/SimCLR style).
    Phase 1: Learns representations without any labels via contrastive infoNCE loss
             over feature corruption/jittering.
    Phase 2: Trains a lightweight linear probe on the learned frozen embeddings.
    """
    def __init__(self, embed_dim=16, temperature=0.1, epochs=60, lr=0.01, random_state=42):
        self.embed_dim = embed_dim
        self.temperature = temperature
        self.epochs = epochs
        self.lr = lr
        self.random_state = random_state

    def fit(self, X, y):
        torch.manual_seed(self.random_state)
        np.random.seed(self.random_state)
        
        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X)
        self.classes_ = np.unique(y)
        
        in_features = X.shape[1]
        self.model_ = ContrastiveEncoder(in_features, self.embed_dim)
        optimizer = optim.Adam(self.model_.parameters(), lr=self.lr)
        
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
        n_samples = len(X)
        batch_size = min(64, n_samples)
        
        # Self-supervised contrastive pretraining (NO labels used here!)
        self.model_.train()
        for epoch in range(self.epochs):
            indices = np.random.permutation(n_samples)
            for i in range(0, n_samples - batch_size + 1, batch_size):
                batch_x = X_tensor[indices[i:i + batch_size]]
                
                # Create 2 augmented views via feature jitter & random swap noise
                noise1 = torch.randn_like(batch_x) * 0.15
                noise2 = torch.randn_like(batch_x) * 0.15
                view1 = batch_x + noise1
                view2 = batch_x + noise2
                
                _, z1 = self.model_(view1)
                _, z2 = self.model_(view2)
                
                z1 = nn.functional.normalize(z1, dim=1)
                z2 = nn.functional.normalize(z2, dim=1)
                
                # SimCLR InfoNCE loss
                sim_matrix = torch.matmul(z1, z2.T) / self.temperature
                labels = torch.arange(batch_size, device=sim_matrix.device)
                loss = nn.functional.cross_entropy(sim_matrix, labels)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
        # Phase 2: Extract representations and fit linear probe
        self.model_.eval()
        with torch.no_grad():
            embeddings, _ = self.model_(X_tensor)
            emb_np = embeddings.numpy()
            
        self.probe_ = LogisticRegression(random_state=self.random_state)
        self.probe_.fit(emb_np, y)
        return self

    def predict_proba(self, X):
        self.model_.eval()
        X_scaled = self.scaler_.transform(X)
        with torch.no_grad():
            embeddings, _ = self.model_(torch.tensor(X_scaled, dtype=torch.float32))
            emb_np = embeddings.numpy()
        return self.probe_.predict_proba(emb_np)

    def predict(self, X):
        self.model_.eval()
        X_scaled = self.scaler_.transform(X)
        with torch.no_grad():
            embeddings, _ = self.model_(torch.tensor(X_scaled, dtype=torch.float32))
            emb_np = embeddings.numpy()
        return self.probe_.predict(emb_np)

class UnsupervisedGMMClassifier(BaseEstimator, ClassifierMixin):
    """
    Unsupervised Probabilistic Clustering via Gaussian Mixture Models (GMM)
    with minimum-entropy cluster-to-label alignment.
    """
    def __init__(self, n_components=4, covariance_type='full', random_state=42):
        self.n_components = n_components
        self.covariance_type = covariance_type
        self.random_state = random_state

    def fit(self, X, y):
        self.scaler_ = StandardScaler()
        X_scaled = self.scaler_.fit_transform(X)
        self.classes_ = np.unique(y)
        
        self.gmm_ = GaussianMixture(
            n_components=self.n_components,
            covariance_type=self.covariance_type,
            random_state=self.random_state
        )
        cluster_preds = self.gmm_.fit_predict(X_scaled)
        
        # Map each cluster to the majority true class
        self.cluster_map_ = {}
        for c in range(self.n_components):
            mask = (cluster_preds == c)
            if np.sum(mask) > 0:
                majority = np.bincount(y[mask]).argmax()
                self.cluster_map_[c] = majority
            else:
                self.cluster_map_[c] = self.classes_[0]
        return self

    def predict(self, X):
        X_scaled = self.scaler_.transform(X)
        cluster_preds = self.gmm_.predict(X_scaled)
        return np.array([self.cluster_map_[c] for c in cluster_preds])

    def predict_proba(self, X):
        X_scaled = self.scaler_.transform(X)
        gmm_probs = self.gmm_.predict_proba(X_scaled)
        probs = np.zeros((X.shape[0], len(self.classes_)))
        for c, cls_idx in self.cluster_map_.items():
            col = np.where(self.classes_ == cls_idx)[0][0]
            probs[:, col] += gmm_probs[:, c]
        # Normalize
        row_sums = probs.sum(axis=1, keepdims=True) + 1e-12
        return probs / row_sums
