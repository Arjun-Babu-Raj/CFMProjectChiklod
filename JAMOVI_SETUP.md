# 🔬 Loading the LLM Assistant Module in Jamovi

This guide walks you through every step required to install and use the
**Jamovi LLM Assistant** module from this repository.

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Install R and Required Packages](#2-install-r-and-required-packages)
3. [Build the Jamovi Module (.jmo file)](#3-build-the-jamovi-module-jmo-file)
   - [Option A – Using `jmvtools` (Recommended)](#option-a--using-jmvtools-recommended)
   - [Option B – Manual zip method](#option-b--manual-zip-method)
4. [Install the Module in Jamovi](#4-install-the-module-in-jamovi)
5. [First-Time Setup inside Jamovi](#5-first-time-setup-inside-jamovi)
6. [Running Your First Analysis](#6-running-your-first-analysis)
7. [Understanding the Output Sections](#7-understanding-the-output-sections)
8. [Sourcing R Modules Directly (without Jamovi)](#8-sourcing-r-modules-directly-without-jamovi)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Prerequisites

| Requirement | Minimum Version | Download |
|-------------|----------------|---------|
| **Jamovi** | 2.3+ | https://www.jamovi.org/download.html |
| **R** | 4.0+ | https://cran.r-project.org |
| **jmvtools** R package | 0.4.0+ | via CRAN (see Step 2) |
| **jmvcore** R package | 0.8.0+ | via CRAN (see Step 2) |
| Google Gemini API key *(optional)* | — | https://makersuite.google.com/app/apikey |

> **Note:** Jamovi ships with its own bundled R installation. The R packages
> listed above must be installed into **that bundled R**, not a separate
> system R. `jmvtools` handles this automatically.

---

## 2. Install R and Required Packages

### 2a. Install `jmvtools` (the Jamovi developer toolkit)

Open a terminal / R console and run:

```r
install.packages("jmvtools", repos = c(
    "https://repo.jamovi.org",
    "https://cran.r-project.org"
))
```

### 2b. Install the module's R dependencies

```r
install.packages(c("jmvcore", "R6"), repos = "https://cran.r-project.org")
```

> **Optional (needed only for live Gemini API calls):**
> ```r
> install.packages(c("httr2", "jsonlite"), repos = "https://cran.r-project.org")
> ```

---

## 3. Build the Jamovi Module (.jmo file)

A Jamovi module is distributed as a `.jmo` file (which is a renamed `.zip`).
You must build it from this repository first.

### Clone the repository

```bash
git clone https://github.com/Arjun-Babu-Raj/CFMProjectChiklod.git
cd CFMProjectChiklod
```

### Option A – Using `jmvtools` (Recommended)

This is the official method and automatically validates the module:

```r
# In R, from the cloned repository root:
setwd("/path/to/CFMProjectChiklod")  # ← adjust to your path

library(jmvtools)

# Build and create the .jmo file in the current directory
jmvtools::build()
```

If the build succeeds you will see:

```
✓ Build complete: jmoviLLMAssistant_1.0.0.jmo
```

The output file `jmoviLLMAssistant_1.0.0.jmo` is created in the repository
root. Keep note of its location.

### Option B – Manual zip method

Use this only if `jmvtools` is unavailable:

**Windows (PowerShell):**
```powershell
# From inside the repository root
Compress-Archive -Path DESCRIPTION, package.yaml, R, jamovi `
    -DestinationPath jmoviLLMAssistant_1.0.0.zip
Rename-Item jmoviLLMAssistant_1.0.0.zip jmoviLLMAssistant_1.0.0.jmo
```

**macOS / Linux:**
```bash
# From inside the repository root
zip -r jmoviLLMAssistant_1.0.0.jmo DESCRIPTION package.yaml R/ jamovi/
```

---

## 4. Install the Module in Jamovi

1. **Open Jamovi.**

2. Click the **≡ (hamburger) menu** in the top-right corner.

3. Select **Manage modules** → **Install from file…**

   ![Jamovi module menu](https://www.jamovi.org/img/install-module.png)

4. Browse to the `.jmo` file you built in Step 3:
   `jmoviLLMAssistant_1.0.0.jmo`

5. Click **Open / Install**.

6. Jamovi will display a progress bar and then confirm:
   > *"LLM Assistant installed successfully."*

7. **Restart Jamovi** when prompted (or close and reopen).

### Verify installation

After restarting, open the **Analyses** ribbon. You should see a new
**"LLM Tools"** group containing the **"LLM Assistant"** item.

---

## 5. First-Time Setup inside Jamovi

### 5a. Open your data file

- Load a dataset (CSV, SPSS, Excel, etc.) in the usual Jamovi way.
- The module will read directly from the active Jamovi data view.

### 5b. Open the LLM Assistant

1. In the **Analyses** ribbon, click **LLM Tools → LLM Assistant**.
2. The analysis panel opens on the right.

### 5c. (Optional) Enter your Gemini API key

If you want AI-generated narrative interpretations powered by Google Gemini:

1. Scroll to the **"Gemini API Key (session only)"** field.
2. Paste your API key (starts with `AIza…`).

> **Security note:** The key is held in memory for the current session only.
> It is never written to your hard disk, never included in output, and is
> cleared the moment Jamovi closes.

You can obtain a free Gemini API key at:
https://makersuite.google.com/app/apikey

---

## 6. Running Your First Analysis

### Step-by-step example: "Compare test scores between male and female students"

Assume your data has:
- `score` — numeric column with test results
- `sex` — categorical column with values "Male" / "Female"

| Setting | Value |
|---------|-------|
| **Analysis Query** | `Compare test scores between male and female students` |
| **Analysis Type** | `Independent t-test` (or leave as *Auto-detect*) |
| **Outcome Variable** | `score` |
| **Grouping Variable** | `sex` |
| **Significance Level** | `0.05` |

Click **▶ Run** (or the analysis runs automatically as you set options).

---

## 7. Understanding the Output Sections

The module produces four collapsible sections:

### 📊 Input Validation Report
```
=== INPUT VALIDATION REPORT ===
✓ All validation checks passed.
⚠ Outliers detected in: score – consider investigation before analysis.
```
Tells you whether your query, data structure, variable types, sample size,
and missing values are appropriate for the chosen analysis.

### 📈 Descriptive Analysis
```
=== DESCRIPTIVE ANALYSIS ===
score:
  Mean: 75.3 (SD: 8.2)   Median: 76.0 (IQR: 69–82)   n = 152   Missing: 0
```
Summary statistics, frequency tables for categorical variables, and a
missing-data report.

### ✅ Assumption Checking
```
=== ASSUMPTION CHECKING ===
✓ Normality: Both groups normally distributed (Shapiro-Wilk p > 0.05)
✓ Homogeneity: Equal variances confirmed (Levene: p = 0.18)
✓ Independence: Observations independent (DW = 1.98)
✓ Sample Size: Adequate (n1=152, n2=148)

⚠ Assumptions violated: –
```
Each statistical assumption is tested and flagged as met (✓) or violated (✗).
When assumptions are violated, remedial actions are suggested automatically
(e.g. Welch's t-test, Mann-Whitney U).

### 🧪 Statistical Test & Results
```
=== INDEPENDENT t-TEST RESULTS ===
  Test Name               : Independent t-test (Welch)
  Group 1 (Female)        : Mean=75.3 (SD=8.2), n=152
  Group 2 (Male)          : Mean=72.8 (SD=9.1), n=148
  Test Statistic (t)      : 2.150
  Degrees of Freedom      : 295.4
  P-value                 : 0.0323 *
  Effect Size (Cohen's d) : 0.280 (small effect)
  95% Confidence Interval : [0.182, 4.818]
  Interpretation          : Female scored 2.5 points higher …
  Assumptions Met         : All checked
```

---

## 8. Sourcing R Modules Directly (without Jamovi)

You can also use the R modules standalone (e.g. in RStudio or a script):

```r
# Source all modules (adjust paths as needed)
source("R/inputValidation.R")
source("R/assumptionChecker.R")
source("R/analysisWorkflow.R")
source("R/resultsFormatter.R")
source("R/promptEngine.R")

# Example: full three-phase workflow
df <- data.frame(
  score = c(rnorm(30, 75, 8), rnorm(30, 72, 9)),
  sex   = rep(c("Female", "Male"), each = 30)
)

result <- run_analysis_workflow(
  query         = "Compare test scores between male and female students",
  data          = df,
  analysis_type = "t_test",
  outcome_var   = "score",
  group_var     = "sex"
)

cat(format_full_report(result))
```

### Module function reference

| Module | Key Functions |
|--------|--------------|
| `inputValidation.R` | `validate_inputs()`, `validate_query()`, `validate_data_structure()`, `detect_missing_values()`, `detect_outliers()`, `validate_sample_size()` |
| `assumptionChecker.R` | `check_assumptions()`, `test_normality()`, `test_homogeneity()`, `test_independence()`, `assess_linearity()`, `check_multicollinearity()` |
| `analysisWorkflow.R` | `run_analysis_workflow()`, `run_t_test()`, `run_anova()`, `run_correlation()`, `run_regression()`, `run_chi_square()` |
| `resultsFormatter.R` | `format_full_report()`, `format_t_test_results()`, `format_anova_results()`, `format_assumption_table()` |
| `promptEngine.R` | `build_prompt(stage, ...)` — stages: `recommend`, `violation`, `interpret`, `quality` |

### Running the tests

```bash
# From repository root
Rscript -e "source('tests/test-inputValidation.R')"
Rscript -e "source('tests/test-assumptionChecker.R')"
Rscript -e "source('tests/test-analysisWorkflow.R')"
Rscript -e "source('tests/test-resultsFormatter.R')"
```

---

## 9. Troubleshooting

### "Module not found / LLM Tools menu not appearing"

1. Confirm Jamovi **2.3 or later** is installed.
2. Check the `.jmo` file is not corrupted: re-build from source.
3. Make sure you **restarted Jamovi** after installation.
4. On Windows, ensure the `.jmo` file is not blocked by Windows security:
   - Right-click the file → Properties → tick **"Unblock"** → OK.
5. Try installing the `.jmo` from the **Jamovi library** tab instead:
   - Open Jamovi → ≡ menu → **Manage modules** → **Jamovi library** →
     search for "LLM Assistant".

### "R package `jmvcore` not found"

The Jamovi bundled R is separate from your system R. Install inside Jamovi's R:

```r
# Find Jamovi's bundled R executable, then:
# Windows:  "C:\Program Files\jamovi\R\bin\Rscript.exe" -e "install.packages('jmvcore')"
# macOS:    /Applications/jamovi.app/Contents/MacOS/Rscript -e "install.packages('jmvcore')"
# Linux:    /usr/lib/jamovi/bin/Rscript -e "install.packages('jmvcore')"
```

Or within Jamovi itself: open the **R console** (≡ → R console) and run:
```r
install.packages("jmvcore")
```

### "Build fails: missing file `NAMESPACE`"

Run `devtools::document()` or `roxygen2::roxygenise()` from the repo root to
generate the `NAMESPACE` file before building:

```r
install.packages("devtools")
devtools::document()      # generates NAMESPACE and man/ pages
library(jmvtools)
jmvtools::build()
```

### "API key field not saving between sessions"

This is **by design** — the API key is session-only and is never persisted.
You must re-enter it each time you open a Jamovi session. This protects
your credentials.

### "Analysis gives unexpected results"

1. Check the **Validation Report** section for warnings about missing values
   or small sample sizes.
2. Check the **Assumption Checking** section — if assumptions are violated,
   the module automatically switches to a more appropriate test (e.g. Welch's
   t-test when variances are unequal).
3. Ensure the correct **Outcome Variable** and **Grouping Variable** are
   selected.

### Getting more help

- Open a GitHub issue: https://github.com/Arjun-Babu-Raj/CFMProjectChiklod/issues
- Jamovi community forum: https://forum.cogsci.nl/categories/jamovi
- Jamovi documentation: https://www.jamovi.org/developer

---

## 📄 File Structure Reference

```
CFMProjectChiklod/
├── DESCRIPTION                     ← R package metadata (required by Jamovi)
├── package.yaml                    ← Jamovi module manifest
├── jamovi/
│   └── llmAssistant.a.yaml         ← Jamovi analysis UI definition
├── R/
│   ├── inputValidation.R           ← Input validation framework
│   ├── assumptionChecker.R         ← Statistical assumption tests
│   ├── analysisWorkflow.R          ← Three-phase analysis orchestrator
│   ├── resultsFormatter.R          ← Results formatting functions
│   └── promptEngine.R              ← Engineered LLM prompts
└── tests/
    ├── test-inputValidation.R
    ├── test-assumptionChecker.R
    ├── test-analysisWorkflow.R
    └── test-resultsFormatter.R
```

---

*Built for the Department of Community and Family Medicine, AIIMS Bhopal.*
