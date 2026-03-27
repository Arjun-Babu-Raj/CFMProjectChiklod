#' Results Formatter for Jamovi LLM Assistant
#'
#' Formats analysis results into human-readable tables and reports including:
#'   - Test name and type
#'   - Descriptive statistics
#'   - Test statistic, degrees of freedom, and p-value
#'   - Effect size with interpretation
#'   - Plain-language interpretation
#'   - Confidence intervals
#'   - Assumption status summary

# ── Helpers ────────────────────────────────────────────────────────────────────

#' Format a numeric value for display, handling NAs
#'
#' @param x Numeric
#' @param digits Number of decimal places (default 3)
#' @return Character string
fmt <- function(x, digits = 3) {
  if (is.null(x) || (length(x) == 1 && is.na(x))) return("NA")
  formatC(round(as.numeric(x), digits), format = "f", digits = digits)
}

#' Format p-value with significance stars
#'
#' @param p Numeric p-value
#' @return Character string like "0.032 *"
fmt_p <- function(p) {
  if (is.na(p)) return("NA")
  stars <- if (p < 0.001) "***"
           else if (p < 0.01) "**"
           else if (p < 0.05) "*"
           else if (p < 0.10) "."
           else ""
  paste0(formatC(p, format = "f", digits = 4), if (nchar(stars) > 0) paste0(" ", stars) else "")
}

#' Build a padded results table from a named list of label-value pairs
#'
#' @param pairs Named list where names are labels and values are display strings
#' @param title Optional section title
#' @return Character string of the formatted table
build_results_table <- function(pairs, title = NULL) {
  labels <- names(pairs)
  values <- unlist(pairs, use.names = FALSE)

  max_label <- max(nchar(labels))
  lines <- character(0)

  if (!is.null(title)) {
    border <- strrep("-", max_label + nchar(max(nchar(values))) + 5)
    lines  <- c(lines, title, border)
  }

  for (i in seq_along(labels)) {
    pad   <- strrep(" ", max_label - nchar(labels[i]))
    lines <- c(lines, sprintf("  %s%s : %s", labels[i], pad, values[i]))
  }
  paste(lines, collapse = "\n")
}


# ── Per-Test Formatters ────────────────────────────────────────────────────────

#' Format t-test results into a comprehensive results table
#'
#' @param result List returned by \code{run_t_test()} in analysisWorkflow.R
#' @param assumption_status Character vector of violated assumption names
#'   (may be empty)
#' @return Character string (printable report)
#' @examples
#' df <- data.frame(score = c(rnorm(30,75,8), rnorm(30,72,9)),
#'                  sex = rep(c("F","M"), each=30))
#' res <- run_t_test(df, "score", "sex")
#' cat(format_t_test_results(res))
format_t_test_results <- function(result, assumption_status = character(0)) {
  g <- result$groups

  desc_g1 <- sprintf("Mean=%.2f (SD=%.2f), n=%d",
                     result$means[1], result$sds[1], result$ns[1])
  desc_g2 <- sprintf("Mean=%.2f (SD=%.2f), n=%d",
                     result$means[2], result$sds[2], result$ns[2])

  ci <- sprintf("[%.3f, %.3f]",
                result$conf_int[1], result$conf_int[2])

  pairs <- list(
    "Test Name"               = result$test_name,
    "Group 1 Descriptives"    = sprintf("%s: %s", g[1], desc_g1),
    "Group 2 Descriptives"    = sprintf("%s: %s", g[2], desc_g2),
    "Test Statistic (t)"      = fmt(result$statistic),
    "Degrees of Freedom"      = fmt(result$df, 1),
    "P-value"                 = fmt_p(result$p_value),
    "Effect Size (Cohen's d)" = sprintf("%s (%s effect)", fmt(result$cohen_d), result$effect_label),
    "95% Confidence Interval" = ci,
    "Interpretation"          = result$interpretation,
    "Assumptions Met"         = if (length(assumption_status) == 0) "All checked"
                                else paste("Violated:", paste(assumption_status, collapse = ", "))
  )

  body <- build_results_table(pairs, title = "=== INDEPENDENT t-TEST RESULTS ===")
  paste(body, "\n", sep = "")
}


#' Format ANOVA results into a comprehensive results table
#'
#' @param result List returned by \code{run_anova()}
#' @param assumption_status Character vector of violated assumption names
#' @return Character string
#' @examples
#' res <- run_anova(iris, "Sepal.Length", "Species")
#' cat(format_anova_results(res))
format_anova_results <- function(result, assumption_status = character(0)) {
  group_desc_parts <- vapply(names(result$group_stats), function(g) {
    gs <- result$group_stats[[g]]
    sprintf("%s: Mean=%.2f SD=%.2f n=%d", g, gs["mean"], gs["sd"], gs["n"])
  }, character(1))
  group_desc <- paste(group_desc_parts, collapse = "; ")

  pairs <- list(
    "Test Name"               = result$test_name,
    "Group Descriptives"      = group_desc,
    "Test Statistic (F)"      = fmt(result$F_stat),
    "Degrees of Freedom"      = sprintf("%d, %d", result$df1, result$df2),
    "P-value"                 = fmt_p(result$p_value),
    "Effect Size (eta²)"      = sprintf("%s (%s effect)", fmt(result$eta_squared),
                                        result$effect_label),
    "Interpretation"          = result$interpretation,
    "Assumptions Met"         = if (length(assumption_status) == 0) "All checked"
                                else paste("Violated:", paste(assumption_status, collapse = ", "))
  )

  build_results_table(pairs, title = "=== ONE-WAY ANOVA RESULTS ===")
}


