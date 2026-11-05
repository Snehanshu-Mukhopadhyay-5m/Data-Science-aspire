import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

class HybridFeaturePipeline:
    def __init__(self, smoothing_m: float = 25.0, n_svd_components: int = 16):
        self.smoothing_m = smoothing_m
        self.n_svd_components = n_svd_components
        self.global_prior_: float = 0.15
        self.company_stats_: pd.DataFrame = pd.DataFrame()
        self.tfidf = TfidfVectorizer(max_features=2000, stop_words="english", ngram_range=(1, 2))
        self.svd = TruncatedSVD(n_components=n_svd_components, random_state=42)

    @staticmethod
    def add_point_in_time_velocity(df: pd.DataFrame) -> pd.DataFrame:
        """Computes historical ticket velocity strictly prior to each row's timestamp."""
        df = df.copy()
        df["date_received"] = pd.to_datetime(df["date_received"])
        df = df.sort_values("date_received").reset_index(drop=True)

        # Prior cumulative complaint count for this company (shifted by 1 to prevent leakage)
        df["company_prior_ticket_count"] = df.groupby("company").cumcount()

        # Expanding historical escalation mean strictly prior to current ticket
        prior_escalations = (
            df.groupby("company")["target_escalated"]
            .apply(lambda s: s.shift(1).expanding().mean())
            .reset_index(level=0, drop=True)
        )
        df["company_pit_escalation_rate"] = prior_escalations
        return df

    def fit(self, df: pd.DataFrame, target_col: str = "target_escalated"):
        """Fits Empirical Bayes encoding stats and NLP SVD projection on Training Data ONLY."""
        self.global_prior_ = float(df[target_col].mean())

        # Compute Micci-Barreca Empirical Bayes smoothed encoding per company
        stats = df.groupby("company")[target_col].agg(n_i="count", n_iY="sum")
        stats["local_mean"] = stats["n_iY"] / stats["n_i"]
        stats["lambda_weight"] = stats["n_i"] / (stats["n_i"] + self.smoothing_m)
        stats["eb_encoded_company"] = (
            stats["lambda_weight"] * stats["local_mean"]
            + (1.0 - stats["lambda_weight"]) * self.global_prior_
        )
        self.company_stats_ = stats[["eb_encoded_company", "n_i"]]

        # Fit TF-IDF + TruncatedSVD on training narratives
        narratives = df["complaint_what_happened"].fillna("")
        tfidf_matrix = self.tfidf.fit_transform(narratives)
        self.svd.fit(tfidf_matrix)
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms any split using frozen training parameters."""
        out = df.copy()

        # 1. Merge Empirical Bayes Company Encoding
        out = out.merge(self.company_stats_, on="company", how="left")
        out["eb_encoded_company"] = out["eb_encoded_company"].fillna(self.global_prior_)
        out["company_train_volume"] = out["n_i"].fillna(0)

        # 2. MNAR Narrative Signals & Urgency Lexicon Counts
        raw_text = out["complaint_what_happened"].fillna("")
        out["has_narrative_mnar"] = out["complaint_what_happened"].notna().astype(int)
        out["narrative_word_count"] = raw_text.str.split().str.len()
        out["urgency_keyword_hits"] = raw_text.str.count(
            r"(?i)\b(fraud|unauthorized|attorney|lawyer|sue|theft|fcra|breach|stolen)\b"
        )

        # 3. Dense SVD Text Embeddings
        tfidf_mat = self.tfidf.transform(raw_text)
        svd_vecs = self.svd.transform(tfidf_mat)
        for i in range(self.n_svd_components):
            out[f"nlp_svd_{i}"] = svd_vecs[:, i]

        # 4. Frequency encode low-cardinality categoricals
        for col in ["product", "issue", "submitted_via"]:
            out[col] = out[col].astype("category")

        feature_cols = (
            ["eb_encoded_company", "company_train_volume", "has_narrative_mnar",
             "narrative_word_count", "urgency_keyword_hits", "product", "issue", "submitted_via"]
            + [f"nlp_svd_{i}" for i in range(self.n_svd_components)]
        )
        return out[feature_cols]