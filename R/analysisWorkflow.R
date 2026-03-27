#' Structured Analysis Workflow for Jamovi LLM Assistant
#'
#' Orchestrates the three-phase analysis pipeline:
#'   1. Descriptive Analysis
#'   2. Assumption Checking
#'   3. Hypothesis Testing
#'
#' Depends on: inputValidation.R, assumptionChecker.R, resultsFormatter.R

# Source companion modules (relative to this file when used interactively)
.source_companion <- function(file) {
  base <- tryCatch(dirname(sys.frame(1)$ofile), error = function(e) ".")
  full <- file.path(base, file)
  if (file.exists(full)) source(full, local = FALSE)
}


# ── Phase 1: Descriptive Analysis ─────────────────────────────────────────────

#' Compute descriptive statistics for a numeric variable
#'
#' @param x Numeric vector
#' @param var_name Label for display
#' @return Named list with mean, median, sd, min, max, range, q1, q3, iqr,
#'   n, n_missing, skewness, kurtosis
#' @examples
#' describe_variable(mtcars$mpg, "mpg")
describe_variable <- function(x, var_name = "variable") {
  x_clean <- x[!is.na(x)]
  n       <- length(x_clean)
  n_miss  <- sum(is.na(x))

  if (n == 0) {
    return(list(
      variable  = var_name,
      n         = 0L,
      n_missing = as.integer(n_miss),
      mean      = NA_real_, median    = NA_real_,
      sd        = NA_real_, min       = NA_real_,
      max       = NA_real_, range     = NA_real_,
      q1        = NA_real_, q3        = NA_real_,
      iqr       = NA_real_, skewness  = NA_real_,
      kurtosis  = NA_real_
    ))
  }

  q   <- quantile(x_clean, probs = c(0.25, 0.75))
  mn  <- mean(x_clean)
  med <- median(x_clean)
  sd_ <- if (n > 1) sd(x_clean) else NA_real_

  # Skewness & excess kurtosis (moment-based)
  skew <- if (n > 2 && !is.na(sd_) && sd_ > 0) {
    (sum((x_clean - mn)^3) / n) / sd_^3
  } else NA_real_

  kurt <- if (n > 3 && !is.na(sd_) && sd_ > 0) {
    (sum((x_clean - mn)^4) / n) / sd_^4 - 3
  } else NA_real_

  list(
    variable  = var_name,
    n         = as.integer(n),
    n_missing = as.integer(n_miss),
    mean      = round(mn,  4),
    median    = round(med, 4),
    sd        = round(sd_, 4),
    min       = round(min(x_clean),  4),
    max       = round(max(x_clean),  4),
    range     = round(diff(range(x_clean)), 4),
    q1        = round(q[1], 4),
    q3        = round(q[2], 4),
    iqr       = round(q[2] - q[1], 4),
    skewness  = round(skew, 4),
    kurtosis  = round(kurt, 4)
  )
}


#' Compute frequency table for a categorical variable
#'
#' @param x Categorical vector (factor, character, logical)
#' @param var_name Label for display
#' @return data.frame with columns: category, count, percent
#' @examples
#' frequency_table(iris$Species, "Species")
frequency_table <- function(x, var_name = "variable") {
  x_clean <- x[!is.na(x)]
  tbl     <- table(x_clean)
  n_total <- length(x_clean)

  df <- data.frame(
    variable         = var_name,
    category         = names(tbl),
    count            = as.integer(tbl),
    percent          = round(as.numeric(tbl) / n_total * 100, 2),
    stringsAsFactors = FALSE
  )
  df[order(df$count, decreasing = TRUE), ]
}


#' Missing data pattern summary
#'
#' @param data A data.frame
#' @return data.frame with variable, n_missing, pct_missing columns
#' @examples
#' missing_data_report(airquality)
missing_data_report <- function(data) {
  if (!is.data.frame(data)) stop("data must be a data.frame.")
  n <- nrow(data)
  miss <- vapply(data, function(x) sum(is.na(x)), integer(1))
  data.frame(
    variable    = names(miss),
    n_missing   = as.integer(miss),
    pct_missing = round(miss / n * 100, 2),
    stringsAsFactors = FALSE
  )
}


