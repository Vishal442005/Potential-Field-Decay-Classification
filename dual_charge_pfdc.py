import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.linear_model import LogisticRegression

class DualChargePFDC(BaseEstimator, ClassifierMixin):
    """
    Upgraded Potential Field Decay Classifier (PFDC) with Dual Support Charge Learning
    and Dimension-Aware Bandwidth Scaling.
    
    Resolves the high-dimensional accuracy gap by:
    1. Learning individual sample charge magnitudes (a_i >= 0), pruning interior
       redundancy and focusing potential energy on active boundary centers.
    2. Learning the ambient ground reference potential (bias b), eliminating
       the zero-threshold bias on imbalanced or clumpy feature manifolds.
    3. Coupling the decay shell to ambient dimension: R_decay = sqrt(D * Var(X)).
    """
    def __init__(self, core_ratio=0.15, decay_rate=2.5, gamma_blend=0.5, C=2.0):
        self.core_ratio = core_ratio
        self.decay_rate = decay_rate
        self.gamma_blend = gamma_blend
        self.C = C

    def fit(self, X, y):
        self.scaler_ = StandardScaler()
        self.X_train_ = self.scaler_.fit_transform(X)
        self.classes_ = np.unique(y)
        self.y_train_ = np.asarray(y)
        self.y_sign_ = np.where(self.y_train_ == self.classes_[1], 1.0, -1.0)
        
        n_samples, n_features = self.X_train_.shape
        
        # 1. Dimension-Aware Bandwidth Calibration
        gamma_scale = 1.0 / (n_features * self.X_train_.var())
        self.r_decay_ = 1.0 / np.sqrt(gamma_scale)
        self.r_core_ = self.r_decay_ * self.core_ratio
        self.gamma_scale_ = gamma_scale
        
        # 2. Pairwise potential kernel matrix
        D = euclidean_distances(self.X_train_, self.X_train_)
        mask_decay = (D > self.r_core_) & (D <= (self.r_core_ + self.r_decay_))
        K_pfdc = np.zeros_like(D)
        K_pfdc[D <= self.r_core_] = 1.0
        if np.any(mask_decay):
            u = (D[mask_decay] - self.r_core_) / self.r_decay_
            K_pfdc[mask_decay] = np.exp(-self.decay_rate * u)
        np.fill_diagonal(K_pfdc, 0.0)
        
        K_rbf = np.exp(-self.gamma_scale_ * (D ** 2))
        np.fill_diagonal(K_rbf, 0.0)
        
        K_net = self.gamma_blend * K_pfdc + (1.0 - self.gamma_blend) * K_rbf
        H = K_net * self.y_sign_[np.newaxis, :]
        
        # 3. Optimize individual support charges a_i and bias b
        self.solver_ = LogisticRegression(C=self.C, max_iter=300, fit_intercept=True)
        self.solver_.fit(H, self.y_train_)
        
        # Learned physical parameters
        self.support_charges_ = self.solver_.coef_[0]
        self.bias_ = self.solver_.intercept_[0]
        return self

    def predict_potential(self, X):
        X_sc = self.scaler_.transform(X)
        D = euclidean_distances(X_sc, self.X_train_)
        
        mask_decay = (D > self.r_core_) & (D <= (self.r_core_ + self.r_decay_))
        K_pfdc = np.zeros_like(D)
        K_pfdc[D <= self.r_core_] = 1.0
        if np.any(mask_decay):
            u = (D[mask_decay] - self.r_core_) / self.r_decay_
            K_pfdc[mask_decay] = np.exp(-self.decay_rate * u)
            
        K_rbf = np.exp(-self.gamma_scale_ * (D ** 2))
        K_net = self.gamma_blend * K_pfdc + (1.0 - self.gamma_blend) * K_rbf
        H = K_net * self.y_sign_[np.newaxis, :]
        return H @ self.support_charges_ + self.bias_

    def predict(self, X):
        return np.where(self.predict_potential(X) >= 0.0, self.classes_[1], self.classes_[0])

    def predict_proba(self, X):
        pot = self.predict_potential(X)
        prob_pos = 1.0 / (1.0 + np.exp(-np.clip(pot, -15, 15)))
        return np.column_stack([1.0 - prob_pos, prob_pos])
