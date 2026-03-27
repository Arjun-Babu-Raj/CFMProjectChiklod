#' Assumption Checking System for Jamovi LLM Assistant
#'
#' Comprehensive statistical assumption tests including normality,
#' homogeneity of variance, independence, linearity, multicollinearity,
#' and sample size adequacy. Generates detailed assumption violation reports.

# ── Normality Tests ────────────────────────────────────────────────────────────

#' Test normality using Shapiro-Wilk (and optionally KS) test
#'
#' @param x Numeric vector to test
#' @param var_name Optional label for display (default "variable")
#' @param alpha Significance level (default 0.05)
#' @return List with fields: test (character), statistic (numeric),
#'   p_value (numeric), normal (logical), interpretation (character)
#' @examples
#' test_normality(rnorm(50))
#' test_normality(rexp(50))
test_normality <- function(x, var_name = "variable", alpha = 0.05) {
  x_clean <- x[!is.na(x)]
  n <- length(x_clean)

  if (n < 3) {
    return(list(
      test           = "Shapiro-Wilk",
      statistic      = NA_real_,
      p_value        = NA_real_,
      normal         = NA,
      interpretation = sprintf("'%s': insufficient data (n=%d) for normality test.", var_name, n)
    ))
  }

  # Shapiro-Wilk is preferred for n <= 5000
  if (n <= 5000) {
    sw <- tryCatch(shapiro.test(x_clean),
                   error = function(e) NULL)
    if (!is.null(sw)) {
      is_normal <- sw$p.value > alpha
      interp <- sprintf(
        "'%s': Shapiro-Wilk W=%.4f, p=%.4f – %s",
        var_name, sw$statistic, sw$p.value,
        if (is_normal) "normally distributed (p > alpha)" else "NOT normally distributed (p <= alpha)"
      )
      return(list(
        test           = "Shapiro-Wilk",
        statistic      = unname(sw$statistic),
        p_value        = sw$p.value,
        normal         = is_normal,
        interpretation = interp
      ))
    }
  }

  # Fallback to Kolmogorov-Smirnov for large samples
  ks <- tryCatch(
    ks.test(x_clean, "pnorm", mean = mean(x_clean), sd = sd(x_clean)),
    error = function(e) NULL
  )
  if (!is.null(ks)) {
    is_normal <- ks$p.value > alpha
    interp <- sprintf(
      "'%s': Kolmogorov-Smirnov D=%.4f, p=%.4f – %s",
      var_name, ks$statistic, ks$p.value,
      if (is_normal) "normally distributed (p > alpha)" else "NOT normally distributed (p <= alpha)"
    )
    return(list(
      test           = "Kolmogorov-Smirnov",
      statistic      = unname(ks$statistic),
      p_value        = ks$p.value,
      normal         = is_normal,
      interpretation = interp
    ))
  }

  list(
    test           = "None",
    statistic      = NA_real_,
    p_value        = NA_real_,
    normal         = NA,
    interpretation = sprintf("'%s': normality test could not be performed.", var_name)
  )
}


#' Test normality for multiple groups of a numeric variable
#'
#' @param data A data.frame
#' @param outcome_var Name of the numeric outcome variable
#' @param group_var Name of the grouping variable
#' @param alpha Significance level (default 0.05)
#' @return List with fields: results (list of per-group test results),
#'   all_normal (logical), summary (character)
#' @examples
#' test_normality_by_group(iris, "Sepal.Length", "Species")
test_normality_by_group <- function(data, outcome_var, group_var, alpha = 0.05) {
  if (!outcome_var %in% names(data))
    stop(sprintf("Outcome variable '%s' not found in data.", outcome_var))
  if (!group_var %in% names(data))
    stop(sprintf("Group variable '%s' not found in data.", group_var))

  groups  <- unique(data[[group_var]])
  results <- lapply(groups, function(g) {
    sub <- data[[outcome_var]][data[[group_var]] == g]
    test_normality(sub, var_name = paste0(outcome_var, "[", g, "]"), alpha = alpha)
  })
  names(results) <- as.character(groups)

  all_normal <- all(vapply(results, function(r) isTRUE(r$normal), logical(1)))

  summary_lines <- vapply(results, function(r) r$interpretation, character(1))
  summary <- paste(summary_lines, collapse = "\n")

  list(results = results, all_normal = all_normal, summary = summary)
}


# ── Homogeneity of Variance ───────────────────────────────────────────────────