#' Format correlation results into a comprehensive results table
#'
#' @param result List returned by \code{run_correlation()}
#' @param assumption_status Character vector of violated assumption names
#' @return Character string
#' @examples
#' res <- run_correlation(mtcars, "mpg", "wt")
#' cat(format_correlation_results(res))
format_correlation_results <- function(result, assumption_status = character(0)) {
  ci <- if (!any(is.na(result$conf_int)))
    sprintf("[%.3f, %.3f]", result$conf_int[1], result$conf_int[2])
  else "Not available"

  pairs <- list(
    "Test Name"               = result$test_name,
    "Variables"               = sprintf("%s vs %s", result$x_var, result$y_var),
    "Correlation (r)"         = fmt(result$r),
    "Degrees of Freedom"      = if (!is.na(result$df)) fmt(result$df, 0) else "NA",
    "P-value"                 = fmt_p(result$p_value),
    "Effect Size"             = sprintf("%s (%s effect)", fmt(result$r), result$effect_label),
    "95% Confidence Interval" = ci,
    "Interpretation"          = result$interpretation,
    "Assumptions Met"         = if (length(assumption_status) == 0) "All checked"
                                else paste("Violated:", paste(assumption_status, collapse = ", "))
  )

  build_results_table(pairs, title = "=== CORRELATION RESULTS ===")
}


#' Format chi-square results into a comprehensive results table
#'
#' @param result List returned by \code{run_chi_square()}
#' @param assumption_status Character vector of violated assumption names
#' @return Character string
#' @examples
#' df <- data.frame(sex=sample(c("M","F"),80,TRUE), pass=sample(c("Y","N"),80,TRUE))
#' res <- run_chi_square(df, "sex", "pass")
#' cat(format_chi_square_results(res))
format_chi_square_results <- function(result, assumption_status = character(0)) {
  pairs <- list(
    "Test Name"                = result$test_name,
    "Test Statistic (χ²)"     = fmt(result$chi2),
    "Degrees of Freedom"       = as.character(result$df),
    "P-value"                  = fmt_p(result$p_value),
    "Effect Size (Cramér's V)" = sprintf("%s (%s association)", fmt(result$cramers_v),
                                         result$effect_label),
    "Interpretation"           = result$interpretation,
    "Assumptions Met"          = if (length(assumption_status) == 0) "All checked"
                                 else paste("Violated:", paste(assumption_status, collapse = ", "))
  )

  build_results_table(pairs, title = "=== CHI-SQUARE TEST RESULTS ===")
}


#' Format linear regression results into a comprehensive results table
#'
#' @param result List returned by \code{run_regression()}
#' @param assumption_status Character vector of violated assumption names
#' @return Character string
#' @examples
#' res <- run_regression(mtcars, "mpg", c("wt","hp"))
#' cat(format_regression_results(res))
format_regression_results <- function(result, assumption_status = character(0)) {
  coef_lines <- apply(result$coefficients, 1, function(row) {
    sprintf("  %-20s b=%-8s SE=%-8s t=%-8s p=%s",
            row["variable"],
            fmt(as.numeric(row["estimate"])),
            fmt(as.numeric(row["std_error"])),
            fmt(as.numeric(row["t_value"])),
            fmt_p(as.numeric(row["p_value"])))
  })

  header_pairs <- list(
    "Test Name"           = result$test_name,
    "Outcome Variable"    = result$outcome_var,
    "Predictor Variables" = paste(result$predictor_vars, collapse = ", "),
    "R-squared"           = fmt(result$r_squared),
    "Adjusted R-squared"  = fmt(result$adj_r_squared),
    "Test Statistic (F)"  = fmt(result$F_stat),
    "Degrees of Freedom"  = sprintf("%d, %d", result$df1, result$df2),
    "P-value"             = fmt_p(result$p_value),
    "Interpretation"      = result$interpretation,
    "Assumptions Met"     = if (length(assumption_status) == 0) "All checked"
                            else paste("Violated:", paste(assumption_status, collapse = ", "))
  )

  header <- build_results_table(header_pairs, title = "=== LINEAR REGRESSION RESULTS ===")
  coef_section <- paste(
    c("\nCoefficients:", coef_lines),
    collapse = "\n"
  )

  paste(header, coef_section, sep = "\n")
}


# ── Assumption Summary Table ──────────────────────────────────────────────────