#' Run the full descriptive analysis phase
#'
#' @param data A data.frame
#' @param numeric_vars Character vector of numeric variable names to summarise
#' @param categorical_vars Character vector of categorical variable names
#' @return List with fields: numeric_stats (list), frequency_tables (list),
#'   missing_report (data.frame), report (character)
#' @examples
#' run_descriptive_phase(iris,
#'   numeric_vars     = c("Sepal.Length", "Sepal.Width"),
#'   categorical_vars = "Species")
run_descriptive_phase <- function(data, numeric_vars = NULL,
                                  categorical_vars = NULL) {
  if (!is.data.frame(data)) stop("data must be a data.frame.")

  num_stats  <- list()
  freq_tbls  <- list()

  if (!is.null(numeric_vars)) {
    for (v in intersect(numeric_vars, names(data))) {
      num_stats[[v]] <- describe_variable(data[[v]], v)
    }
  }

  if (!is.null(categorical_vars)) {
    for (v in intersect(categorical_vars, names(data))) {
      freq_tbls[[v]] <- frequency_table(data[[v]], v)
    }
  }

  miss_rpt <- missing_data_report(data)

  # Build human-readable report
  lines <- c("=== DESCRIPTIVE ANALYSIS ===")

  for (nm in names(num_stats)) {
    s <- num_stats[[nm]]
    lines <- c(lines,
      sprintf("%s:", nm),
      sprintf("  Mean: %.2f (SD: %.2f)", s$mean, s$sd),
      sprintf("  Median: %.2f (IQR: %.2f–%.2f)", s$median, s$q1, s$q3),
      sprintf("  n = %d  |  Missing: %d  |  Range: [%.2f, %.2f]",
              s$n, s$n_missing, s$min, s$max)
    )
    if (!is.na(s$skewness)) {
      lines <- c(lines,
        sprintf("  Skewness: %.3f  |  Excess Kurtosis: %.3f",
                s$skewness, s$kurtosis))
    }
    lines <- c(lines, "")
  }

  for (nm in names(freq_tbls)) {
    ft <- freq_tbls[[nm]]
    lines <- c(lines, sprintf("Frequency table – %s:", nm))
    for (i in seq_len(nrow(ft))) {
      lines <- c(lines,
        sprintf("  %-20s: %d (%.1f%%)", ft$category[i], ft$count[i], ft$percent[i]))
    }
    lines <- c(lines, "")
  }

  miss_vars <- miss_rpt[miss_rpt$n_missing > 0, ]
  if (nrow(miss_vars) > 0) {
    lines <- c(lines, "Missing Data:")
    for (i in seq_len(nrow(miss_vars))) {
      lines <- c(lines,
        sprintf("  %s: %d missing (%.1f%%)",
                miss_vars$variable[i], miss_vars$n_missing[i],
                miss_vars$pct_missing[i]))
    }
    lines <- c(lines, "")
  }

  list(
    numeric_stats     = num_stats,
    frequency_tables  = freq_tbls,
    missing_report    = miss_rpt,
    report            = paste(lines, collapse = "\n")
  )
}


# ── Phase 2: Assumption Checking (delegates to assumptionChecker.R) ───────────

#' Run the assumption checking phase
#'
#' @param data A data.frame
#' @param analysis_type Character. One of "t_test", "anova", "correlation",
#'   "regression", "chi_square", "descriptive"
#' @param outcome_var Name of the primary outcome variable
#' @param group_var Name of grouping variable (t_test / anova)
#' @param predictor_vars Character vector of predictor names (regression)
#' @param alpha Significance level (default 0.05)
#' @return Output from \code{check_assumptions()} in assumptionChecker.R
run_assumption_phase <- function(data, analysis_type, outcome_var,
                                  group_var = NULL, predictor_vars = NULL,
                                  alpha = 0.05) {
  # check_assumptions is defined in assumptionChecker.R
  if (!exists("check_assumptions", mode = "function")) {
    stop("check_assumptions() not found. Source assumptionChecker.R first.")
  }
  check_assumptions(
    data            = data,
    analysis_type   = analysis_type,
    outcome_var     = outcome_var,
    group_var       = group_var,
    predictor_vars  = predictor_vars,
    alpha           = alpha
  )
}


# ── Phase 3: Hypothesis Testing ───────────────────────────────────────────────

