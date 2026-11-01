import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import StandardScaler

class DynamicPFDC(BaseEstimator, ClassifierMixin):
    """
    Potential Field Decay Classifier (PFDC) with Dynamic Parameter Evolution.
    
    Supports:
    - Core radius (signed, with polarity +1 / -1 and magnitude |R_core|)
    - Decay radius R_decay > 0
    - Extended parameters: alpha (decay shape exponent), gamma (kernel mixing)
    - 3 Dynamic Learning-Rate Cases:
        * Case 1: 'fixed' -> constant learning rates
        * Case 2: 'halved' -> lr halved on boundary crossing / sign shift
        * Case 3: 'exponential_accelerating' -> lr decreases exponentially with accelerating penalty (c^2)
    """
    def __init__(
        self,
        r_core_init=0.6,
        r_decay_init=1.2,
        decay_rate=5.0,
        alpha=1.0,
        gamma=1.0,
        rbf_beta=1.0,
        lr_core_init=0.08,
        lr_decay_init=0.05,
        lr_case="fixed", # "fixed", "halved", "exponential_accelerating"
        accel_beta=0.15,
        max_epochs=120,
        balance_charges=True,
        random_state=42
    ):
        self.r_core_init = r_core_init
        self.r_decay_init = r_decay_init
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.gamma = gamma
        self.rbf_beta = rbf_beta
        self.lr_core_init = lr_core_init
        self.lr_decay_init = lr_decay_init
        self.lr_case = lr_case
        self.accel_beta = accel_beta
        self.max_epochs = max_epochs
        self.balance_charges = balance_charges
        self.random_state = random_state

    def _sigmoid(self, z):
        return 1.0 / (1.0 + np.exp(-np.clip(z, -20.0, 20.0)))

    def _compute_influence(self, dists, r_core_mag, r_decay):
        """
        Computes the piecewise radial influence:
        Zone 1: d <= r_core -> 1.0
        Zone 2: r_core < d <= r_core + r_decay -> exp(-lambda * ((d - r_core)/r_decay)^alpha)
        Zone 3: d > r_core + r_decay -> 0.0
        """
        influence = np.zeros_like(dists, dtype=float)
        
        # Zone 1
        mask_core = (dists <= r_core_mag)
        influence[mask_core] = 1.0
        
        # Zone 2
        outer_limit = r_core_mag + r_decay
        mask_decay = (dists > r_core_mag) & (dists <= outer_limit)
        
        if np.any(mask_decay):
            u = (dists[mask_decay] - r_core_mag) / np.maximum(r_decay, 1e-6)
            influence[mask_decay] = np.exp(-self.decay_rate * (u ** self.alpha))
            
        return influence, mask_decay

    def fit(self, X, y, eval_set=None):
        """
        Trains the PFDC model using analytical gradients and records epoch-by-epoch
        trajectories for loss, accuracy, radii, learning rates, and sign-changes.
        """
        self.scaler_ = StandardScaler()
        self.X_train_ = self.scaler_.fit_transform(X)
        self.y_train_ = np.asarray(y)
        self.classes_ = np.unique(self.y_train_)
        
        if len(self.classes_) != 2:
            raise ValueError("DynamicPFDC currently focuses on binary classification (expandable via OvR).")
            
        # Target class is classes_[1] (+1), opposing is classes_[0] (-1)
        self.pos_class_ = self.classes_[1]
        n_samples = len(self.y_train_)
        pos_mask = (self.y_train_ == self.pos_class_)
        neg_mask = ~pos_mask
        
        if self.balance_charges:
            n_pos = np.sum(pos_mask)
            n_neg = np.sum(neg_mask)
            q_pos = (n_samples / (2.0 * n_pos)) if n_pos > 0 else 1.0
            q_neg = -(n_samples / (2.0 * n_neg)) if n_neg > 0 else -1.0
            self.charges_ = np.where(pos_mask, q_pos, q_neg)
        else:
            self.charges_ = np.where(pos_mask, 1.0, -1.0)

        # Precompute pairwise distances among training points (N x N)
        diffs = self.X_train_[:, np.newaxis, :] - self.X_train_[np.newaxis, :, :]
        train_dists = np.linalg.norm(diffs, axis=2)
        
        # Prepare eval set if provided
        if eval_set is not None:
            X_val, y_val = eval_set
            X_val_scaled = self.scaler_.transform(X_val)
            val_diffs = X_val_scaled[:, np.newaxis, :] - self.X_train_[np.newaxis, :, :]
            val_dists = np.linalg.norm(val_diffs, axis=2)
            y_val_bin = (y_val == self.pos_class_).astype(float)
        else:
            val_dists, y_val_bin = None, None

        y_train_bin = (self.y_train_ == self.pos_class_).astype(float)

        # Initialize trainable parameters
        # r_core has signed value (e.g., initial +0.6 or -0.6)
        r_core = float(self.r_core_init)
        r_decay = float(self.r_decay_init)
        
        lr_core = float(self.lr_core_init)
        lr_decay = float(self.lr_decay_init)
        
        # History tracking
        self.history_ = {
            "epoch": [],
            "loss": [],
            "val_loss": [],
            "train_acc": [],
            "val_acc": [],
            "r_core": [],
            "r_core_mag": [],
            "r_decay": [],
            "lr_core": [],
            "lr_decay": [],
            "grad_core": [],
            "grad_decay": [],
            "sign_changes_core": [],
            "sign_changes_decay": [],
            "sign_shift_events": []
        }
        
        sign_changes_core = 0
        sign_changes_decay = 0
        prev_sign_core = np.sign(r_core)
        prev_grad_core_sign = 0
        prev_grad_decay_sign = 0

        for epoch in range(1, self.max_epochs + 1):
            r_core_mag = np.maximum(np.abs(r_core), 0.01)
            core_sign = np.sign(r_core) if r_core != 0 else 1.0
            
            # 1. Compute Potential on training points
            inf, mask_decay = self._compute_influence(train_dists, r_core_mag, r_decay)
            p_pfdc = np.sum(inf * self.charges_[np.newaxis, :], axis=1)
            
            # Kernel mixing (optional RBF component)
            if self.gamma < 1.0:
                p_rbf = np.sum(np.exp(-self.rbf_beta * (train_dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
                pot = self.gamma * p_pfdc + (1.0 - self.gamma) * p_rbf
            else:
                pot = p_pfdc
                
            probs = self._sigmoid(pot)
            preds = (pot >= 0).astype(int)
            train_acc = np.mean(preds == y_train_bin)
            
            # Binary Cross Entropy Loss
            eps = 1e-12
            loss = -np.mean(y_train_bin * np.log(probs + eps) + (1.0 - y_train_bin) * np.log(1.0 - probs + eps))
            
            # Validation metrics
            if val_dists is not None:
                val_inf, _ = self._compute_influence(val_dists, r_core_mag, r_decay)
                val_pfdc = np.sum(val_inf * self.charges_[np.newaxis, :], axis=1)
                if self.gamma < 1.0:
                    val_rbf = np.sum(np.exp(-self.rbf_beta * (val_dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
                    val_pot = self.gamma * val_pfdc + (1.0 - self.gamma) * val_rbf
                else:
                    val_pot = val_pfdc
                val_probs = self._sigmoid(val_pot)
                val_preds = (val_pot >= 0).astype(int)
                val_acc = np.mean(val_preds == y_val_bin)
                val_loss = -np.mean(y_val_bin * np.log(val_probs + eps) + (1.0 - y_val_bin) * np.log(1.0 - val_probs + eps))
            else:
                val_loss, val_acc = None, None

            # 2. Compute Analytical Gradients w.r.t r_core and r_decay
            # Error signal: delta_m = probs_m - y_m
            delta = probs - y_train_bin # shape (N,)
            
            # Grad w.r.t I_ij in Zone 2:
            # u = (d - r_core_mag) / r_decay
            # dI/d(r_core_mag) = (lambda * alpha / r_decay) * u^(alpha-1) * exp(-lambda * u^alpha)
            # dI/d(r_decay)    = (lambda * alpha / r_decay) * u^alpha     * exp(-lambda * u^alpha)
            dI_dcore = np.zeros_like(train_dists)
            dI_ddecay = np.zeros_like(train_dists)
            
            if np.any(mask_decay):
                u_decay = (train_dists[mask_decay] - r_core_mag) / np.maximum(r_decay, 1e-6)
                u_clamped = np.maximum(u_decay, 1e-6)
                decay_exp = np.exp(-self.decay_rate * (u_clamped ** self.alpha))
                factor = (self.decay_rate * self.alpha / np.maximum(r_decay, 1e-6)) * decay_exp
                
                dI_dcore[mask_decay] = factor * (u_clamped ** (self.alpha - 1.0))
                dI_ddecay[mask_decay] = factor * (u_clamped ** self.alpha)

            # dP_m / dTheta = sum_i q_i * (dI_mi / dTheta)
            dP_dcore = np.sum(dI_dcore * self.charges_[np.newaxis, :], axis=1) # shape (N,)
            dP_ddecay = np.sum(dI_ddecay * self.charges_[np.newaxis, :], axis=1) # shape (N,)
            
            if self.gamma < 1.0:
                dP_dcore *= self.gamma
                dP_ddecay *= self.gamma

            grad_core_mag = np.mean(delta * dP_dcore)
            grad_decay = np.mean(delta * dP_ddecay)
            
            # Signed core update gradient
            grad_core = core_sign * grad_core_mag
            
            # Clip gradients for numerical stability
            grad_core = np.clip(grad_core, -5.0, 5.0)
            grad_decay = np.clip(grad_decay, -5.0, 5.0)

            # 3. Detect Boundary Crossing & Sign Shifts
            curr_grad_core_sign = np.sign(grad_core)
            curr_grad_decay_sign = np.sign(grad_decay)
            
            sign_shifted_core = False
            sign_shifted_decay = False
            
            # Sign shift for core occurs if gradient flips sign OR radius crosses 0
            if epoch > 1 and prev_grad_core_sign != 0 and curr_grad_core_sign != prev_grad_core_sign:
                sign_shifted_core = True
                sign_changes_core += 1
                
            if epoch > 1 and prev_grad_decay_sign != 0 and curr_grad_decay_sign != prev_grad_decay_sign:
                sign_shifted_decay = True
                sign_changes_decay += 1
                
            # 4. Apply the 3 Dynamic Learning-Rate Cases
            if self.lr_case == "fixed":
                # Case 1: Learning rates remain fixed
                lr_core = self.lr_core_init
                lr_decay = self.lr_decay_init
                
            elif self.lr_case == "halved":
                # Case 2: Halved whenever crossing boundary / sign shift
                if sign_shifted_core:
                    lr_core = 0.5 * lr_core
                if sign_shifted_decay:
                    lr_decay = 0.5 * lr_decay
                    
            elif self.lr_case == "exponential_accelerating":
                # Case 3: Exponential decrease with accelerating penalty after each sign change
                # Multiplier = exp(-beta * c^2)
                # First change: small drop. 2nd change: big drop. 3rd change: very big drop.
                mult_core = np.exp(-self.accel_beta * (sign_changes_core ** 2))
                mult_decay = np.exp(-self.accel_beta * (sign_changes_decay ** 2))
                lr_core = self.lr_core_init * mult_core
                lr_decay = self.lr_decay_init * mult_decay
                
            else:
                raise ValueError(f"Unknown lr_case: {self.lr_case}")

            # Record history
            self.history_["epoch"].append(epoch)
            self.history_["loss"].append(loss)
            self.history_["val_loss"].append(val_loss)
            self.history_["train_acc"].append(train_acc)
            self.history_["val_acc"].append(val_acc)
            self.history_["r_core"].append(r_core)
            self.history_["r_core_mag"].append(r_core_mag)
            self.history_["r_decay"].append(r_decay)
            self.history_["lr_core"].append(lr_core)
            self.history_["lr_decay"].append(lr_decay)
            self.history_["grad_core"].append(grad_core)
            self.history_["grad_decay"].append(grad_decay)
            self.history_["sign_changes_core"].append(sign_changes_core)
            self.history_["sign_changes_decay"].append(sign_changes_decay)
            self.history_["sign_shift_events"].append(sign_shifted_core or sign_shifted_decay)

            # Update parameters
            r_core = r_core - lr_core * grad_core
            r_decay = r_decay - lr_decay * grad_decay
            
            # Ensure r_decay stays positive and bounded
            r_decay = np.clip(r_decay, 0.05, 10.0)
            # Clip r_core to reasonable bounds
            r_core = np.clip(r_core, -5.0, 5.0)

            # Check if r_core flipped sign relative to previous step
            curr_sign_core = np.sign(r_core)
            if curr_sign_core != 0 and prev_sign_core != 0 and curr_sign_core != prev_sign_core:
                # Boundary cross event
                if self.lr_case == "halved" and not sign_shifted_core:
                    lr_core = 0.5 * lr_core
                elif self.lr_case == "exponential_accelerating" and not sign_shifted_core:
                    sign_changes_core += 1
                    lr_core = self.lr_core_init * np.exp(-self.accel_beta * (sign_changes_core ** 2))

            prev_sign_core = curr_sign_core
            prev_grad_core_sign = curr_grad_core_sign
            prev_grad_decay_sign = curr_grad_decay_sign

        # Final parameters
        self.r_core_final_ = r_core
        self.r_core_mag_final_ = np.maximum(np.abs(r_core), 0.01)
        self.r_decay_final_ = r_decay
        self.lr_core_final_ = lr_core
        self.lr_decay_final_ = lr_decay
        return self

    def predict_potential(self, X):
        """ Computes net scalar potential on arbitrary query points X. """
        X_scaled = self.scaler_.transform(X)
        diffs = X_scaled[:, np.newaxis, :] - self.X_train_[np.newaxis, :, :]
        dists = np.linalg.norm(diffs, axis=2)
        
        inf, _ = self._compute_influence(dists, self.r_core_mag_final_, self.r_decay_final_)
        p_pfdc = np.sum(inf * self.charges_[np.newaxis, :], axis=1)
        
        if self.gamma < 1.0:
            p_rbf = np.sum(np.exp(-self.rbf_beta * (dists ** 2)) * self.charges_[np.newaxis, :], axis=1)
            pot = self.gamma * p_pfdc + (1.0 - self.gamma) * p_rbf
        else:
            pot = p_pfdc
        return pot

    def predict_proba(self, X):
        """ Returns calibrated class probabilities via potential sigmoid. """
        pot = self.predict_potential(X)
        p1 = self._sigmoid(pot)
        p0 = 1.0 - p1
        return np.column_stack([p0, p1])

    def predict(self, X):
        """ Decision rule: pot >= 0 -> class 1, else class 0 """
        pot = self.predict_potential(X)
        preds = np.where(pot >= 0, self.classes_[1], self.classes_[0])
        return preds

    def compute_force_vectors(self, X):
        """ Computes net attraction / repulsion directional force vector field. """
        X_scaled = self.scaler_.transform(X)
        diffs = self.X_train_[np.newaxis, :, :] - X_scaled[:, np.newaxis, :]
        dists = np.linalg.norm(diffs, axis=2)
        unit_vecs = diffs / (dists[:, :, np.newaxis] + 1e-9)
        
        inf, _ = self._compute_influence(dists, self.r_core_mag_final_, self.r_decay_final_)
        weighted = unit_vecs * (inf * self.charges_[np.newaxis, :])[:, :, np.newaxis]
        net_force = np.sum(weighted, axis=1)
        return net_force
