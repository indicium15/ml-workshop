"""
Synthetic student learning profile generator.
Produces 500 rows with realistic inter-feature correlations driven by a
latent academic-ability variable. Includes a deliberate mix of continuous,
integer, binary, and multi-level categorical columns so that workshops can
demonstrate mixed-type preprocessing (encoding + scaling together).
Output saved to ../sample_data/.
"""
import os
import numpy as np
import pandas as pd

np.random.seed(42)
n = 500


def _clip(arr, lo, hi):
    return np.clip(arr, lo, hi)


def _noise(scale, size):
    return np.random.normal(0, scale, size)


def _categorical_from_probs(categories, prob_matrix):
    """Draw one category per row given an (n, k) probability matrix."""
    prob_matrix = prob_matrix / prob_matrix.sum(axis=1, keepdims=True)
    indices = np.array([np.random.choice(len(categories), p=row) for row in prob_matrix])
    return np.array(categories)[indices]


# ── Latent ability (drives most correlations) ─────────────────────────────────
ability = np.random.normal(0, 1, n)

# ── Demographics ──────────────────────────────────────────────────────────────
student_id = np.arange(1000, 1000 + n)
age = np.random.randint(18, 26, n)
gender = np.random.choice(["Male", "Female", "Other"], n, p=[0.48, 0.48, 0.04])
year_of_study = np.random.randint(1, 5, n)
faculty = np.random.choice(
    ["Engineering", "Business", "Arts", "Science", "Education"], n
)
socioeconomic_index = np.random.randint(1, 6, n)
parental_education_level = np.random.randint(1, 6, n)

# ── NEW: Binary categorical — scholarship_holder ───────────────────────────────
# High-ability students more likely to hold a scholarship (logistic transform)
p_scholarship = 1 / (1 + np.exp(-1.5 * ability))
scholarship_holder = np.where(np.random.random(n) < p_scholarship, "Yes", "No")

# ── NEW: Nominal 3-level — accommodation_type ─────────────────────────────────
# On-campus students tend to have slightly higher tutorial attendance.
# Higher ability → marginally more likely to be on-campus (selection effect).
accom_probs = np.column_stack([
    _clip(0.30 + 0.08 * ability, 0.05, 0.65),   # On-campus
    _clip(0.45 - 0.03 * ability, 0.20, 0.65),   # Off-campus
    _clip(0.25 - 0.05 * ability, 0.05, 0.45),   # Family home
])
accommodation_type = _categorical_from_probs(
    ["On-campus", "Off-campus", "Family home"], accom_probs
)

# ── NEW: Nominal 4-level — learning_style ─────────────────────────────────────
# Intentionally mostly random — demonstrates that not every categorical predicts outcome.
learning_style = np.random.choice(
    ["Visual", "Auditory", "Reading-Writing", "Kinesthetic"],
    n, p=[0.40, 0.20, 0.30, 0.10],
)

# ── NEW: Ordinal-ish 4-level — internet_access_quality ────────────────────────
# Driven by socioeconomic_index: higher SES → better access.
# Affects LMS logins (added below).
internet_score = socioeconomic_index + _noise(0.8, n)
internet_access_quality = pd.cut(
    internet_score,
    bins=[-np.inf, 2.0, 3.2, 4.4, np.inf],
    labels=["Poor", "Fair", "Good", "Excellent"],
).astype(str)

# ── NEW: Nominal 4-level — preferred_study_time ───────────────────────────────
# Mostly random — another example of a nominal feature with weak predictive power.
preferred_study_time = np.random.choice(
    ["Morning", "Afternoon", "Evening", "Night"],
    n, p=[0.25, 0.35, 0.30, 0.10],
)

# ── Engagement & performance (continuous) ─────────────────────────────────────
# On-campus students get a small attendance boost
accom_boost = np.where(accommodation_type == "On-campus", 4.0, 0.0)
lecture_attendance_rate = _clip(55 + 10 * ability + accom_boost * 0.5 + _noise(20, n), 0, 100)
tutorial_attendance_rate = _clip(60 + 15 * ability + accom_boost + _noise(15, n), 0, 100)
tutorial_participation_score = _clip(3 + 0.5 * ability + _noise(0.8, n), 1, 5)
office_hours_visits = _clip(
    np.round(2 + 1.5 * ability + _noise(1.5, n)), 0, 10
).astype(int)

# Poor internet → fewer LMS logins
internet_penalty = np.select(
    [internet_access_quality == "Poor", internet_access_quality == "Fair"],
    [-3.0, -1.5],
    default=0.0,
)
lms_logins_per_week = _clip(8 + 3 * ability + internet_penalty + _noise(4, n), 0, 20)

assignment_completion_rate = _clip(70 + 12 * ability + _noise(15, n), 0, 100)
avg_assignment_score = _clip(65 + 12 * ability + _noise(10, n), 0, 100)
midterm_score = _clip(60 + 15 * ability + _noise(12, n), 0, 100)
final_exam_score = _clip(60 + 18 * ability + _noise(10, n), 0, 100)
avg_score = 0.2 * midterm_score + 0.5 * final_exam_score + 0.3 * avg_assignment_score

