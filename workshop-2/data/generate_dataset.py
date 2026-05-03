"""
Synthetic student learning profile generator.

The sample data is built for three workshop tasks:
- HCA should reveal a visible hierarchy of student learning profiles.
- K-Means should have a teachable elbow/silhouette around 4 clusters.
- Random Forest should predict performance bands from explainable engagement
  and lifestyle variables, even after obvious score columns are reviewed.

The CSV keeps a realistic mix of numeric, binary, and multi-level categorical
columns so the notebooks can demonstrate encoding, scaling, clustering, leakage
checks, feature importance, and classification.
"""
import os

import numpy as np
import pandas as pd


RNG = np.random.default_rng(42)
N = 500


def _clip(arr, lo, hi):
    return np.clip(arr, lo, hi)


def _normal(mean, sd, size=N):
    return RNG.normal(mean, sd, size)


def _draw_categorical(categories, prob_matrix):
    """Draw one category per row from row-wise probability vectors."""
    prob_matrix = prob_matrix / prob_matrix.sum(axis=1, keepdims=True)
    idx = [RNG.choice(len(categories), p=row) for row in prob_matrix]
    return np.array(categories)[idx]


def _band(score):
    if score < 45:
        return "At-Risk"
    if score < 62:
        return "Pass"
    if score < 78:
        return "Merit"
    return "Distinction"


# Hidden teaching archetypes. They are not exported to the CSV, but they create
# the explainable structure students should discover through clustering.
profile_names = np.array(
    [
        "At-Risk",
        "Practical Pass",
        "Engaged Merit",
        "High Distinction",
    ]
)
profile_prob = np.array([0.18, 0.32, 0.30, 0.20])
profile_idx = RNG.choice(len(profile_names), size=N, p=profile_prob)

# One latent continuum preserves within-profile variation, while the profile
# centers make the cluster story legible.
readiness_center = np.array([-1.45, -0.45, 0.55, 1.45])
readiness = readiness_center[profile_idx] + _normal(0, 0.28)
support_seeking = np.array([0.15, -0.25, 0.75, 0.45])[profile_idx] + _normal(0, 0.35)
time_pressure = np.array([1.15, 0.45, -0.25, -0.65])[profile_idx] + _normal(0, 0.35)


# Demographics
student_id = np.arange(1000, 1000 + N)
age = RNG.integers(18, 26, N)
gender = RNG.choice(["Male", "Female", "Other"], N, p=[0.48, 0.48, 0.04])
year_of_study = _clip(
    np.round(2.4 + 0.25 * readiness + _normal(0, 1.0)), 1, 4
).astype(int)
faculty = RNG.choice(
    ["Engineering", "Business", "Arts", "Science", "Education"],
    N,
    p=[0.24, 0.22, 0.17, 0.22, 0.15],
)
socioeconomic_index = _clip(
    np.round(3 + 0.35 * readiness - 0.25 * time_pressure + _normal(0, 0.95)), 1, 5
).astype(int)
parental_education_level = _clip(
    np.round(3 + 0.25 * socioeconomic_index + _normal(-0.65, 1.0)), 1, 5
).astype(int)


# Categorical context
p_scholarship = 1 / (1 + np.exp(-(0.2 + 1.35 * readiness)))
scholarship_holder = np.where(RNG.random(N) < p_scholarship, "Yes", "No")

accom_probs = np.column_stack(
    [
        _clip(0.28 + 0.10 * readiness, 0.05, 0.65),
        _clip(0.43 - 0.02 * readiness, 0.20, 0.65),
        _clip(0.29 - 0.08 * readiness + 0.04 * time_pressure, 0.06, 0.50),
    ]
)
accommodation_type = _draw_categorical(
    ["On-campus", "Off-campus", "Family home"], accom_probs
)

learning_style = RNG.choice(
    ["Visual", "Auditory", "Reading-Writing", "Kinesthetic"],
    N,
    p=[0.40, 0.20, 0.30, 0.10],
)

internet_score = socioeconomic_index + 0.45 * readiness - 0.20 * time_pressure + _normal(0, 0.75)
internet_access_quality = pd.cut(
    internet_score,
    bins=[-np.inf, 2.1, 3.25, 4.45, np.inf],
    labels=["Poor", "Fair", "Good", "Excellent"],
).astype(str)

preferred_study_time = RNG.choice(
    ["Morning", "Afternoon", "Evening", "Night"],
    N,
    p=[0.25, 0.35, 0.30, 0.10],
)


# Engagement and behaviour. Tutorial variables intentionally carry a stronger
# performance signal than lecture attendance, matching the notebook reflection.
on_campus = accommodation_type == "On-campus"
poor_internet = internet_access_quality == "Poor"
fair_internet = internet_access_quality == "Fair"

