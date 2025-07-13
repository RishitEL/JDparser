from __future__ import annotations

import numpy as np
from typing import Dict, Any, List
from tqdm import tqdm

from src.utils.embedding_utils import embed_texts, aggregate_mean
from src.extractors.feature_extraction import jd_to_embed_payload, resume_to_embed_payload
from src.extractors.experience_utils import estimate_years_experience, parse_required_years
from src.extractors.education_utils import highest_degree, required_degree, meets_degree_requirement
from config.weight_loader import get_config


class ResumeJDMatcher:
    def __init__(self, config_path: str | None = None):
        self.config_path = config_path

    # --------------------------------------------------
    # Vectorisation helpers
    # --------------------------------------------------

    def _vectorize_resume(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        payload = resume_to_embed_payload(resume)

        skill_vecs = embed_texts(payload["skill_texts"])
        exp_vecs = embed_texts(payload["exp_bullets"])
        proj_vecs = embed_texts(payload["proj_bullets"])
        sent_vecs = np.vstack([exp_vecs, proj_vecs]) if (exp_vecs.size + proj_vecs.size) else np.empty((0, 384))

        features = {
            "skill_vecs": skill_vecs.astype(np.float32),  # individual skill vectors
            "skill_vec": aggregate_mean(skill_vecs),      # mean vector (for DB)
            "exp_vec": aggregate_mean(exp_vecs),
            "sentence_vecs": sent_vecs.astype(np.float32),
            "years_experience": estimate_years_experience(resume),
            "degree_level": highest_degree(resume),
        }
        return features

    def _vectorize_jd(self, jd: Dict[str, Any]) -> Dict[str, Any]:
        payload = jd_to_embed_payload(jd)

        jd_skill_vecs = embed_texts(payload["skill_texts"])
        jd_bullet_vecs = embed_texts(payload["bullet_texts"])

        features = {
            "skill_vecs": jd_skill_vecs.astype(np.float32),  # individual JD skill vectors
            "skill_vec": aggregate_mean(jd_skill_vecs),      # mean vector (for DB)
            "exp_vec": aggregate_mean(jd_bullet_vecs),
            "sentence_vecs": jd_bullet_vecs.astype(np.float32),
            "years_required": parse_required_years(jd),
            "degree_required": required_degree(jd),
        }
        return features

    # --------------------------------------------------
    # Similarity helpers
    # --------------------------------------------------

    @staticmethod
    def _cosine(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b)) if a.any() and b.any() else 0.0

    @staticmethod
    def _skill_coverage(jd_vecs: np.ndarray, res_vecs: np.ndarray) -> float:
        """
        Coverage = mean over JD skills of the best-matching résumé skill.
        Returns 0 if either side is empty.
        """
        if jd_vecs.size == 0 or res_vecs.size == 0:
            return 0.0
        sim_matrix = jd_vecs @ res_vecs.T               # (x, n)
        best_for_each_jd = sim_matrix.max(axis=1)       # (x,)
        return float(best_for_each_jd.mean())

    @staticmethod
    def _topk_sentence_similarity(jd_vecs: np.ndarray, res_vecs: np.ndarray, k: int = 20) -> float:
        if jd_vecs.size == 0 or res_vecs.size == 0:
            return 0.0
        sims = jd_vecs @ res_vecs.T  # (m, n)
        topk = np.partition(sims, -k, axis=None)[-k:]
        return float(topk.mean())

    # --------------------------------------------------
    # Public scoring API
    # --------------------------------------------------

    def score(self, resume: Dict[str, Any], jd: Dict[str, Any]) -> float:
        cfg = get_config(self.config_path)
        weights = cfg["weights"]
        penalties = cfg["penalties"]

        resume_f = self._vectorize_resume(resume)
        jd_f = self._vectorize_jd(jd)

        # Use skill coverage instead of mean-vector similarity
        skill_sim = self._skill_coverage(jd_f["skill_vecs"], resume_f["skill_vecs"])
        exp_sim = self._cosine(resume_f["exp_vec"], jd_f["exp_vec"])
        sent_sim = self._topk_sentence_similarity(jd_f["sentence_vecs"], resume_f["sentence_vecs"], k=20)
        edu_match = 1.0 if meets_degree_requirement(resume_f["degree_level"], jd_f["degree_required"]) else 0.0

        year_gap = max(0, jd_f["years_required"] - resume_f["years_experience"])

        final = (
            weights.get("skill_similarity", 0) * skill_sim
            + weights.get("exp_similarity", 0) * exp_sim
            + weights.get("education_match", 0) * edu_match
            + weights.get("sentence_similarity", 0) * sent_sim
            + penalties.get("lacking_years", 0) * year_gap
        )
        return round(final, 4)

    def rank_resumes(self, resumes: List[Dict[str, Any]], jd: Dict[str, Any]) -> List[tuple[str, float]]:
        """Return list of (resume_id_or_index, score) sorted descending."""
        scores = []
        for idx, res in enumerate(tqdm(resumes, desc="Scoring resumes")):
            s = self.score(res, jd)
            scores.append((idx, s))
        scores.sort(key=lambda t: t[1], reverse=True)
        return scores 