#' Levene's test for homogeneity of variance (centre = median)
#'
#' @param data A data.frame
#' @param outcome_var Name of numeric outcome variable
#' @param group_var Name of grouping variable
#' @param alpha Significance level (default 0.05)
#' @return List with fields: test (character), statistic (numeric),
#'   df1 (integer), df2 (integer), p_value (numeric),
#'   equal_variances (logical), interpretation (character)
#' @examples
#' test_homogeneity(iris, "Sepal.Length", "Species")
test_homogeneity <- function(data, outcome_var, group_var, alpha = 0.05) {
  if (!outcome_var %in% names(data))
    stop(sprintf("'%s' not found in data.", outcome_var))
  if (!group_var %in% names(data))
    stop(sprintf("'%s' not found in data.", group_var))

  y <- data[[outcome_var]]
  g <- as.factor(data[[group_var]])

  complete <- !is.na(y) & !is.na(g)
  y <- y[complete]
  g <- g[complete]

  groups <- levels(g)
  k <- length(groups)
  n <- length(y)

  # Levene's test (median-based = Brown-Forsythe)
  group_medians <- tapply(y, g, median)
  z <- abs(y - group_medians[as.character(g)])

  z_bar_grand  <- mean(z)
  z_bar_groups <- tapply(z, g, mean)
  group_sizes  <- tabulate(g)

  ss_between <- sum(group_sizes * (z_bar_groups - z_bar_grand)^2)
  ss_within  <- sum((z - z_bar_groups[as.character(g)])^2)

  df1 <- k - 1L
  df2 <- n - k

  if (ss_within == 0 || df2 <= 0) {
    return(list(
      test            = "Levene",
      statistic       = NA_real_,
      df1             = df1,
      df2             = df2,
      p_value         = NA_real_,
      equal_variances = NA,
      interpretation  = "Levene's test could not be computed."
    ))
  }

  F_stat <- (ss_between / df1) / (ss_within / df2)
  p_val  <- pf(F_stat, df1, df2, lower.tail = FALSE)

  equal_var <- p_val > alpha
  interp <- sprintf(
    "Levene's test: F(%d,%d)=%.3f, p=%.4f – %s",
    df1, df2, F_stat, p_val,
    if (equal_var) "equal variances assumed (p > alpha)"
    else "unequal variances (p <= alpha); consider Welch's t-test"
  )

  list(
    test            = "Levene",
    statistic       = F_stat,
    df1             = as.integer(df1),
    df2             = as.integer(df2),
    p_value         = p_val,
    equal_variances = equal_var,
    interpretation  = interp
  )
}


#' Bartlett's test for homogeneity of variance
#'
#' @param data A data.frame
#' @param outcome_var Name of numeric outcome variable
#' @param group_var Name of grouping variable
#' @param alpha Significance level (default 0.05)
#' @return List with fields: test, statistic, df, p_value,
#'   equal_variances, interpretation
#' @examples
#' test_homogeneity_bartlett(iris, "Sepal.Length", "Species")
test_homogeneity_bartlett <- function(data, outcome_var, group_var, alpha = 0.05) {
  if (!outcome_var %in% names(data))
    stop(sprintf("'%s' not found in data.", outcome_var))
  if (!group_var %in% names(data))
    stop(sprintf("'%s' not found in data.", group_var))

  formula_obj <- as.formula(paste(outcome_var, "~", group_var))
  bt <- tryCatch(
    bartlett.test(formula_obj, data = data),
    error = function(e) NULL
  )

  if (is.null(bt)) {
    return(list(
      test            = "Bartlett",
      statistic       = NA_real_,
      df              = NA_integer_,
      p_value         = NA_real_,
      equal_variances = NA,
      interpretation  = "Bartlett's test could not be computed."
    ))
  }

  equal_var <- bt$p.value > alpha
  interp <- sprintf(
    "Bartlett's test: K2(%.0f)=%.3f, p=%.4f – %s",
    bt$parameter, bt$statistic, bt$p.value,
    if (equal_var) "equal variances assumed (p > alpha)"
    else "unequal variances (p <= alpha); data may not be normally distributed"
  )

  list(
    test            = "Bartlett",
    statistic       = unname(bt$statistic),
    df              = as.integer(bt$parameter),
    p_value         = bt$p.value,
    equal_variances = equal_var,
    interpretation  = interp
  )
}


# ── Independence / Autocorrelation ────────────────────────────────────────────