lecture_attendance_rate = _clip(67 + 11 * readiness - 3 * time_pressure + 3 * on_campus + _normal(0, 6.0), 0, 100)
tutorial_attendance_rate = _clip(69 + 14 * readiness + 2 * support_seeking - 3 * time_pressure + 4 * on_campus + _normal(0, 5.0), 0, 100)
tutorial_participation_score = _clip(3.05 + 0.55 * readiness + 0.35 * support_seeking + _normal(0, 0.32), 1, 5)
office_hours_visits = _clip(
    np.round(2.4 + 0.75 * readiness + 1.25 * support_seeking + _normal(0, 0.9)), 0, 10
).astype(int)

internet_penalty = np.select([poor_internet, fair_internet], [-2.6, -1.1], default=0.0)
lms_logins_per_week = _clip(8.7 + 3.0 * readiness + 0.7 * support_seeking + internet_penalty + _normal(0, 1.4), 0, 20)

assignment_completion_rate = _clip(72 + 13 * readiness + 4 * support_seeking - 3 * time_pressure + _normal(0, 5.5), 0, 100)
avg_weekly_study_hours = _clip(14.5 + 5.4 * readiness - 1.2 * time_pressure + 0.8 * support_seeking + _normal(0, 2.6), 0, 40)
self_reported_stress_level = _clip(
    np.round(3.0 + 0.75 * time_pressure - 0.25 * readiness + _normal(0, 0.45)), 1, 5
).astype(int)
part_time_work_hours = _clip(8.2 + 3.6 * time_pressure - 1.4 * readiness + _normal(0, 2.4), 0, 20)
extracurricular_hours_per_week = _clip(5.5 + 0.8 * readiness - 0.35 * time_pressure + RNG.uniform(0, 3, N) + _normal(0, 1.0), 0, 15)


# Raw-count columns deliberately duplicate behaviour on larger scales so the
# scaling demonstrations have a clear before/after effect.
total_study_minutes_per_week = _clip(avg_weekly_study_hours * 60 + _normal(0, 28), 0, 2400)
cumulative_lms_sessions_per_semester = _clip(
    np.round(lms_logins_per_week * 13 + _normal(0, 12)), 0, 300
).astype(int)


# Assessment scores are downstream of engagement. They make an intentionally
# easy baseline, while the leakage-check step can remove them and still leave a
# meaningful predictive pattern in attendance, LMS, study hours, work, and stress.
academic_signal = (
    0.22 * lecture_attendance_rate
    + 0.30 * tutorial_attendance_rate
    + 5.0 * tutorial_participation_score
    + 0.10 * assignment_completion_rate
    + 0.42 * avg_weekly_study_hours
    + 0.35 * lms_logins_per_week
    - 1.25 * part_time_work_hours
    - 2.2 * self_reported_stress_level
)
academic_signal = 10 + academic_signal + _normal(0, 3.0)

avg_assignment_score = _clip(academic_signal + 4.5 + _normal(0, 4.0), 0, 100)
midterm_score = _clip(academic_signal + _normal(0, 4.5), 0, 100)
final_exam_score = _clip(academic_signal + 2.5 + 2.4 * readiness + _normal(0, 4.0), 0, 100)
avg_score = 0.30 * avg_assignment_score + 0.20 * midterm_score + 0.50 * final_exam_score
performance_band = pd.Series(avg_score).apply(_band)


df = pd.DataFrame(
    {
        "student_id": student_id,
        "age": age,
        "gender": gender,
        "year_of_study": year_of_study,
        "faculty": faculty,
        "socioeconomic_index": socioeconomic_index,
        "parental_education_level": parental_education_level,
        "scholarship_holder": scholarship_holder,
        "accommodation_type": accommodation_type,
        "learning_style": learning_style,
        "internet_access_quality": internet_access_quality,
        "preferred_study_time": preferred_study_time,
        "lecture_attendance_rate": np.round(lecture_attendance_rate, 1),
        "tutorial_attendance_rate": np.round(tutorial_attendance_rate, 1),
        "tutorial_participation_score": np.round(tutorial_participation_score, 2),
        "office_hours_visits": office_hours_visits,
        "lms_logins_per_week": np.round(lms_logins_per_week, 1),
        "total_study_minutes_per_week": np.round(total_study_minutes_per_week, 0),
        "cumulative_lms_sessions_per_semester": cumulative_lms_sessions_per_semester,
        "assignment_completion_rate": np.round(assignment_completion_rate, 1),
        "avg_assignment_score": np.round(avg_assignment_score, 1),
        "midterm_score": np.round(midterm_score, 1),
        "final_exam_score": np.round(final_exam_score, 1),
        "avg_score": np.round(avg_score, 1),
        "self_reported_stress_level": self_reported_stress_level,
        "avg_weekly_study_hours": np.round(avg_weekly_study_hours, 1),
        "extracurricular_hours_per_week": np.round(extracurricular_hours_per_week, 1),
        "part_time_work_hours": np.round(part_time_work_hours, 1),
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