#' Perform independent samples t-test (Welch or Student)
#'
#' @param data A data.frame
#' @param outcome_var Numeric outcome variable name
#' @param group_var Binary grouping variable name
#' @param equal_variances If FALSE (default), Welch's t-test is used
#' @param alpha Significance level (default 0.05)
#' @return List with test details including statistic, df, p_value,
#'   means, sds, ns, cohen_d, conf_int, significant, interpretation
#' @examples
#' df <- data.frame(score = c(rnorm(30, 75, 8), rnorm(30, 72, 9)),
#'                  sex   = rep(c("F", "M"), each = 30))
#' run_t_test(df, "score", "sex")
run_t_test <- function(data, outcome_var, group_var, equal_variances = FALSE,
                        alpha = 0.05) {
  groups   <- levels(as.factor(data[[group_var]]))
  if (length(groups) != 2)
    stop("t-test requires exactly 2 groups.")

  g1 <- data[[outcome_var]][data[[group_var]] == groups[1]]
  g2 <- data[[outcome_var]][data[[group_var]] == groups[2]]

  g1 <- g1[!is.na(g1)]
  g2 <- g2[!is.na(g2)]

  tt <- t.test(g1, g2, var.equal = equal_variances, conf.level = 1 - alpha)

  m1 <- mean(g1); m2 <- mean(g2)
  s1 <- sd(g1);   s2 <- sd(g2)
  n1 <- length(g1); n2 <- length(g2)

  # Pooled SD for Cohen's d
  sp <- sqrt(((n1 - 1) * s1^2 + (n2 - 1) * s2^2) / (n1 + n2 - 2))
  cohen_d <- if (sp > 0) (m1 - m2) / sp else NA_real_

  sig <- tt$p.value < alpha

  interp <- sprintf(
    "%s scored %.2f points %s on average. t(%.1f)=%.3f, p=%.4f%s. Cohen's d=%.3f (%s effect). 95%% CI: [%.3f, %.3f].",
    groups[1],
    abs(m1 - m2),
    if (m1 > m2) sprintf("higher than %s", groups[2]) else sprintf("lower than %s", groups[2]),
    tt$parameter,
    unname(tt$statistic),
    tt$p.value,
    if (sig) " *" else " (ns)",
    cohen_d,
    interpret_effect_size_d(abs(cohen_d)),
    tt$conf.int[1],
    tt$conf.int[2]
  )

  list(
    test_name      = if (equal_variances) "Independent t-test (Student)" else "Independent t-test (Welch)",
    groups         = groups,
    means          = c(g1 = m1, g2 = m2),
    sds            = c(g1 = s1, g2 = s2),
    ns             = c(g1 = n1, g2 = n2),
    statistic      = unname(tt$statistic),
    df             = unname(tt$parameter),
    p_value        = tt$p.value,
    conf_int       = as.numeric(tt$conf.int),
    cohen_d        = cohen_d,
    effect_label   = interpret_effect_size_d(abs(cohen_d)),
    significant    = sig,
    interpretation = interp
  )
}


#' Perform one-way ANOVA
#'
#' @param data A data.frame
#' @param outcome_var Numeric outcome variable name
#' @param group_var Grouping variable name (>= 2 levels)
#' @param alpha Significance level (default 0.05)
#' @return List with F statistic, df, p_value, eta_squared, group stats,
#'   significant, interpretation
#' @examples
#' run_anova(iris, "Sepal.Length", "Species")
run_anova <- function(data, outcome_var, group_var, alpha = 0.05) {
  formula_obj <- as.formula(paste(outcome_var, "~", group_var))
  fit <- aov(formula_obj, data = data)
  sm  <- summary(fit)[[1]]

  F_stat  <- sm["F value"][1, 1]
  df1     <- sm["Df"][1, 1]
  df2     <- sm["Df"][2, 1]
  p_val   <- sm["Pr(>F)"][1, 1]
  ss_b    <- sm["Sum Sq"][1, 1]
  ss_tot  <- sum(sm["Sum Sq"])

  eta2    <- ss_b / ss_tot

  sig     <- p_val < alpha

  group_stats <- tapply(data[[outcome_var]], data[[group_var]], function(x) {
    x_c <- x[!is.na(x)]
    c(mean = mean(x_c), sd = sd(x_c), n = length(x_c))
  })

  interp <- sprintf(
    "One-way ANOVA: F(%d,%d)=%.3f, p=%.4f%s. Eta-squared=%.3f (%s effect). %s",
    df1, df2, F_stat, p_val,
    if (sig) " *" else " (ns)",
    eta2,
    interpret_effect_size_eta2(eta2),
    if (sig) "Significant differences exist between groups."
    else "No significant difference between groups."
  )

  list(
    test_name      = "One-way ANOVA",
    F_stat         = F_stat,
    df1            = as.integer(df1),
    df2            = as.integer(df2),
    p_value        = p_val,
    eta_squared    = eta2,
    effect_label   = interpret_effect_size_eta2(eta2),
    group_stats    = group_stats,
    significant    = sig,
    interpretation = interp
  )
}