#' Durbin-Watson test for autocorrelation in regression residuals
#'
#' @param residuals Numeric vector of model residuals
#' @param alpha Significance level (default 0.05)
#' @return List with fields: test (character), statistic (numeric),
#'   independent (logical), interpretation (character)
#' @examples
#' m <- lm(mpg ~ wt, data = mtcars)
#' test_independence(residuals(m))
test_independence <- function(residuals, alpha = 0.05) {
  r <- residuals[!is.na(residuals)]
  n <- length(r)

  if (n < 3) {
    return(list(
      test           = "Durbin-Watson",
      statistic      = NA_real_,
      independent    = NA,
      interpretation = "Insufficient residuals for Durbin-Watson test."
    ))
  }

  dw <- sum(diff(r)^2) / sum(r^2)

  # DW ~ 2 indicates no autocorrelation; rough bounds [1.5, 2.5]
  independent <- dw >= 1.5 && dw <= 2.5
  interp <- sprintf(
    "Durbin-Watson statistic: DW=%.4f – %s",
    dw,
    if (independent) "no significant autocorrelation detected (DW near 2)"
    else if (dw < 1.5) "positive autocorrelation suspected (DW < 1.5)"
    else "negative autocorrelation suspected (DW > 2.5)"
  )

  list(
    test           = "Durbin-Watson",
    statistic      = dw,
    independent    = independent,
    interpretation = interp
  )
}


# ── Linearity Assessment ──────────────────────────────────────────────────────

#' Assess linearity between two numeric variables via correlation
#'
#' @param data A data.frame
#' @param x_var Name of predictor variable
#' @param y_var Name of outcome variable
#' @param alpha Significance level (default 0.05)
#' @return List with fields: pearson_r, spearman_r, p_value_pearson,
#'   linear (logical), interpretation (character)
#' @examples
#' assess_linearity(mtcars, "wt", "mpg")
assess_linearity <- function(data, x_var, y_var, alpha = 0.05) {
  if (!x_var %in% names(data)) stop(sprintf("'%s' not found.", x_var))
  if (!y_var %in% names(data)) stop(sprintf("'%s' not found.", y_var))

  complete <- complete.cases(data[, c(x_var, y_var)])
  x <- data[[x_var]][complete]
  y <- data[[y_var]][complete]

  if (length(x) < 4) {
    return(list(
      pearson_r        = NA_real_,
      spearman_r       = NA_real_,
      p_value_pearson  = NA_real_,
      linear           = NA,
      interpretation   = "Insufficient complete cases for linearity assessment."
    ))
  }

  pearson  <- tryCatch(cor.test(x, y, method = "pearson"),  error = function(e) NULL)
  spearman <- tryCatch(cor.test(x, y, method = "spearman"), error = function(e) NULL)

  r_p <- if (!is.null(pearson))  unname(pearson$estimate)  else NA_real_
  r_s <- if (!is.null(spearman)) unname(spearman$estimate) else NA_real_
  p_p <- if (!is.null(pearson))  pearson$p.value           else NA_real_

  # If Pearson and Spearman r are similar, relationship is likely linear
  linear <- !is.na(r_p) && !is.na(r_s) && abs(abs(r_p) - abs(r_s)) < 0.1

  interp <- sprintf(
    "Linearity (%s vs %s): Pearson r=%.3f (p=%.4f), Spearman r=%.3f – %s",
    x_var, y_var, r_p, p_p, r_s,
    if (isTRUE(linear)) "likely linear relationship"
    else "potential non-linearity; consider transformation or non-parametric test"
  )

  list(
    pearson_r       = r_p,
    spearman_r      = r_s,
    p_value_pearson = p_p,
    linear          = linear,
    interpretation  = interp
  )
}


# ── Multicollinearity (VIF) ───────────────────────────────────────────────────

