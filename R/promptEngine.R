#' Prompt Engineering Module for Jamovi LLM Assistant
#'
#' Generates sophisticated, context-aware prompt templates that guide
#' Gemini (or any compatible LLM) to produce structured, statistically
#' rigorous analysis recommendations and interpretations.

# ── Constants ─────────────────────────────────────────────────────────────────

#' Supported analysis type labels for prompt construction
ANALYSIS_TYPE_LABELS <- list(
  t_test      = "Independent Samples t-test",
  anova       = "One-Way ANOVA",
  correlation = "Pearson/Spearman Correlation",
  regression  = "Linear Regression",
  chi_square  = "Chi-Square Test of Independence",
  descriptive = "Descriptive Statistics"
)

#' System-level LLM role definition
SYSTEM_ROLE_PROMPT <- paste(
  "You are an expert biostatistician and data analysis assistant integrated",
  "into the Jamovi statistical software platform. Your role is to:",
  "1. Recommend appropriate statistical analyses based on the user's query and data structure.",
  "2. Guide users through assumption checking before applying inferential tests.",
  "3. Interpret results in plain language with appropriate effect size context.",
  "4. Suggest remedial actions when statistical assumptions are violated.",
  "5. Always prioritize scientific rigor while remaining accessible to non-statisticians.",
  sep = "\n"
)


# ── Data Context Builder ───────────────────────────────────────────────────────

#' Build a concise data context string for injection into prompts
#'
#' @param data A data.frame (or NULL)
#' @param max_rows Maximum number of sample rows to include (default 3)
#' @return Character string describing the dataset
#' @examples
#' build_data_context(iris)
build_data_context <- function(data, max_rows = 3) {
  if (is.null(data) || !is.data.frame(data)) {
    return("No dataset provided.")
  }

  n_rows <- nrow(data)
  n_cols <- ncol(data)

  col_info <- vapply(names(data), function(v) {
    x <- data[[v]]
    type <- if (is.numeric(x)) "numeric"
            else if (is.factor(x)) "factor"
            else if (is.character(x)) "character"
            else class(x)[1]

    detail <- if (is.numeric(x) && n_rows > 0) {
      sprintf("range [%.2f, %.2f]", min(x, na.rm = TRUE), max(x, na.rm = TRUE))
    } else if ((is.factor(x) || is.character(x)) && n_rows > 0) {
      lvls <- unique(as.character(x))
      lvls <- lvls[!is.na(lvls)]
      n_unique <- length(lvls)
      if (n_unique <= 6) {
        paste0("levels: ", paste(lvls, collapse = ", "))
      } else {
        sprintf("%d unique values", n_unique)
      }
    } else ""

    sprintf("  - %s (%s) %s", v, type, detail)
  }, character(1))

  n_missing_total <- sum(is.na(data))

  lines <- c(
    sprintf("Dataset: %d rows × %d columns", n_rows, n_cols),
    "Variables:",
    col_info
  )

  if (n_missing_total > 0) {
    lines <- c(lines,
      sprintf("Missing values: %d total across all variables", n_missing_total))
  }

  paste(lines, collapse = "\n")
}


# ── Core Prompt Templates ──────────────────────────────────────────────────────

#' Generate the main analysis recommendation prompt
#'
#' Constructs a structured prompt asking the LLM to recommend the most
#' appropriate statistical analysis, verify assumptions, and outline an
#' analysis plan.
#'
#' @param query Character user query
#' @param data_context Character string from \code{build_data_context()}
#' @param analysis_type Optional character. If provided, focuses the prompt
#'   on this analysis type.
#' @return Character string (prompt ready for LLM submission)
#' @examples
#' ctx <- build_data_context(iris)
#' cat(build_analysis_prompt("Compare petal lengths by species", ctx))
build_analysis_prompt <- function(query, data_context, analysis_type = NULL) {
  type_guidance <- if (!is.null(analysis_type) && analysis_type %in% names(ANALYSIS_TYPE_LABELS)) {
    sprintf(
      "\nThe user is interested in performing a %s. Focus your response accordingly.",
      ANALYSIS_TYPE_LABELS[[analysis_type]]
    )
  } else ""

  prompt <- sprintf(
'%s

---
USER QUERY:
"%s"

DATA CONTEXT:
%s
%s

---
INSTRUCTIONS:
Please provide a structured statistical analysis plan with the following sections:

### 1. RECOMMENDED ANALYSIS
- State the most appropriate statistical test for this query and data
- Explain why this test is suitable
- List any alternative tests if assumptions are violated

### 2. ASSUMPTION CHECKING REQUIRED
List each assumption that must be verified before applying the test:
- Assumption name
- How to test it (specific test or method)
- What to do if violated

### 3. DESCRIPTIVE STATISTICS TO REPORT
List which descriptive statistics are most relevant for this analysis.

### 4. EXPECTED OUTPUT FORMAT
Describe what the results table should contain:
- Test statistic (name and symbol)
- Degrees of freedom
- P-value interpretation
- Effect size measure and benchmark
- Confidence interval

### 5. INTERPRETATION TEMPLATE
Provide a template for interpreting results in plain language, including:
- How to state the key finding
- How to describe effect size in practical terms
- When to conclude significance vs. practical significance

Respond in a clear, structured format that a health science researcher would find useful.',
    SYSTEM_ROLE_PROMPT,
    query,
    data_context,
    type_guidance
  )

  prompt
}


