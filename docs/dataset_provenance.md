# Dataset Provenance: UCI Student Performance

## 1. Dataset Identification

- **Dataset title:** Student Performance
- **Publisher:** UCI Machine Learning Repository
- **Dataset author:** Paulo Cortez
- **Original paper authors:** Paulo Cortez and Alice Maria Gonçalves Silva, University of Minho, Portugal
- **UCI dataset citation:** Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning Repository. [https://doi.org/10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T).
- **Original paper:** Cortez, P., & Silva, A. (2008). *Using data mining to predict secondary school student performance*. Proceedings of the 5th Annual Future Business Technology Conference (FUBUTEC 2008), pages 5–12.
- **Official dataset page:** [UCI Student Performance](https://archive.ics.uci.edu/dataset/320/student+performance)
- **Official direct archive download:** [student+performance.zip](https://archive.ics.uci.edu/static/public/320/student%2Bperformance.zip)
- **DOI:** [10.24432/C5TG7T](https://doi.org/10.24432/C5TG7T)
- **Access / verification date:** 2026-10-25

## 2. License, Attribution, and Changes

- **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), as stated in the UCI dataset metadata.
- **Attribution:** Attribute the dataset to Paulo Cortez and UCI Machine Learning Repository, link to the license, and indicate changes when sharing adapted material. Cite the Cortez and Silva paper when discussing the research publication.
- **Dataset citation:** Cortez, P. (2008). *Student Performance* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T.
- **Changes made in this project:**
  1. The raw source CSV files are retained in `data/raw/` unmodified with no changes to original values.
  2. Sequential per-file surrogate keys (e.g., `MAT_0001`, `POR_0001`) are assigned dynamically for internal audit traceability.
  3. A derived boolean pass/fail flag is computed based on the illustrative benchmark (G3 >= 8/20).
  4. Aggregate descriptive tables and visual summaries are generated in reports; no individual student-level data is published.

## 3. Dataset Files, Integrity, and Schema

The UCI archive contains two distinct course files, each with 33 columns and formatted with semicolon (`;`) delimiters.

### 3.1 Course Files, Checksums, and Record Counts

1. **`student-mat.csv` (Mathematics Course):**
   - **Retrieval date:** 2026-10-25
   - **File size:** 56,993 bytes
   - **SHA-256:** `e47f9ee225e1ee6e69b7564e6dac7123e80b8486677fe111f351964cef5dec80`
   - **Record count:** 395 student instances (plus 1 header row = 396 lines)
   - **Attributes:** 33 columns

2. **`student-por.csv` (Portuguese Language Course):**
   - **Retrieval date:** 2026-10-25
   - **File size:** 93,220 bytes
   - **SHA-256:** `a7594a11d7771c0efe1a740824e0e833da9c4cad07c39a9766a874575563fb3f`
   - **Record count:** 649 student instances (plus 1 header row = 650 lines)
   - **Attributes:** 33 columns

**Cohort Separation and Overlap Note:**
The UCI documentation states that 382 students appear in both files, identified by demographic attributes. However, neither file has an official student ID, and demographic matching is not guaranteed to identify individuals uniquely. **This project strictly treats the two files as separate, independent cohorts and never merges or matches individual records across files.**

### 3.2 Data Dictionary (33 Features)

| Attribute | Type | Values or range | Description |
| --- | --- | --- | --- |
| `school` | Binary | `GP`, `MS` | Student school: Gabriel Pereira or Mousinho da Silveira |
| `sex` | Binary | `F`, `M` | Student sex |
| `age` | Integer | 15–22 | Student age |
| `address` | Binary | `U`, `R` | Urban or rural home address |
| `famsize` | Binary | `LE3`, `GT3` | Family size: 3 or fewer, or more than 3 |
| `Pstatus` | Binary | `T`, `A` | Parents living together or apart |
| `Medu` | Integer | 0–4 | Mother education: none, 4th grade, 5th-9th, secondary, higher |
| `Fedu` | Integer | 0–4 | Father education: none, 4th grade, 5th-9th, secondary, higher |
| `Mjob` | Nominal | `teacher`, `health`, `services`, `at_home`, `other` | Mother job category |
| `Fjob` | Nominal | `teacher`, `health`, `services`, `at_home`, `other` | Father job category |
| `reason` | Nominal | `home`, `reputation`, `course`, `other` | Reason for choosing school |
| `guardian` | Nominal | `mother`, `father`, `other` | Student primary guardian |
| `traveltime` | Ordinal | 1–4 | Travel time: <15m, 15-30m, 30-60m, >60m |
| `studytime` | Ordinal | 1–4 | Weekly study time category: <2h, 2-5h, 5-10h, >10h (**ordinal categories, not continuous hours**) |
| `failures` | Integer category | 0–4 | Past class failures (4 = 3 or more) |
| `schoolsup` | Binary | `yes`, `no` | Extra educational support |
| `famsup` | Binary | `yes`, `no` | Family educational support |
| `paid` | Binary | `yes`, `no` | Extra paid classes in course subject |
| `activities` | Binary | `yes`, `no` | Extra-curricular activities |
| `nursery` | Binary | `yes`, `no` | Attended nursery school |
| `higher` | Binary | `yes`, `no` | Aspirations to take higher education |
| `internet` | Binary | `yes`, `no` | Internet access at home |
| `romantic` | Binary | `yes`, `no` | In a romantic relationship |
| `famrel` | Integer | 1–5 | Family relationship quality (1=very bad to 5=excellent) |
| `freetime` | Integer | 1–5 | Free time after school (1=very low to 5=very high) |
| `goout` | Integer | 1–5 | Going out with friends (1=very low to 5=very high) |
| `Dalc` | Integer | 1–5 | Workday alcohol consumption (1=very low to 5=very high) |
| `Walc` | Integer | 1–5 | Weekend alcohol consumption (1=very low to 5=very high) |
| `health` | Integer | 1–5 | Current health status (1=very bad to 5=very good) |
| `absences` | Integer | 0–93 | Number of school absences |
| `G1` | Integer | 0–20 | First period grade |
| `G2` | Integer | 0–20 | Second period grade |
| `G3` | Integer | 0–20 | Final period grade (**primary evaluation outcome**) |

## 4. Analytical and Data-Quality Rules

### 4.1 Grade Scale
Grades are recorded on a 0–20 integer scale (Portuguese secondary education). Scores outside this range represent invalid entries and are quarantined as ungradable.

### 4.2 Primary Outcome and Illustrative Pass Threshold
- **Primary outcome:** `G3` is the sole score evaluated for pass/fail determination.
- **Pass rule:** A record passes when G3 >= 8 out of 20 (illustrative 40% benchmark).
- **Threshold rationale:** 8 out of 20 represents an illustrative project threshold for demonstration purposes. **It does not represent an official school policy.**
- **Other grades:** `G1` and `G2` are tracked for period trend comparisons but are never averaged with `G3` for the pass decision.

### 4.3 Study Time Treatment
`studytime` is strictly an ordinal categorical factor (1 to 4). It is never treated as continuous measured hours.

### 4.4 Duplicate Detection
Exact duplicate rows across all 33 features are audited and reported. Rows are never silently deleted or deduplicated using demographic fields.

### 4.5 Surrogate Keys
Because neither file contains official student IDs, the pipeline assigns surrogate keys (e.g. `MAT_0001`, `POR_0001`) strictly for row-level tracing and audit reporting.

## 5. Resolved Analysis Approach

Analyze `student-mat.csv` and `student-por.csv` as independent, parallel cohorts. Load, validate, audit, and summarize each file separately. Cross-course comparisons are strictly aggregate; individual student records are never linked across files.