#' Calculate Variance Inflation Factors for regression predictors
#'
#' VIF > 10 indicates severe multicollinearity; VIF > 5 is a common warning.
#'
#' @param data A data.frame
#' @param outcome_var Name of outcome variable
#' @param predictor_vars Character vector of predictor variable names
#' @param vif_threshold Threshold above which multicollinearity is flagged
#'   (default 5)
#' @return List with fields: vif_values (named numeric),
#'   multicollinear (logical), issues (character vector),
#'   interpretation (character)
#' @examples
#' check_multicollinearity(mtcars, "mpg", c("wt", "hp", "disp"))
check_multicollinearity <- function(data, outcome_var, predictor_vars,
                                    vif_threshold = 5) {
  issues <- character(0)

  for (v in c(outcome_var, predictor_vars)) {
    if (!v %in% names(data)) {
      issues <- c(issues, sprintf("Variable '%s' not found in data.", v))
    }
  }
  if (length(issues) > 0) {
    return(list(vif_values = numeric(0), multicollinear = NA,
                issues = issues, interpretation = paste(issues, collapse = "; ")))
  }

  if (length(predictor_vars) < 2) {
    return(list(
      vif_values     = c(setNames(1, predictor_vars)),
      multicollinear = FALSE,
      issues         = character(0),
      interpretation = "VIF not applicable with a single predictor."
    ))
  }

  formula_str <- paste(outcome_var, "~", paste(predictor_vars, collapse = " + "))
  fit <- tryCatch(
    lm(as.formula(formula_str), data = data),
    error = function(e) NULL
  )

  if (is.null(fit)) {
    return(list(vif_values = numeric(0), multicollinear = NA,
                issues = "Model could not be fitted for VIF calculation.",
                interpretation = "VIF calculation failed."))
  }

  # Compute VIF manually as diag((X'X)^{-1}) * RSS/(n-p) / var(predictor)
  X <- model.matrix(fit)[, -1, drop = FALSE]  # drop intercept
  vif_vals <- tryCatch({
    XtX_inv <- solve(t(X) %*% X)
    r2s <- vapply(seq_len(ncol(X)), function(j) {
      summary(lm(X[, j] ~ X[, -j]))$r.squared
    }, numeric(1))
    1 / (1 - r2s)
  }, error = function(e) rep(NA_real_, ncol(X)))

  names(vif_vals) <- colnames(X)
  high_vif <- names(vif_vals)[!is.na(vif_vals) & vif_vals > vif_threshold]

  multicollinear <- length(high_vif) > 0

  if (multicollinear) {
    issues <- c(issues,
      paste("High VIF (>", vif_threshold, ") detected for:",
            paste(high_vif, collapse = ", "),
            "– consider removing correlated predictors."))
  }

  interp_lines <- paste(names(vif_vals), round(vif_vals, 3), sep = " = VIF ")
  interp <- paste(
    c("VIF values:", interp_lines,
      if (multicollinear) "⚠ Multicollinearity detected." else "✓ No severe multicollinearity."),
    collapse = "\n  "
  )

  list(
    vif_values     = vif_vals,
    multicollinear = multicollinear,
    issues         = issues,
    interpretation = interp
  )
}


# ── Assumption Violation Report ───────────────────────────────────────────────

