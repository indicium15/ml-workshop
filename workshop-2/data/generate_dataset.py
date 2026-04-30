"""
Synthetic student learning profile generator.
Produces 500 rows with realistic inter-feature correlations driven by a
latent academic-ability variable. Output saved to ../sample_data/.
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


ability = np.random.normal(0, 1, n)

student_id = np.arange(1000, 1000 + n)
age = np.random.randint(18, 26, n)
gender = np.random.choice(["Male", "Female", "Other"], n, p=[0.48, 0.48, 0.04])
year_of_study = np.random.randint(1, 5, n)
faculty = np.random.choice(
    ["Engineering", "Business", "Arts", "Science", "Education"], n
)
socioeconomic_index = np.random.randint(1, 6, n)
parental_education_level = np.random.randint(1, 6, n)

lecture_attendance_rate = _clip(55 + 10 * ability + _noise(20, n), 0, 100)
tutorial_attendance_rate = _clip(60 + 15 * ability + _noise(15, n), 0, 100)
tutorial_participation_score = _clip(3 + 0.5 * ability + _noise(0.8, n), 1, 5)
office_hours_visits = _clip(
    np.round(2 + 1.5 * ability + _noise(1.5, n)), 0, 10
).astype(int)
lms_logins_per_week = _clip(8 + 3 * ability + _noise(4, n), 0, 20)
assignment_completion_rate = _clip(70 + 12 * ability + _noise(15, n), 0, 100)
avg_assignment_score = _clip(65 + 12 * ability + _noise(10, n), 0, 100)
midterm_score = _clip(60 + 15 * ability + _noise(12, n), 0, 100)
final_exam_score = _clip(60 + 18 * ability + _noise(10, n), 0, 100)
avg_score = 0.2 * midterm_score + 0.5 * final_exam_score + 0.3 * avg_assignment_score

self_reported_stress_level = _clip(
    np.round(3 - 0.3 * ability + _noise(1, n)), 1, 5
).astype(int)
avg_weekly_study_hours = _clip(15 + 5 * ability + _noise(7, n), 0, 40)
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
        "student_id": student_id,
        "age": age,
        "gender": gender,
        "year_of_study": year_of_study,
        "faculty": faculty,
        "socioeconomic_index": socioeconomic_index,
        "parental_education_level": parental_education_level,
        "lecture_attendance_rate": np.round(lecture_attendance_rate, 1),
        "tutorial_attendance_rate": np.round(tutorial_attendance_rate, 1),
        "tutorial_participation_score": np.round(tutorial_participation_score, 2),
        "office_hours_visits": office_hours_visits,
        "lms_logins_per_week": np.round(lms_logins_per_week, 1),
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
print(f"Saved {len(df)} rows to {out_path}")
print(df["performance_band"].value_counts())