#' Generate the assumption violation response prompt
#'
#' When assumptions are violated, this prompt asks the LLM to suggest
#' appropriate remedial actions and alternative tests.
#'
#' @param violated_assumptions Character vector of violated assumption names
#' @param analysis_type The originally intended analysis type
#' @param data_context Character string from \code{build_data_context()}
#' @return Character string (prompt)
#' @examples
#' cat(build_assumption_violation_prompt(c("normality","homogeneity"), "t_test",
#'                                       build_data_context(iris)))
build_assumption_violation_prompt <- function(violated_assumptions,
                                               analysis_type,
                                               data_context) {
  violated_list <- paste(
    sprintf("  - %s", violated_assumptions),
    collapse = "\n"
  )

  intended_label <- if (analysis_type %in% names(ANALYSIS_TYPE_LABELS)) {
    ANALYSIS_TYPE_LABELS[[analysis_type]]
  } else analysis_type

  sprintf(
'%s

---
CONTEXT:
The user intended to perform a %s, but the following statistical assumptions
were found to be VIOLATED:

%s

DATA CONTEXT:
%s

---
INSTRUCTIONS:
The user needs guidance on how to proceed. Please provide:

### 1. VIOLATION IMPACT
For each violated assumption, briefly explain:
- Why this assumption matters for the intended test
- The consequence of proceeding without addressing it

### 2. RECOMMENDED ALTERNATIVES
For each violated assumption, suggest:
a) The most appropriate non-parametric alternative test
b) Any data transformation that might restore the assumption
c) Any robust variant of the original test

### 3. PRIORITISED RECOMMENDATION
Based on the violations, state clearly:
- Which alternative test you recommend and why
- How the interpretation would change compared to the original test
- Whether the alternative test has its own assumption requirements

### 4. REPORTING GUIDANCE
Advise how to transparently report in a research paper or report that:
- Assumptions were checked
- Violations were found
- The alternative test was used

Keep the response practical and actionable for a health science researcher.',
    SYSTEM_ROLE_PROMPT,
    intended_label,
    violated_list,
    data_context
  )
}


#' Generate the results interpretation prompt
#'
#' Takes computed results and asks the LLM to provide a rich, context-aware
#' plain-language interpretation.
#'
#' @param results_summary Character string summarising computed test results
#'   (e.g. from \code{format_full_report()})
#' @param query Character user query
#' @param assumption_status Character vector of violated assumptions (may be empty)
#' @return Character string (prompt)
#' @examples
#' cat(build_interpretation_prompt("t(298)=2.15, p=0.032, d=0.28",
#'                                  "Compare scores between male and female students"))
build_interpretation_prompt <- function(results_summary, query,
                                         assumption_status = character(0)) {
  assumption_note <- if (length(assumption_status) > 0) {
    sprintf(
      "\n\nNOTE: The following assumptions were violated: %s\nAcknowledge this in your interpretation.",
      paste(assumption_status, collapse = ", ")
    )
  } else ""

  sprintf(
'%s

---
USER QUERY:
"%s"

COMPUTED RESULTS:
%s
%s

---
INSTRUCTIONS:
Please provide a comprehensive, plain-language interpretation of the results above.
Structure your response as follows:

### MAIN FINDING
State the key result in one or two sentences that a non-statistician can understand.
Include the direction and magnitude of the effect.

### STATISTICAL EVIDENCE
Briefly summarise the statistical evidence:
- Report the test statistic, degrees of freedom, and p-value
- State whether the result is statistically significant (alpha = 0.05)
- Include the confidence interval interpretation if available

### EFFECT SIZE INTERPRETATION
Interpret the practical significance:
- Name the effect size measure used
- Describe whether the effect is negligible / small / medium / large
- Translate this into real-world terms relevant to the research context

### CONTEXTUAL RECOMMENDATIONS
Based on the findings:
1. What do these results mean for practice or decision-making?
2. What further analyses would you recommend?
3. Are there any important caveats or limitations to acknowledge?

Keep the language accessible, precise, and suitable for a research report.',
    SYSTEM_ROLE_PROMPT,
    query,
    results_summary,
    assumption_note
  )
}