#' Generate a comprehensive assumption checking report for common analyses
#'
#' @param data A data.frame
#' @param analysis_type One of "t_test", "anova", "correlation", "regression"
#' @param outcome_var Name of numeric outcome variable
#' @param group_var Name of grouping variable (for t_test / anova)
#' @param predictor_vars Character vector of predictors (for regression)
#' @param alpha Significance level (default 0.05)
#' @return List with fields: met (logical vector of assumption results),
#'   violated (character vector of violated assumption names),
#'   report (character), details (list)
#' @examples
#' check_assumptions(iris, "t_test", "Sepal.Length", group_var = "Species")
check_assumptions <- function(data, analysis_type, outcome_var,
                               group_var = NULL, predictor_vars = NULL,
                               alpha = 0.05) {
  details  <- list()
  met      <- logical(0)
  violated <- character(0)

  lines <- c("=== ASSUMPTION CHECKING ===")

  # 1. Normality
  if (!is.null(group_var)) {
    norm_res <- test_normality_by_group(data, outcome_var, group_var, alpha)
    details$normality <- norm_res
    if (is.na(norm_res$all_normal)) {
      lines <- c(lines, "? Normality: could not be determined")
    } else if (norm_res$all_normal) {
      lines <- c(lines, "✓ Normality: All groups normally distributed (p > alpha)")
      met   <- c(met, normality = TRUE)
    } else {
      lines <- c(lines, "✗ Normality: Normality violated in one or more groups")
      met      <- c(met, normality = FALSE)
      violated <- c(violated, "normality")
    }
  } else {
    norm_res <- test_normality(data[[outcome_var]], outcome_var, alpha)
    details$normality <- norm_res
    if (is.na(norm_res$normal)) {
      lines <- c(lines, "? Normality: could not be determined")
    } else if (norm_res$normal) {
      lines <- c(lines, "✓ Normality: Variable is normally distributed (p > alpha)")
      met   <- c(met, normality = TRUE)
    } else {
      lines <- c(lines, "✗ Normality: Normality violated")
      met      <- c(met, normality = FALSE)
      violated <- c(violated, "normality")
    }
  }

  # 2. Homogeneity of variance (t_test / anova)
  if (analysis_type %in% c("t_test", "anova") && !is.null(group_var)) {
    hom_res <- test_homogeneity(data, outcome_var, group_var, alpha)
    details$homogeneity <- hom_res
    if (is.na(hom_res$equal_variances)) {
      lines <- c(lines, "? Homogeneity of Variance: could not be determined")
    } else if (hom_res$equal_variances) {
      lines <- c(lines, sprintf("✓ Homogeneity: Equal variances confirmed (Levene: p=%.4f)",
                                hom_res$p_value))
      met   <- c(met, homogeneity = TRUE)
    } else {
      lines <- c(lines, sprintf("✗ Homogeneity: Unequal variances (Levene: p=%.4f) – use Welch's correction",
                                hom_res$p_value))
      met      <- c(met, homogeneity = FALSE)
      violated <- c(violated, "homogeneity")
    }
  }

  # 3. Independence (residuals check for regression)
  if (analysis_type == "regression" && !is.null(predictor_vars)) {
    formula_str <- paste(outcome_var, "~", paste(predictor_vars, collapse = " + "))
    fit <- tryCatch(lm(as.formula(formula_str), data = data), error = function(e) NULL)
    if (!is.null(fit)) {
      indep_res <- test_independence(residuals(fit), alpha)
      details$independence <- indep_res
      if (is.na(indep_res$independent)) {
        lines <- c(lines, "? Independence: could not be determined")
      } else if (indep_res$independent) {
        lines <- c(lines, sprintf("✓ Independence: No autocorrelation (DW=%.3f)",
                                  indep_res$statistic))
        met   <- c(met, independence = TRUE)
      } else {
        lines <- c(lines, sprintf("✗ Independence: Autocorrelation detected (DW=%.3f)",
                                  indep_res$statistic))
        met      <- c(met, independence = FALSE)
        violated <- c(violated, "independence")
      }
    }
  }

  # 4. Linearity (regression / correlation)
  if (analysis_type %in% c("regression", "correlation") && !is.null(predictor_vars)) {
    lin_results <- lapply(predictor_vars, function(pv) {
      if (pv %in% names(data)) assess_linearity(data, pv, outcome_var, alpha)
      else NULL
    })
    lin_results <- Filter(Negate(is.null), lin_results)
    details$linearity <- lin_results

    all_linear <- all(vapply(lin_results, function(r) isTRUE(r$linear), logical(1)))
    if (all_linear) {
      lines <- c(lines, "✓ Linearity: Linear relationships confirmed")
      met   <- c(met, linearity = TRUE)
    } else {
      lines <- c(lines, "✗ Linearity: Potential non-linearity detected")
      met      <- c(met, linearity = FALSE)
      violated <- c(violated, "linearity")
    }
  }

  # 5. Multicollinearity (regression only)
  if (analysis_type == "regression" && !is.null(predictor_vars) &&
      length(predictor_vars) >= 2) {
    vif_res <- check_multicollinearity(data, outcome_var, predictor_vars)
    details$multicollinearity <- vif_res
    if (is.na(vif_res$multicollinear)) {
      lines <- c(lines, "? Multicollinearity: could not be determined")
    } else if (!vif_res$multicollinear) {
      lines <- c(lines, "✓ Multicollinearity: No severe multicollinearity detected")
      met   <- c(met, multicollinearity = FALSE)
    } else {
      lines <- c(lines, "✗ Multicollinearity: High VIF detected")
      met      <- c(met, multicollinearity = TRUE)
      violated <- c(violated, "multicollinearity")
    }
  }

  # Summary
  if (length(violated) == 0) {
    lines <- c(lines, "", "✓ All checked assumptions are met.")
  } else {
    lines <- c(lines, "",
               paste("⚠ Assumptions violated:", paste(violated, collapse = ", ")))
    lines <- c(lines, "  → Consider non-parametric alternatives or data transformations.")
  }

  list(
    met      = met,
    violated = violated,
    report   = paste(lines, collapse = "\n"),
    details  = details
  )
}
