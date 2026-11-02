import numpy as np

class ElectroPotentialFieldProjection:
    """
    Electro-Potential Field-Aligned Projection (EP-FAP).
    
    A novel, robust, physics-grounded 2D manifold projection designed specifically 
    for the Potential Field Decay Classifier (PFDC). Replaces variance-greedy,
    outlier-sensitive Principal Component Analysis (PCA) with an intrinsic physical 
    coordinate system aligned with the electro-potential gradient field.
    
    Mathematical Formulation:
    -------------------------
    1. Primary Axis (u_1) - Electrostatic Dipole / Recourse Axis:
       Aligned with the anisotropically-weighted difference between robust class medians:
           v_1 = W * (mu_+^med - mu_-^med)
           u_1 = v_1 / ||v_1||_2
       Physical Meaning: xi_1 = u_1^T (x - mu_0) directly measures the distance along the
       electrostatic separation dipole. Negative values lie in the Class 0 basin of
       attraction, while positive values lie in the Class 1 basin of attraction.
       
    2. Secondary Axis (u_2) - Robust Transverse Equipotential Axis:
       Constructed orthogonal to u_1 (u_2 perp u_1) using Huber-weighted robust scatter
       on the null space projection P_perp = I - u_1 u_1^T:
           S_perp = P_perp * [ sum_i psi_Huber(||z_i||) * (z_i z_i^T) / ||z_i||^2 ] * P_perp
       u_2 is the leading eigenvector of S_perp.
       Physical Meaning: xi_2 captures the transverse spread along the equipotential
       separatrix without distorting the flow lines of the conservative force field.
    """
    def __init__(self, huber_quantile=0.85, random_state=42):
        self.huber_quantile = huber_quantile
        self.random_state = random_state
        self.u1_ = None
        self.u2_ = None
        self.U_ = None
        self.origin_ = None
        self.feature_weights_ = None

    def fit(self, X, y, feature_weights=None, sample_charges=None):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y)
        n_samples, n_features = X.shape
        
        # Default anisotropic weights to uniform if not provided
        if feature_weights is None:
            self.feature_weights_ = np.ones(n_features, dtype=np.float64)
        else:
            self.feature_weights_ = np.asarray(feature_weights, dtype=np.float64)
            
        classes = np.unique(y)
        if len(classes) < 2:
            raise ValueError("EP-FAP requires at least 2 distinct classes.")
            
        # 1. Compute Robust Spatial Medians for each class
        # Coordinate-wise median is highly resistant to heavy-tailed outliers (breakdown point 50%)
        mask_0 = (y == classes[0])
        mask_1 = (y == classes[1])
        
        if sample_charges is not None:
            # Charge-weighted median / mean
            q0 = np.asarray(sample_charges)[mask_0]
            q1 = np.asarray(sample_charges)[mask_1]
            q0 = np.maximum(q0, 1e-4)
            q1 = np.maximum(q1, 1e-4)
            mu_0 = np.average(X[mask_0], axis=0, weights=q0)
            mu_1 = np.average(X[mask_1], axis=0, weights=q1)
        else:
            mu_0 = np.median(X[mask_0], axis=0)
            mu_1 = np.median(X[mask_1], axis=0)
            
        # Global robust center
        self.origin_ = 0.5 * (mu_0 + mu_1)
        
        # 2. Axis 1 (u_1): Anisotropic Electrostatic Dipole Axis
        # v_1 = W * (mu_1 - mu_0)
        v1 = self.feature_weights_ * (mu_1 - mu_0)
        norm_v1 = np.linalg.norm(v1)
        if norm_v1 < 1e-9:
            # Fallback to random orthogonal vector if centroids coincide
            rng = np.random.default_rng(self.random_state)
            v1 = rng.standard_normal(n_features)
            norm_v1 = np.linalg.norm(v1)
        self.u1_ = v1 / norm_v1
        
        # 3. Orthogonal Projection Operator onto Subspace perp to u_1
        # P_perp = I - u_1 u_1^T
        # We can implement matrix-vector multiplication without forming D x D matrix
        # (critical for D = 1,000!)
        
        # Centered data
        X_centered = X - self.origin_
        # Project each point: x_perp = x - (x . u1) * u1
        proj_u1 = np.dot(X_centered, self.u1_) # shape (N,)
        X_perp = X_centered - np.outer(proj_u1, self.u1_) # shape (N, D)
        
        # Apply anisotropic scaling: Z_perp = X_perp * sqrt(W)
        Z_perp = X_perp * np.sqrt(np.maximum(self.feature_weights_, 1e-6))
        
        # 4. Axis 2 (u_2): Robust Huber-Weighted Transverse Scatter
        # Compute norms for outlier downweighting
        norms_perp = np.linalg.norm(Z_perp, axis=1)
        huber_cutoff = np.quantile(norms_perp, self.huber_quantile)
        huber_cutoff = max(huber_cutoff, 1e-6)
        
        # Huber weights: w_h = 1 if r <= k else k / r
        weights_huber = np.ones(n_samples)
        outlier_mask = norms_perp > huber_cutoff
        weights_huber[outlier_mask] = huber_cutoff / norms_perp[outlier_mask]
        
        # We find the leading eigenvector of the weighted transverse scatter using
        # power iteration or randomized SVD (efficient for high D)
        Z_weighted = Z_perp * np.sqrt(weights_huber)[:, np.newaxis]
        
        # Power iteration to find dominant transverse direction
        rng = np.random.default_rng(self.random_state)
        u2 = rng.standard_normal(n_features)
        # Ensure orthogonal to u1
        u2 -= np.dot(u2, self.u1_) * self.u1_
        u2 /= (np.linalg.norm(u2) + 1e-9)
        
        for _ in range(30):
            # Multiply: w = Z_weighted^T * (Z_weighted * u2)
            temp = np.dot(Z_weighted, u2)
            w = np.dot(Z_weighted.T, temp)
            # Re-orthogonalize against u1
            w -= np.dot(w, self.u1_) * self.u1_
            norm_w = np.linalg.norm(w)
            if norm_w < 1e-9:
                break
            u2 = w / norm_w
            
        self.u2_ = u2
        
        # Combine into projection matrix U = [u1, u2] (D x 2)
        self.U_ = np.column_stack([self.u1_, self.u2_])
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=np.float64)
        X_centered = X - self.origin_
        return np.dot(X_centered, self.U_)

    def fit_transform(self, X, y, feature_weights=None, sample_charges=None):
        return self.fit(X, y, feature_weights, sample_charges).transform(X)

    def inverse_transform(self, X_2d):
        X_2d = np.asarray(X_2d, dtype=np.float64)
        return self.origin_ + np.dot(X_2d, self.U_.T)
