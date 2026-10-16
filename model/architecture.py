"""
DeepLearnX Neural Network Architecture
Multi-Branch Cognitive Neural Network (DeepCognitiveNet)
Combines:
- Sequential Response Pattern Bi-GRU with Self-Attention Pooling
- Multi-Tier Structured Cognitive Feature ANN
- Multi-Task Cognitive Prediction Heads (State, Misconception, Prerequisite Risk)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class AttentionPooling(nn.Module):
    """Self-attention mechanism to pool sequence steps into a single latent vector."""
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attn = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1)
        )

    def forward(self, x, mask=None):
        # x: [batch_size, seq_len, hidden_dim]
        scores = self.attn(x) # [batch_size, seq_len, 1]
        if mask is not None:
            scores = scores.masked_fill(~mask.unsqueeze(-1), -1e9)
        weights = F.softmax(scores, dim=1) # [batch_size, seq_len, 1]
        pooled = torch.sum(x * weights, dim=1) # [batch_size, hidden_dim]
        return pooled, weights

class DeepCognitiveNet(nn.Module):
    def __init__(
        self,
        num_concepts: int = 12,
        num_tiers: int = 3,
        num_misconceptions: int = 11, # 0=None, 1..10=misconceptions
        structured_dim: int = 9,
        gru_hidden: int = 48,
        num_classes: int = 4
    ):
        super().__init__()
        
        # --- BRANCH 1: Sequential Cognitive Response Bi-GRU ---
        self.concept_emb = nn.Embedding(num_concepts, 16)
        self.tier_emb = nn.Embedding(num_tiers, 8)
        self.misc_emb = nn.Embedding(num_misconceptions, 8)
        
        # Continuous response features: [is_correct, norm_response_time, norm_confidence] -> 3 dims
        seq_step_dim = 16 + 8 + 8 + 3 # 35
        self.seq_proj = nn.Sequential(
            nn.Linear(seq_step_dim, 48),
            nn.LayerNorm(48),
            nn.GELU()
        )
        
        self.bigru = nn.GRU(
            input_size=48,
            hidden_size=gru_hidden,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.15
        )
        
        gru_out_dim = gru_hidden * 2 # 96
        self.attn_pool = AttentionPooling(gru_out_dim)
        
        # --- BRANCH 2: Structured Cognitive Feature ANN ---
        self.structured_ann = nn.Sequential(
            nn.Linear(structured_dim, 64),
            nn.BatchNorm1d(64),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(64, 48),
            nn.GELU()
        )
        
        # --- MULTIMODAL COGNITIVE FUSION ---
        fusion_dim = gru_out_dim + 48 # 96 + 48 = 144
        self.fusion = nn.Sequential(
            nn.Linear(fusion_dim, 96),
            nn.LayerNorm(96),
            nn.GELU(),
            nn.Dropout(0.2)
        )
        
        # --- MULTI-TASK PREDICTION HEADS ---
        # Head 1: Cognitive State (Genuine Mastery, False Mastery, Misconception, Knowledge Gap)
        self.state_head = nn.Sequential(
            nn.Linear(96, 48),
            nn.GELU(),
            nn.Linear(48, num_classes)
        )
        
        # Head 2: Misconception Category Multi-class Classifier
        self.misc_head = nn.Sequential(
            nn.Linear(96, 48),
            nn.GELU(),
            nn.Linear(48, num_misconceptions)
        )
        
        # Head 3: Prerequisite Gap Risk (Continuous Regression)
        self.prereq_head = nn.Sequential(
            nn.Linear(96, 32),
            nn.GELU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, seq_concepts, seq_tiers, seq_miscs, seq_cont, structured_feats):
        """
        Forward pass of DeepCognitiveNet.
        Args:
            seq_concepts: [B, T]
            seq_tiers: [B, T]
            seq_miscs: [B, T]
            seq_cont: [B, T, 3] (is_correct, time, confidence)
            structured_feats: [B, structured_dim]
        Returns:
            state_logits: [B, 4]
            misc_logits: [B, num_misconceptions]
            prereq_risk: [B, 1]
            attn_weights: [B, T, 1]
        """
        # Embeddings
        c_emb = self.concept_emb(seq_concepts)
        t_emb = self.tier_emb(seq_tiers)
        m_emb = self.misc_emb(seq_miscs)
        
        # Concatenate sequential step vector
        step_input = torch.cat([c_emb, t_emb, m_emb, seq_cont], dim=-1) # [B, T, 35]
        step_proj = self.seq_proj(step_input) # [B, T, 48]
        
        # Bi-GRU temporal encoding
        gru_out, _ = self.bigru(step_proj) # [B, T, 96]
        
        # Sequence Attention Pooling
        latent_seq, attn_weights = self.attn_pool(gru_out) # [B, 96]
        
        # Structured Cognitive ANN
        latent_struct = self.structured_ann(structured_feats) # [B, 48]
        
        # Multimodal Fusion
        fused = torch.cat([latent_seq, latent_struct], dim=-1) # [B, 144]
        latent_cognitive = self.fusion(fused) # [B, 96]
        
        # Multi-task predictions
        state_logits = self.state_head(latent_cognitive)
        misc_logits = self.misc_head(latent_cognitive)
        prereq_risk = self.prereq_head(latent_cognitive)
        
        return state_logits, misc_logits, prereq_risk, attn_weights