self_reported_stress_level = _clip(
    np.round(3 - 0.3 * ability + _noise(1, n)), 1, 5
).astype(int)
avg_weekly_study_hours = _clip(15 + 5 * ability + _noise(7, n), 0, 40)

# ── Large-scale raw-count columns (normalisation demonstration) ────────────────
# Deliberately paired with existing features to expose the scale-domination
# problem in distance-based algorithms (K-Means, HCA).
#
#   total_study_minutes_per_week  ↔  avg_weekly_study_hours  (~60× scale difference)
#   cumulative_lms_sessions_per_semester  ↔  lms_logins_per_week  (~13× difference)
#
# Without StandardScaler, total_study_minutes_per_week (0–2400) contributes
# ~60× more to Euclidean distance than avg_weekly_study_hours (0–40), even
# though they encode identical behaviour.
total_study_minutes_per_week = _clip(
    avg_weekly_study_hours * 60 + _noise(30, n), 0, 2400
)
cumulative_lms_sessions_per_semester = _clip(
    np.round(lms_logins_per_week * 13 + _noise(15, n)), 0, 300
).astype(int)
extracurricular_hours_per_week = _clip(
    5 + 0.5 * _noise(3, n) + np.random.uniform(0, 5, n), 0, 15
)
part_time_work_hours = _clip(8 - 3 * ability + _noise(5, n), 0, 20)


def _band(score):
    if score < 40:
        return "At-Risk"
    elif score < 60:
        return "Pass"
    elif score < 75:
        return "Merit"
    else:
        return "Distinction"


performance_band = pd.Series(avg_score).apply(_band)

df = pd.DataFrame(
    {
        # ── Identifiers ──────────────────────────────────────────────────────
        "student_id": student_id,
        # ── Demographics (mixed: int + categorical) ──────────────────────────
        "age": age,
        "gender": gender,                           # categorical, 3 levels
        "year_of_study": year_of_study,
        "faculty": faculty,                         # categorical, 5 levels
        "socioeconomic_index": socioeconomic_index,
        "parental_education_level": parental_education_level,
        # ── New categorical features ─────────────────────────────────────────
        "scholarship_holder": scholarship_holder,          # binary Yes/No — correlated with ability
        "accommodation_type": accommodation_type,          # 3-level nominal — mild attendance effect
        "learning_style": learning_style,                  # 4-level nominal — weak predictor
        "internet_access_quality": internet_access_quality,# 4-level ordinal — affects LMS logins
        "preferred_study_time": preferred_study_time,      # 4-level nominal — mostly random
        # ── Engagement (continuous) ──────────────────────────────────────────
        "lecture_attendance_rate": np.round(lecture_attendance_rate, 1),
        "tutorial_attendance_rate": np.round(tutorial_attendance_rate, 1),
        "tutorial_participation_score": np.round(tutorial_participation_score, 2),
        "office_hours_visits": office_hours_visits,
        "lms_logins_per_week": np.round(lms_logins_per_week, 1),
        # ── Large-scale raw-count columns (normalisation demonstration) ───────
        "total_study_minutes_per_week": np.round(total_study_minutes_per_week, 0),
        "cumulative_lms_sessions_per_semester": cumulative_lms_sessions_per_semester,
        # ─────────────────────────────────────────────────────────────────────
        "assignment_completion_rate": np.round(assignment_completion_rate, 1),
        # ── Assessment (continuous) ──────────────────────────────────────────
        "avg_assignment_score": np.round(avg_assignment_score, 1),
        "midterm_score": np.round(midterm_score, 1),
        "final_exam_score": np.round(final_exam_score, 1),
        "avg_score": np.round(avg_score, 1),
        # ── Lifestyle (continuous + ordinal int) ─────────────────────────────
        "self_reported_stress_level": self_reported_stress_level,
        "avg_weekly_study_hours": np.round(avg_weekly_study_hours, 1),
        "extracurricular_hours_per_week": np.round(extracurricular_hours_per_week, 1),
        "part_time_work_hours": np.round(part_time_work_hours, 1),
        # ── Target label ─────────────────────────────────────────────────────
        "performance_band": performance_band,
    }
)

out_dir = os.path.join(os.path.dirname(__file__), "..", "sample_data")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "student_learning_profiles.csv")
df.to_csv(out_path, index=False)

cat_cols = df.select_dtypes(include="object").columns.tolist()
num_cols = df.select_dtypes(include="number").columns.tolist()
print(f"Saved {len(df)} rows to {out_path}")
print(f"  Numeric columns  ({len(num_cols)}): {num_cols}")
print(f"  Categorical cols ({len(cat_cols)}): {cat_cols}")
print()
print(df["performance_band"].value_counts())
print()
print("scholarship_holder distribution:")
print(df["scholarship_holder"].value_counts())
print()
print("internet_access_quality distribution:")
print(df["internet_access_quality"].value_counts())