#' Perform Pearson / Spearman correlation test
#'
#' @param data A data.frame
#' @param x_var Name of first numeric variable
#' @param y_var Name of second numeric variable
#' @param method "pearson" (default) or "spearman"
#' @param alpha Significance level (default 0.05)
#' @return List with r, p_value, conf_int, significant, interpretation
#' @examples
#' run_correlation(mtcars, "mpg", "wt")
run_correlation <- function(data, x_var, y_var, method = "pearson", alpha = 0.05) {
  ct <- cor.test(data[[x_var]], data[[y_var]], method = method,
                 conf.level = 1 - alpha)

  r   <- unname(ct$estimate)
  sig <- ct$p.value < alpha

  ci  <- if (!is.null(ct$conf.int)) as.numeric(ct$conf.int) else c(NA_real_, NA_real_)

  interp <- sprintf(
    "%s correlation between '%s' and '%s': r=%.3f, p=%.4f%s (%s effect). 95%% CI: [%.3f, %.3f].",
    tools::toTitleCase(method),
    x_var, y_var,
    r,
    ct$p.value,
    if (sig) " *" else " (ns)",
    interpret_effect_size_r(abs(r)),
    ci[1], ci[2]
  )

  list(
    test_name      = sprintf("%s Correlation", tools::toTitleCase(method)),
    x_var          = x_var,
    y_var          = y_var,
    r              = r,
    p_value        = ct$p.value,
    conf_int       = ci,
    df             = unname(ct$parameter),
    effect_label   = interpret_effect_size_r(abs(r)),
    significant    = sig,
    interpretation = interp
  )
}


#' Perform chi-square test of independence
#'
#' @param data A data.frame
#' @param row_var Name of first categorical variable
#' @param col_var Name of second categorical variable
#' @param alpha Significance level (default 0.05)
#' @return List with chi2, df, p_value, cramers_v, significant, interpretation
#' @examples
#' df <- data.frame(sex = sample(c("M","F"), 100, TRUE),
#'                  pass = sample(c("Y","N"), 100, TRUE))
#' run_chi_square(df, "sex", "pass")
run_chi_square <- function(data, row_var, col_var, alpha = 0.05) {
  tbl <- table(data[[row_var]], data[[col_var]])
  ct  <- chisq.test(tbl)

  # Cramér's V
  n  <- sum(tbl)
  k  <- min(nrow(tbl), ncol(tbl)) - 1
  cv <- if (k > 0) sqrt(ct$statistic / (n * k)) else NA_real_

  sig <- ct$p.value < alpha

  interp <- sprintf(
    "Chi-square test: X2(%d, n=%d)=%.3f, p=%.4f%s. Cramér's V=%.3f (%s association).",
    ct$parameter, n,
    unname(ct$statistic),
    ct$p.value,
    if (sig) " *" else " (ns)",
    cv,
    interpret_effect_size_v(cv)
  )

  list(
    test_name      = "Chi-square Test of Independence",
    chi2           = unname(ct$statistic),
    df             = as.integer(ct$parameter),
    p_value        = ct$p.value,
    cramers_v      = unname(cv),
    effect_label   = interpret_effect_size_v(cv),
    contingency_table = tbl,
    significant    = sig,
    interpretation = interp
  )
}