#' Format assumption check results into a summary table
#'
#' @param assumption_result List returned by \code{check_assumptions()}
#' @return Character string
#' @examples
#' ar <- check_assumptions(iris, "t_test", "Sepal.Length", group_var="Species")
#' cat(format_assumption_table(ar))
format_assumption_table <- function(assumption_result) {
  if (is.null(assumption_result)) {
    return("No assumption checks performed.")
  }

  met      <- assumption_result$met
  violated <- assumption_result$violated

  lines <- c("=== ASSUMPTION STATUS SUMMARY ===")

  assumption_names <- c(
    "normality"        = "Normality (Shapiro-Wilk/KS)",
    "homogeneity"      = "Homogeneity of Variance (Levene)",
    "independence"     = "Independence (Durbin-Watson)",
    "linearity"        = "Linearity (Correlation)",
    "multicollinearity"= "Multicollinearity (VIF)"
  )

  checked <- names(met)

  for (a_key in names(assumption_names)) {
    a_label <- assumption_names[a_key]
    if (a_key %in% checked) {
      status <- if (isTRUE(met[a_key]) || (a_key == "multicollinearity" && !isTRUE(met[a_key]))) {
        if (a_key == "multicollinearity") {
          if (isTRUE(met[a_key])) "✗ VIOLATED" else "✓ MET"
        } else {
          if (isTRUE(met[a_key])) "✓ MET" else "✗ VIOLATED"
        }
      } else {
        "✗ VIOLATED"
      }
      lines <- c(lines, sprintf("  %-45s %s", a_label, status))
    }
  }

  if (length(violated) > 0) {
    lines <- c(lines, "",
               "Remedial Actions:",
               "  • Normality violated  → Consider Mann-Whitney U / Kruskal-Wallis / Spearman",
               "  • Homogeneity violated → Use Welch's t-test or Welch ANOVA",
               "  • Independence violated→ Use time-series models or mixed models",
               "  • Linearity violated   → Consider polynomial terms or non-linear models",
               "  • Multicollinearity    → Remove correlated predictors or apply regularisation"
    )
  } else {
    lines <- c(lines, "", "✓ All checked assumptions are met. Parametric tests are appropriate.")
  }

  paste(lines, collapse = "\n")
}


# ── Full Workflow Report Formatter ────────────────────────────────────────────

#' Format a complete workflow result object into a polished text report
#'
#' @param workflow_result List returned by \code{run_analysis_workflow()}
#' @return Character string containing the full formatted report
#' @examples
#' df <- data.frame(score = c(rnorm(30,75,8), rnorm(30,72,9)),
#'                  sex = rep(c("F","M"), each=30))
#' wf  <- run_analysis_workflow("Compare scores", df, "t_test", "score", "sex")
#' cat(format_full_report(wf))
format_full_report <- function(workflow_result) {
  parts <- character(0)

  # Validation
  if (!is.null(workflow_result$validation)) {
    parts <- c(parts, workflow_result$validation$report, "")
  }

  # Descriptive
  if (!is.null(workflow_result$descriptive)) {
    parts <- c(parts, workflow_result$descriptive$report, "")
  }

  # Assumptions
  if (!is.null(workflow_result$assumptions)) {
    parts <- c(parts, workflow_result$assumptions$report, "")
    parts <- c(parts, format_assumption_table(workflow_result$assumptions), "")
  }

  # Test results
  tr <- workflow_result$test
  if (!is.null(tr) && is.null(tr$error)) {
    violated <- if (!is.null(workflow_result$assumptions))
      workflow_result$assumptions$violated
    else character(0)

    formatted_test <- tryCatch({
      switch(tr$test_name,
        "Independent t-test (Welch)"   = ,
        "Independent t-test (Student)" = format_t_test_results(tr, violated),
        "One-way ANOVA"                = format_anova_results(tr, violated),
        "Pearson Correlation"          = ,
        "Spearman Correlation"         = format_correlation_results(tr, violated),
        "Chi-square Test of Independence" = format_chi_square_results(tr, violated),
        "Linear Regression"            = format_regression_results(tr, violated),
        tr$interpretation
      )
    }, error = function(e) tr$interpretation)

    parts <- c(parts, formatted_test, "")
  } else if (!is.null(tr) && !is.null(tr$error)) {
    parts <- c(parts, paste("=== TEST ERROR ===\n", tr$error), "")
  }

  # Overall interpretation
  parts <- c(parts, "=== INTERPRETATION ===")
  if (!is.null(tr) && is.null(tr$error)) {
    parts <- c(parts, tr$interpretation)
    if (!is.null(workflow_result$assumptions) &&
        length(workflow_result$assumptions$violated) > 0) {
      parts <- c(parts, "",
        sprintf("⚠ Assumption(s) violated: %s",
                paste(workflow_result$assumptions$violated, collapse = ", ")),
        "  For the most robust inference, consider the non-parametric alternatives",
        "  listed in the Assumption Status Summary above."
      )
    }
  } else {
    parts <- c(parts, "Analysis could not be completed. Review validation report.")
  }

  paste(parts, collapse = "\n")
}
