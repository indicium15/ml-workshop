---
marp: true
theme: default
paginate: true
style: |
  /* ── Base ── */
  :root {
    --navy-950: #111c2f;
    --navy-900: #172640;
    --navy-800: #203653;
    --slate-700: #415064;
    --slate-200: #d7dee8;
    --slate-100: #eef3f8;
    --paper: #f8fbff;
    --cyan: #7fd7ff;
    --cyan-strong: #2b9dcc;
    --amber: #c97a1a;
  }
  section {
    font-family: 'Segoe UI', Arial, sans-serif;
    background:
      linear-gradient(180deg, rgba(248,251,255,0.98), rgba(244,248,253,0.98));
    color: var(--navy-950);
    padding: 44px 56px;
    font-size: 27px;
    line-height: 1.34;
  }
  h1 {
    color: var(--navy-900);
    border-bottom: 3px solid var(--cyan-strong);
    padding-bottom: 8px;
    margin: 0 0 22px;
  }
  h2 { color: var(--navy-900); margin: 0 0 18px; }
  h3 { color: var(--navy-800); margin: 0 0 10px; }
  p, ul, ol { margin-top: 0; }
  li { margin: 0.26em 0; }
  strong { color: var(--navy-800); font-weight: 700; }
  code {
    background: #e7eef7;
    color: var(--navy-900);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.86em;
  }
  a { color: var(--cyan-strong); }
  section table {
    display: table !important;
    font-size: 0.72em;
    line-height: 1.22;
    border-collapse: collapse;
    width: auto !important;
    max-width: 100%;
    margin: 8px auto 14px !important;
    background: rgba(255,255,255,0.72);
    border: 1px solid var(--slate-200);
  }
  th {
    background: var(--navy-800);
    color: white;
    padding: 7px 10px;
    text-align: left;
    font-weight: 650;
  }
  td { padding: 6px 10px; border-bottom: 1px solid var(--slate-200); }
  tr:nth-child(even) td { background: #f2f6fb; }
  blockquote {
    border-left: 5px solid var(--cyan-strong);
    background: #eaf6fc;
    color: var(--slate-700);
    padding: 9px 15px;
    margin: 14px 0 0;
    border-radius: 0 4px 4px 0;
    font-size: 0.82em;
    line-height: 1.32;
  }
  pre { font-size: 0.7em; line-height: 1.24; }
  /* ── Title slide ── */
  section.title {
    background:
      radial-gradient(circle at 72% 36%, rgba(127,215,255,0.26), transparent 26%),
      linear-gradient(135deg, var(--navy-950) 0%, var(--navy-800) 62%, #2e5f84 100%);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
  }
  section.title h1 {
    color: white;
    border-bottom: 3px solid rgba(127,215,255,0.72);
    font-size: 2em;
    max-width: 980px;
  }
  section.title h2 { color: rgba(255,255,255,0.9); font-weight: 300; }
  section.title h3 { color: rgba(255,255,255,0.78); }
  section.title p  { color: rgba(255,255,255,0.8); font-size: 0.9em; }
  section.title strong { color: #ffffff; }
  section.title code { background: rgba(255,255,255,0.9); color: var(--navy-950); }
  /* ── Section divider ── */
  section.section {
    background:
      radial-gradient(circle at 82% 20%, rgba(127,215,255,0.24), transparent 24%),
      linear-gradient(135deg, var(--navy-950), var(--navy-800));
    color: white; display: flex; flex-direction: column;
    justify-content: center; align-items: flex-start;
  }
  section.section h1 {
    color: white;
    border-bottom: 2px solid rgba(127,215,255,0.58);
    font-size: 2.2em;
  }
  section.section h2,
  section.section h3,
  section.section strong { color: rgba(255,255,255,0.9); }
  section.section p  { color: rgba(255,255,255,0.85); font-size: 1.1em; }
  /* ── Highlight box ── */
  .box {
    background: #eaf6fc;
    border: 1px solid #aed7e8;
    border-left: 6px solid var(--cyan-strong);
    border-radius: 4px;
    padding: 12px 18px;
    margin: 12px 0;
  }
  .warn {
    background: #fff7e8;
    border: 1px solid #e3b36f;
    border-left: 6px solid var(--amber);
    border-radius: 4px;
    padding: 12px 18px;
    margin: 12px 0;
  }
  .muted { color: var(--slate-700); }
  .small { font-size: 0.78em; }
  /* ── Two-column layout ── */
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  .cols3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .concept-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
  .concept-card {
    background: rgba(255,255,255,0.74);
    border: 1px solid var(--slate-200);
    border-top: 5px solid var(--cyan-strong);
    border-radius: 5px;
    padding: 18px 20px;
  }
  .concept-card.alt { border-top-color: var(--amber); background: #fffaf0; }
  .concept-card h3 { color: var(--navy-900); }
  .pipeline { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 18px 0; }
  .step {
    background: rgba(255,255,255,0.74);
    border: 1px solid var(--slate-200);
    border-top: 4px solid var(--cyan-strong);
    border-radius: 5px;
    padding: 12px 14px;
    min-height: 110px;
  }
  .step strong { display: block; color: var(--navy-900); margin-bottom: 6px; }
  .flow-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
  .flow-card {
    background: rgba(255,255,255,0.74);
    border: 1px solid var(--slate-200);
    border-radius: 5px;
    padding: 16px 18px;
  }
  .flow-card h3 { color: var(--navy-900); }
  section.dataset {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 52px 68px;
    font-size: 29px;
  }
  section.dataset h2 {
    width: 100%;
    max-width: 1120px;
    margin-bottom: 26px;
  }
  .data-table {
    width: 100%;
    max-width: 1120px;
    margin: 0 auto;
  }
  .data-table table {
    table-layout: fixed;
    width: 100%;
    font-size: 0.78em;
    line-height: 1.28;
    box-shadow: 0 10px 24px rgba(17,28,47,0.08);
  }
  section.byo-dataset {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 38px 68px;
    font-size: 24px;
  }
  section.byo-dataset h2,
  section.byo-dataset p,
  section.byo-dataset .data-table {
    width: 100%;
    max-width: 1120px;
    margin-left: auto;
    margin-right: auto;
  }
  section.byo-dataset h2 { margin-bottom: 14px; }
  section.byo-dataset p { margin-bottom: 14px; }
  section.byo-dataset .data-table table { font-size: 0.7em; }
  /* ── Image sizing helpers ── */
  .img-center { text-align: center; }
  .img-center img { max-width: 100%; max-height: 360px; border-radius: 5px; box-shadow: 0 8px 22px rgba(17,28,47,0.12); }
  .img-full { text-align: center; }
  .img-full img { max-width: 100%; max-height: 410px; width: auto; border-radius: 5px; box-shadow: 0 8px 22px rgba(17,28,47,0.12); }
  .img-half img { max-width: 100%; max-height: 280px; border-radius: 5px; box-shadow: 0 8px 22px rgba(17,28,47,0.12); }
  .output-pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 26px;
    margin: 8px 0 22px;
  }
  .output-figure {
    height: 340px;
    background: white;
    border-radius: 6px;
    box-shadow: 0 8px 22px rgba(17,28,47,0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
  .output-figure p {
    width: 100%;
    height: 100%;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .output-figure img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    box-shadow: none;
    border-radius: 0;
  }
  .output-intuition {
    font-size: 0.9em;
    line-height: 1.24;
  }
---

<!-- _class: title -->

# Hands-On Machine Learning Workshop: From Data to Insights

## OfR Professional Development Series

<br>
<br>
<br>

**Wednesday, 06 May 2026**<br>
**1.00 pm - 3.30 pm**<br>
**Link to the Slides: https://tinyurl.com/ml-workshop-slides**

---

## Agenda

Today's workshop has two main themes, **concepts** and **implementations**. We will:
1. Understand the core concepts and techniques behind supervised and unsupervised learning.
2. Learn how to use Jupyter Notebooks and Python to implement these concepts.
3. Understand how to interpret results
4. Gain an intuition and the materials for how to analyze your own datasets. 

**Pre-requisites: Google Account for Google Colab / Local Python Environment**

---

## Bring Your Own Dataset

The materials from this workshop are designed to be re-used for your own datasets. If you have your own data you would like to explore, feel free to try using it here.

We have also generated a synthetic dataset of student performance data for today's exercises. It contains 500 rows and 29 columns covering:

| Column Group | Column Names |
|---|---|
| Demographics and context | `year_of_study`, `faculty`, `scholarship_holder`, `internet_access_quality` |
| Engagement | `lecture_attendance_rate`, `tutorial_attendance_rate`, `lms_logins_per_week` |
| Study and workload | `avg_weekly_study_hours`, `part_time_work_hours`, `self_reported_stress_level` |
| Assessment scores | `avg_assignment_score`, `midterm_score`, `final_exam_score`, `avg_score` |
| Target/outcome | `performance_band` |

The default clustering notebooks use behaviour and workload columns. The Random Forest notebook also includes selected context columns and leaves score columns for leakage review.

---

## Exercise 1: Exploratory Data Analysis

Before making any decisions on how to proceed with a dataset, we must first get an overall understanding of it.

We can use the following Python libraries for this:
1. [Pandas](https://pandas.pydata.org/docs/user_guide/index.html) for data loading and manipulation
2. [Matplotlib](https://matplotlib.org/stable/users/index.html) for data visualization

Notebook Link: https://tinyurl.com/ml-workshop-notebook-0

---

## Dataset Pre-Processing

| Column type | Example | Typical question | Possible action |
|---|---|---|---|
| Numeric | `avg_weekly_study_hours` | Are the scales comparable? | Scale or normalise |
| Categorical | `faculty` | Can the model read labels? | Encode or exclude |
| Identifier | `student_id` | Does it describe behaviour? | Usually remove |
| Missing values | blank attendance values | Are blanks meaningful or accidental? | Fill, remove, or revisit |
| Target/outcome | `performance_band` | Is this what we are predicting? | Exclude from training data |

---

## Categorical Encoding

Models need numbers, so categorical columns can be label encoded, one-hot encoded, or dropped.

- **Label encoding:** replace each category with a number, such as `Low = 0`, `Medium = 1`, `High = 2`.
- **One-hot encoding:** create one 0/1 column per category, such as `faculty_Engineering` or `faculty_Business`.
- **Dropping:** remove a categorical column when it is not useful, has too many messy categories, or would add noise.

---

## Scaling

HCA and K-Means compare rows by measuring distance between feature values.

Scaling puts features onto a comparable range so the model pays attention to patterns across all selected columns.

<div class="img-full">

![Scaling before and after preprocessing](images/14_preprocessing_scaling_before_after.png)

</div>

---

## Two Paradigms of Machine Learning

<div class="cols">
<div>

### Unsupervised Learning

I only see inputs, so I have to figure out the structure myself.

> "Do these features naturally group together?"

</div>
<div>

### Supervised learning

I see both inputs and outputs, so I learn to map one to the other.

> "Can we predict this label?"

</div>
</div>

---

<!-- _class: section -->

# Unsupervised Learning
## HCA and K-Means Clustering

---

## HCA: Introduction

Hierarchical Clustering Analysis is a bottom-up algorithm that starts by treating every row as its own cluster. It repeatedly joins the closest rows or groups until everything is connected.

**Use HCA when:**
- the dataset is not too large
- you do not know how many groups to expect

**Account for:**
- features having different scales
- branches not being clearly separated

---

## HCA Output: Dendrogram

<div class="img-full">

![Dendrogram](images/04_dendrogram.png)

</div>

Key Intuition: Reading the graph bottom-up

---

## HCA: Jupyter Notebook Walkthrough

**Notebook 1**
- load the dataset
- choose feature columns
- apply preprocessing
- run HCA
- inspect the dendrogram and cluster profiles

Notebook Link: https://tinyurl.com/ml-workshop-notebook-1

---

## K-Means: Introduction

K-Means is a clustering algorithm that assigns every row to one of `k` clusters. It places centroids, assigns rows to the nearest centroid, moves the centroids, and repeats until the assignments settle.

**Use K-Means when:**
- you want a fixed number of groups
- the dataset is larger
- you want to assign every row to one cluster

**Account for:**
- having to choose `k` before running the model
- features having different scales

---

## K-Means Output: Elbow Plot and Cluster Comparison

<div class="output-pair">
<div class="output-figure">

![Elbow curve](images/05_elbow_curve.png)

</div>
<div class="output-figure">

![K-Means vs bands](images/07_kmeans_vs_bands.png)

</div>
</div>

<div class="output-intuition">

Key Intuition:

- The elbow plot helps choose an appropriate number of clusters
- The cluster comparison helps us check whether the groups are interpretable.

</div>

---

## K-Means Model Selection: AIC/BIC Elbow

<div class="output-pair">
<div>

- lower score is better
- fit improves as `k` increases
- extra clusters are penalised
- BIC is more conservative than AIC

Choose a `k` near the elbow where adding more clusters gives diminishing returns.

</div>
<div class="output-figure">

![AIC and BIC model selection](images/15_aic_bic_model_selection.png)

</div>
</div>

---

## K-Means: Jupyter Notebook Walkthrough

**Notebook 2**
- load the dataset
- choose feature columns
- apply required scaling
- inspect the elbow plot
- choose `k`
- compare cluster profiles

Notebook Link: https://tinyurl.com/ml-workshop-notebook-2

---

<!-- _class: section -->

# Supervised Learning
## Random Forest Classification

---

## Random Forest: Introduction

A decision tree segments data based on yes/no questions. A Random Forest builds many trees and lets them vote on the outcome.

**Use Random Forest when:**
- you have a known label to predict
- you want a strong baseline model
- you want to inspect which features the model used

**Account for:**
- overfitting
- class imbalance

---

## Random Forest Output: Confusion Matrix and Feature Importance

<div class="output-pair">
<div class="output-figure">

![Confusion matrix](images/09_confusion_matrix.png)

</div>
<div class="output-figure">

![Feature importance](images/08_feature_importance.png)

</div>
</div>

---

## Random Forest: Jupyter Notebook Walkthrough

**Notebook 3**
- select `performance_band` as the label
- choose feature columns
- train the Random Forest
- inspect the confusion matrix
- compare feature importance
- test what happens when leakage is introduced

Notebook Link: https://tinyurl.com/ml-workshop-notebook-3

---

<!-- _class: section -->

# Part 4
## Extending this to your own data

---

## Using Jupyter Notebooks for Machine Learning

The notebooks are designed to be re-used with your own CSV files.

<div class="cols">
<div>

**Good notebook habits**
- duplicate notebooks before major experiments
- use clear names like `hca_mydata_v1.ipynb`
- code / markdown comments are useful for tracking changes
</div>
<div>

**Useful references**
- [Jupyter documentation](https://docs.jupyter.org/)
- [pandas getting started](https://pandas.pydata.org/docs/getting_started/index.html)
- [scikit-learn preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html)
- [scikit-learn train/test split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [scikit-learn clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [scikit-learn model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)

</div>
</div>

---

## Conclusion

Today we:

- prepared data by encoding categories and scaling numeric features
- explored when to use unsupervised or supervised learning techniques
- used HCA to explore possible groupings
- used K-Means to create and compare clusters
- used Random Forest to predict a known outcome and inspect influential features
- discussed how to adapt the notebooks for your own datasets