#' Generate a data quality report prompt
#'
#' Asks the LLM to comment on data quality issues detected during validation.
#'
#' @param validation_report Character string from \code{validate_inputs()$report}
#' @param data_context Character string from \code{build_data_context()}
#' @return Character string (prompt)
#' @examples
#' vr <- validate_inputs("Compare groups", airquality, "t_test")
#' cat(build_data_quality_prompt(vr$report, build_data_context(airquality)))
build_data_quality_prompt <- function(validation_report, data_context) {
  sprintf(
'%s

---
DATA QUALITY REPORT:
%s

DATA CONTEXT:
%s

---
INSTRUCTIONS:
Based on the data quality issues identified above, please advise the user on:

### 1. CRITICAL ISSUES
Identify any issues that must be resolved before proceeding with analysis.

### 2. MISSING DATA STRATEGY
If missing values were detected:
- Explain the impact of missing data on the planned analysis
- Recommend an appropriate missing data strategy:
  a) Complete case analysis (listwise deletion)
  b) Mean/median imputation
  c) Multiple imputation
  d) Model-based imputation
- Describe when each strategy is appropriate

### 3. OUTLIER HANDLING
If outliers were detected:
- Explain potential impact on the analysis
- Suggest appropriate handling strategies:
  a) Investigation and verification
  b) Robust statistical methods
  c) Transformation approaches
  d) Exclusion criteria and reporting

### 4. SAMPLE SIZE CONSIDERATIONS
If sample size warnings were raised:
- Comment on statistical power implications
- Suggest whether additional data collection is needed
- Recommend conservative interpretation if sample is small

Provide practical, actionable guidance appropriate for a health research context.',
    SYSTEM_ROLE_PROMPT,
    validation_report,
    data_context
  )
}


# ── Prompt Builder Factory ─────────────────────────────────────────────────────

#' Build the appropriate prompt based on workflow stage
#'
#' This is the main entry point for the prompt engine. It selects and
#' constructs the correct prompt based on the current stage of analysis.
#'
#' @param stage One of: "recommend", "violation", "interpret", "quality"
#' @param query Character user query
#' @param data A data.frame (used to build data context)
#' @param analysis_type Optional analysis type string
#' @param results_summary Optional character: formatted results for
#'   interpretation stage
#' @param violated_assumptions Optional character vector for violation stage
#' @param validation_report Optional character for quality stage
#' @return Character string (ready-to-send LLM prompt)
#' @examples
#' prompt <- build_prompt("recommend",
#'                        query = "Compare test scores by gender",
#'                        data  = iris,
#'                        analysis_type = "t_test")
#' cat(prompt)
build_prompt <- function(stage, query, data = NULL,
                          analysis_type = NULL,
                          results_summary = NULL,
                          violated_assumptions = character(0),
                          validation_report = NULL) {
  data_context <- build_data_context(data)

  switch(stage,
    recommend = build_analysis_prompt(query, data_context, analysis_type),

    violation = {
      if (length(violated_assumptions) == 0)
        stop("violated_assumptions must be provided for stage='violation'.")
      if (is.null(analysis_type))
        stop("analysis_type must be provided for stage='violation'.")
      build_assumption_violation_prompt(violated_assumptions, analysis_type, data_context)
    },

    interpret = {
      if (is.null(results_summary))
        stop("results_summary must be provided for stage='interpret'.")
      build_interpretation_prompt(results_summary, query, violated_assumptions)
    },

    quality = {
      if (is.null(validation_report))
        stop("validation_report must be provided for stage='quality'.")
      build_data_quality_prompt(validation_report, data_context)
    },

    stop(sprintf("Unknown stage '%s'. Choose: recommend, violation, interpret, quality.", stage))
  )
}