#' Perform linear regression
#'
#' @param data A data.frame
#' @param outcome_var Outcome variable name
#' @param predictor_vars Character vector of predictor variable names
#' @param alpha Significance level (default 0.05)
#' @return List with coefficients, r_squared, F_stat, p_value,
#'   interpretation, fit object
#' @examples
#' run_regression(mtcars, "mpg", c("wt", "hp"))
run_regression <- function(data, outcome_var, predictor_vars, alpha = 0.05) {
  formula_str <- paste(outcome_var, "~", paste(predictor_vars, collapse = " + "))
  fit  <- lm(as.formula(formula_str), data = data)
  sm   <- summary(fit)

  r2   <- sm$r.squared
  adj_r2 <- sm$adj.r.squared
  fstat <- sm$fstatistic
  p_val <- pf(fstat[1], fstat[2], fstat[3], lower.tail = FALSE)
  sig   <- p_val < alpha

  coef_df <- as.data.frame(sm$coefficients)
  names(coef_df) <- c("estimate", "std_error", "t_value", "p_value")
  coef_df$variable <- rownames(coef_df)

  interp <- sprintf(
    "Linear regression: R2=%.3f (adj. R2=%.3f), F(%d,%d)=%.3f, p=%.4f%s. Model %s.",
    r2, adj_r2,
    as.integer(fstat[2]), as.integer(fstat[3]),
    fstat[1],
    p_val,
    if (sig) " *" else " (ns)",
    if (sig) "is statistically significant" else "does not reach significance"
  )

  list(
    test_name      = "Linear Regression",
    outcome_var    = outcome_var,
    predictor_vars = predictor_vars,
    r_squared      = r2,
    adj_r_squared  = adj_r2,
    F_stat         = fstat[1],
    df1            = as.integer(fstat[2]),
    df2            = as.integer(fstat[3]),
    p_value        = p_val,
    coefficients   = coef_df,
    significant    = sig,
    interpretation = interp,
    fit            = fit
  )
}


# ── Effect Size Helpers ───────────────────────────────────────────────────────

#' Interpret Cohen's d effect size
interpret_effect_size_d <- function(d) {
  if (is.na(d)) return("unknown")
  if (d < 0.2) "negligible"
  else if (d < 0.5) "small"
  else if (d < 0.8) "medium"
  else "large"
}

#' Interpret eta-squared effect size
interpret_effect_size_eta2 <- function(eta2) {
  if (is.na(eta2)) return("unknown")
  if (eta2 < 0.01) "negligible"
  else if (eta2 < 0.06) "small"
  else if (eta2 < 0.14) "medium"
  else "large"
}

#' Interpret Pearson r effect size
interpret_effect_size_r <- function(r) {
  if (is.na(r)) return("unknown")
  r_abs <- abs(r)
  if (r_abs < 0.1) "negligible"
  else if (r_abs < 0.3) "small"
  else if (r_abs < 0.5) "medium"
  else "large"
}

#' Interpret Cramér's V effect size
interpret_effect_size_v <- function(v) {
  if (is.na(v)) return("unknown")
  if (v < 0.1) "negligible"
  else if (v < 0.3) "small"
  else if (v < 0.5) "medium"
  else "large"
}


# ── Orchestrator ──────────────────────────────────────────────────────────────

#' Run the complete three-phase analysis workflow
#'
#' This is the main entry point. It:
#'   1. Validates inputs
#'   2. Runs descriptive analysis
#'   3. Checks statistical assumptions
#'   4. Performs the appropriate hypothesis test
#'   5. Returns a comprehensive results object
#'
#' @param query Character user query
#' @param data A data.frame
#' @param analysis_type One of "t_test", "anova", "correlation",
#'   "regression", "chi_square", "descriptive"
#' @param outcome_var Name of outcome variable
#' @param group_var Name of grouping variable (optional)
#' @param predictor_vars Character vector of predictor names (optional)
#' @param numeric_vars Character vector of numeric variable names for
#'   descriptive phase (optional; inferred if NULL)
#' @param categorical_vars Character vector of categorical variable names
#'   (optional; inferred if NULL)
#' @param alpha Significance level (default 0.05)
#' @return List with phases: validation, descriptive, assumptions, test,
#'   full_report (character)
#' @examples
#' df <- data.frame(score = c(rnorm(30, 75, 8), rnorm(30, 72, 9)),
#'                  sex   = rep(c("F", "M"), each = 30))
#' run_analysis_workflow(
#'   query         = "Compare scores between male and female students",
#'   data          = df,
#'   analysis_type = "t_test",
#'   outcome_var   = "score",
#'   group_var     = "sex"
#' )
run_analysis_workflow <- function(query, data,
                                   analysis_type  = "descriptive",
                                   outcome_var    = NULL,
                                   group_var      = NULL,
                                   predictor_vars = NULL,
                                   numeric_vars   = NULL,
                                   categorical_vars = NULL,
                                   alpha          = 0.05) {
  # ── Auto-infer variable types if not provided ──────────────────────────────
  if (is.data.frame(data)) {
    all_types <- vapply(data, function(x) {
      if (is.numeric(x) || is.integer(x)) "numeric" else "categorical"
    }, character(1))

    if (is.null(numeric_vars))
      numeric_vars <- names(all_types)[all_types == "numeric"]
    if (is.null(categorical_vars))
      categorical_vars <- names(all_types)[all_types == "categorical"]
  }

  required <- unique(c(outcome_var, group_var, predictor_vars))
  required <- required[!is.null(required)]

  # ── Phase 0: Input Validation ─────────────────────────────────────────────
  if (!exists("validate_inputs", mode = "function")) {
    stop("validate_inputs() not found. Source inputValidation.R first.")
  }
  validation <- validate_inputs(
    query         = query,
    data          = data,
    analysis_type = analysis_type,
    required_vars = if (length(required) > 0) required else NULL,
    group_var     = group_var
  )

  if (!validation$valid) {
    return(list(
      validation   = validation,
      descriptive  = NULL,
      assumptions  = NULL,
      test         = NULL,
      full_report  = paste(
        validation$report,
        "\n\n⛔ Analysis aborted due to validation errors.",
        sep = ""
      )
    ))
  }

  # ── Phase 1: Descriptive ──────────────────────────────────────────────────
  descriptive <- run_descriptive_phase(
    data             = data,
    numeric_vars     = numeric_vars,
    categorical_vars = categorical_vars
  )

  # ── Phase 2: Assumptions ─────────────────────────────────────────────────
  assumptions <- NULL
  if (!is.null(outcome_var) && analysis_type != "descriptive") {
    assumptions <- run_assumption_phase(
      data           = data,
      analysis_type  = analysis_type,
      outcome_var    = outcome_var,
      group_var      = group_var,
      predictor_vars = predictor_vars,
      alpha          = alpha
    )
  }

  # ── Phase 3: Hypothesis Test ──────────────────────────────────────────────
  test_result <- NULL
  if (!is.null(outcome_var) && analysis_type != "descriptive") {
    test_result <- tryCatch({
      switch(analysis_type,
        t_test     = run_t_test(data, outcome_var, group_var,
                                equal_variances = isTRUE(assumptions$met["homogeneity"]),
                                alpha = alpha),
        anova      = run_anova(data, outcome_var, group_var, alpha),
        correlation = run_correlation(data, outcome_var,
                                      predictor_vars[1], alpha = alpha),
        regression = run_regression(data, outcome_var, predictor_vars, alpha),
        chi_square = run_chi_square(data, outcome_var, group_var, alpha),
        NULL
      )
    }, error = function(e) {
      list(error = conditionMessage(e), interpretation = paste("Test failed:", conditionMessage(e)))
    })
  }

  # ── Compile Full Report ───────────────────────────────────────────────────
  report_parts <- c(
    sprintf("Query: \"%s\"\n", query),
    validation$report,
    "",
    descriptive$report
  )

  if (!is.null(assumptions)) {
    report_parts <- c(report_parts, "", assumptions$report)
  }

  if (!is.null(test_result)) {
    if (!is.null(test_result$error)) {
      report_parts <- c(report_parts, "", "=== STATISTICAL TEST ===",
                        paste("Error:", test_result$error))
    } else {
      report_parts <- c(report_parts, "", "=== STATISTICAL TEST ===",
                        test_result$interpretation)
      if (!is.null(assumptions) && length(assumptions$violated) > 0) {
        report_parts <- c(report_parts,
          sprintf("\n⚠ Note: The following assumptions were violated: %s",
                  paste(assumptions$violated, collapse = ", ")),
          "  Consider non-parametric alternatives for more robust inference."
        )
      }
    }
  }

  list(
    validation  = validation,
    descriptive = descriptive,
    assumptions = assumptions,
    test        = test_result,
    full_report = paste(report_parts, collapse = "\n")
  )
}
