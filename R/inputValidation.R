#' Input Validation Framework for Jamovi LLM Assistant
#'
#' Comprehensive validation of user queries, data structure, variable types,
#' missing values, sample size, and data quality issues before analysis.

# ── Query Validation ───────────────────────────────────────────────────────────

#' Validate a user analysis query for clarity and specificity
#'
#' @param query Character string containing the user's analysis request
#' @return List with fields: valid (logical), issues (character vector),
#'   warnings (character vector)
#' @examples
#' validate_query("Compare test scores between male and female students")
#' validate_query("")
validate_query <- function(query) {
  issues   <- character(0)
  warnings <- character(0)

  if (!is.character(query) || length(query) != 1) {
    issues <- c(issues, "Query must be a single character string.")
    return(list(valid = FALSE, issues = issues, warnings = warnings))
  }

  trimmed <- trimws(query)

  if (nchar(trimmed) == 0) {
    issues <- c(issues, "Query cannot be empty.")
    return(list(valid = FALSE, issues = issues, warnings = warnings))
  }

  if (nchar(trimmed) < 10) {
    warnings <- c(warnings,
      "Query is very short. Consider providing more detail about the analysis.")
  }

  if (nchar(trimmed) > 2000) {
    warnings <- c(warnings,
      "Query is very long. Consider simplifying to improve LLM accuracy.")
  }

  word_count <- length(strsplit(trimmed, "\\s+")[[1]])
  if (word_count < 3) {
    warnings <- c(warnings,
      "Query appears too brief. Specify variables, groups, or analysis type.")
  }

  list(valid = length(issues) == 0, issues = issues, warnings = warnings)
}


# ── Data Structure Validation ──────────────────────────────────────────────────

#' Validate overall data structure (dimensions and types)
#'
#' @param data A data.frame or similar tabular object
#' @param min_rows Minimum acceptable number of rows (default 5)
#' @param min_cols Minimum acceptable number of columns (default 1)
#' @return List with fields: valid (logical), issues (character vector),
#'   info (list of structure metadata), warnings (character vector)
#' @examples
#' validate_data_structure(mtcars)
validate_data_structure <- function(data, min_rows = 5, min_cols = 1) {
  issues   <- character(0)
  warnings <- character(0)

  if (is.null(data)) {
    issues <- c(issues, "Data is NULL.")
    return(list(valid = FALSE, issues = issues, info = list(), warnings = warnings))
  }

  if (!is.data.frame(data)) {
    issues <- c(issues, "Data must be a data.frame.")
    return(list(valid = FALSE, issues = issues, info = list(), warnings = warnings))
  }

  n_rows <- nrow(data)
  n_cols <- ncol(data)

  if (n_rows == 0) {
    issues <- c(issues, "Data has no rows.")
  } else if (n_rows < min_rows) {
    issues <- c(issues,
      sprintf("Data has only %d row(s); minimum required is %d.", n_rows, min_rows))
  }

  if (n_cols == 0) {
    issues <- c(issues, "Data has no columns.")
  } else if (n_cols < min_cols) {
    issues <- c(issues,
      sprintf("Data has only %d column(s); minimum required is %d.", n_cols, min_cols))
  }

  if (n_rows > 0 && n_cols > 0) {
    if (n_rows < 30) {
      warnings <- c(warnings,
        sprintf("Small dataset (%d rows). Some analyses may lack statistical power.", n_rows))
    }
    if (n_cols > 100) {
      warnings <- c(warnings,
        "Large number of columns detected. Consider selecting relevant variables.")
    }
  }

  col_types <- vapply(data, function(x) class(x)[1], character(1))

  info <- list(
    n_rows    = n_rows,
    n_cols    = n_cols,
    col_names = names(data),
    col_types = col_types
  )

  list(valid = length(issues) == 0, issues = issues, info = info, warnings = warnings)
}


# ── Variable Existence & Type Validation ───────────────────────────────────────

#' Check that required variables exist in the data and have expected types
#'
#' @param data A data.frame
#' @param required_vars Character vector of required variable names
#' @param expected_types Named character vector mapping variable names to
#'   expected types: "numeric", "factor", "character", or "any"
#' @return List with fields: valid (logical), issues (character vector),
#'   warnings (character vector)
#' @examples
#' validate_variables(mtcars, c("mpg", "cyl"),
#'                    c(mpg = "numeric", cyl = "numeric"))
validate_variables <- function(data, required_vars, expected_types = NULL) {
  issues   <- character(0)
  warnings <- character(0)

  if (!is.data.frame(data)) {
    return(list(valid = FALSE,
                issues = "Data must be a data.frame.",
                warnings = warnings))
  }

  missing_vars <- setdiff(required_vars, names(data))
  if (length(missing_vars) > 0) {
    issues <- c(issues,
      paste("Required variable(s) not found in data:",
            paste(missing_vars, collapse = ", ")))
  }

  if (!is.null(expected_types)) {
    for (var in intersect(names(expected_types), names(data))) {
      expected <- expected_types[[var]]
      if (expected == "any") next
      actual <- class(data[[var]])[1]
      ok <- switch(expected,
        numeric   = is.numeric(data[[var]]),
        factor    = is.factor(data[[var]]),
        character = is.character(data[[var]]),
        FALSE
      )
      if (!ok) {
        issues <- c(issues,
          sprintf("Variable '%s' expected to be %s but is %s.",
                  var, expected, actual))
      }
    }
  }

  list(valid = length(issues) == 0, issues = issues, warnings = warnings)
}


# ── Missing Value Detection ────────────────────────────────────────────────────

#' Detect and summarise missing values in the data
#'
#' @param data A data.frame
#' @param threshold Proportion of missingness above which a variable triggers
#'   a warning (default 0.1 = 10 %)
#' @return List with fields: valid (logical), issues (character vector),
#'   missing_summary (data.frame), warnings (character vector)
#' @examples
#' df <- data.frame(x = c(1, NA, 3), y = c(NA, NA, 3))
#' detect_missing_values(df)
detect_missing_values <- function(data, threshold = 0.1) {
  issues   <- character(0)
  warnings <- character(0)

  if (!is.data.frame(data) || nrow(data) == 0) {
    return(list(
      valid           = FALSE,
      issues          = "Data must be a non-empty data.frame.",
      missing_summary = data.frame(),
      warnings        = warnings
    ))
  }

  n <- nrow(data)
  miss_count <- vapply(data, function(x) sum(is.na(x)), integer(1))
  miss_pct   <- miss_count / n

  summary_df <- data.frame(
    variable        = names(data),
    missing_count   = miss_count,
    missing_percent = round(miss_pct * 100, 2),
    stringsAsFactors = FALSE
  )

  high_miss <- summary_df[summary_df$missing_percent > threshold * 100, , drop = FALSE]
  if (nrow(high_miss) > 0) {
    for (i in seq_len(nrow(high_miss))) {
      warnings <- c(warnings,
        sprintf("Variable '%s' has %.1f%% missing values.",
                high_miss$variable[i], high_miss$missing_percent[i]))
    }
  }

  all_missing <- summary_df[summary_df$missing_count == n, , drop = FALSE]
  if (nrow(all_missing) > 0) {
    issues <- c(issues,
      paste("Variable(s) completely missing:",
            paste(all_missing$variable, collapse = ", ")))
  }

  list(
    valid           = length(issues) == 0,
    issues          = issues,
    missing_summary = summary_df,
    warnings        = warnings
  )
}


# ── Numeric vs Categorical Detection ──────────────────────────────────────────

#' Classify columns as numeric, categorical, or other
#'
#' @param data A data.frame
#' @return List with fields: numeric_vars (character), categorical_vars
#'   (character), other_vars (character), type_map (named character vector)
#' @examples
#' classify_variable_types(iris)
classify_variable_types <- function(data) {
  if (!is.data.frame(data)) {
    stop("Data must be a data.frame.")
  }

  type_map <- vapply(data, function(x) {
    if (is.numeric(x) || is.integer(x)) {
      "numeric"
    } else if (is.factor(x) || is.logical(x) || is.character(x)) {
      "categorical"
    } else {
      "other"
    }
  }, character(1))

  list(
    numeric_vars     = names(type_map)[type_map == "numeric"],
    categorical_vars = names(type_map)[type_map == "categorical"],
    other_vars       = names(type_map)[type_map == "other"],
    type_map         = type_map
  )
}


# ── Sample Size Validation ─────────────────────────────────────────────────────

#' Validate whether sample size is adequate for the requested analysis type
#'
#' @param data A data.frame
#' @param analysis_type Character. One of "t_test", "anova", "correlation",
#'   "regression", "chi_square", "descriptive"
#' @param group_var Optional character: column name of grouping variable
#' @return List with fields: adequate (logical), n (integer),
#'   min_required (integer), issues (character vector),
#'   warnings (character vector)
#' @examples
#' validate_sample_size(mtcars, "t_test", group_var = "am")
validate_sample_size <- function(data, analysis_type, group_var = NULL) {
  issues   <- character(0)
  warnings <- character(0)

  if (!is.data.frame(data)) {
    return(list(adequate = FALSE, n = 0L, min_required = NA_integer_,
                issues = "Data must be a data.frame.", warnings = warnings))
  }

  n <- nrow(data)

  min_required <- switch(analysis_type,
    t_test      = 10L,
    anova       = 20L,
    correlation = 10L,
    regression  = 20L,
    chi_square  = 20L,
    descriptive =  5L,
    10L          # default
  )

  if (n < min_required) {
    issues <- c(issues,
      sprintf("Sample size (%d) is below the minimum recommended (%d) for %s.",
              n, min_required, analysis_type))
  } else if (n < min_required * 2) {
    warnings <- c(warnings,
      sprintf("Sample size (%d) is marginal for %s. Results may lack power.",
              n, analysis_type))
  }

  # Per-group checks for t_test / anova
  if (!is.null(group_var) && group_var %in% names(data)) {
    grp_counts <- table(data[[group_var]])
    small_groups <- grp_counts[grp_counts < 5]
    if (length(small_groups) > 0) {
      warnings <- c(warnings,
        paste("Small group(s) detected (n < 5):",
              paste(names(small_groups), collapse = ", ")))
    }
  }

  list(
    adequate     = length(issues) == 0,
    n            = as.integer(n),
    min_required = min_required,
    issues       = issues,
    warnings     = warnings
  )
}


# ── Outlier Detection ─────────────────────────────────────────────────────────

#' Detect outliers in numeric columns using the IQR method
#'
#' @param data A data.frame
#' @param threshold Multiplier for the IQR fence (default 1.5)
#' @return List with fields: outlier_summary (data.frame), warnings
#'   (character vector)
#' @examples
#' detect_outliers(mtcars)
detect_outliers <- function(data, threshold = 1.5) {
  warnings <- character(0)

  if (!is.data.frame(data)) {
    return(list(outlier_summary = data.frame(), warnings = "Data must be a data.frame."))
  }

  num_cols <- names(data)[vapply(data, is.numeric, logical(1))]

  if (length(num_cols) == 0) {
    return(list(
      outlier_summary = data.frame(),
      warnings        = "No numeric columns found for outlier detection."
    ))
  }

  results <- lapply(num_cols, function(col) {
    x   <- data[[col]]
    x   <- x[!is.na(x)]
    q1  <- quantile(x, 0.25)
    q3  <- quantile(x, 0.75)
    iqr <- q3 - q1
    lo  <- q1 - threshold * iqr
    hi  <- q3 + threshold * iqr
    n_out <- sum(x < lo | x > hi)
    data.frame(
      variable       = col,
      n_outliers     = as.integer(n_out),
      lower_fence    = round(lo, 4),
      upper_fence    = round(hi, 4),
      stringsAsFactors = FALSE
    )
  })

  summary_df <- do.call(rbind, results)

  vars_with_outliers <- summary_df[summary_df$n_outliers > 0, "variable"]
  if (length(vars_with_outliers) > 0) {
    warnings <- c(warnings,
      paste("Outliers detected in:", paste(vars_with_outliers, collapse = ", "),
            "- consider investigation before analysis."))
  }

  list(outlier_summary = summary_df, warnings = warnings)
}


# ── Full Input Validation Pipeline ────────────────────────────────────────────

#' Run all input validation checks and return a consolidated report
#'
#' @param query Character user query
#' @param data A data.frame
#' @param analysis_type Character analysis type (for sample size check)
#' @param required_vars Character vector of required variable names
#' @param group_var Optional grouping variable name
#' @return List with fields: valid (logical), report (character),
#'   details (list of per-check results)
#' @examples
#' validate_inputs("Compare mpg by cylinder count", mtcars,
#'                 analysis_type = "anova",
#'                 required_vars = c("mpg", "cyl"),
#'                 group_var = "cyl")
validate_inputs <- function(query, data, analysis_type = "descriptive",
                            required_vars = NULL, group_var = NULL) {
  details <- list()

  details$query     <- validate_query(query)
  details$structure <- validate_data_structure(data)
  details$missing   <- detect_missing_values(data)
  details$sample    <- validate_sample_size(data, analysis_type, group_var)
  details$outliers  <- detect_outliers(data)
  details$types     <- classify_variable_types(data)

  if (!is.null(required_vars)) {
    details$variables <- validate_variables(data, required_vars)
  }

  all_issues <- unlist(lapply(details, function(x) x$issues))
  all_warnings <- unlist(lapply(details, function(x) x$warnings))

  valid <- length(all_issues) == 0

  lines <- c("=== INPUT VALIDATION REPORT ===")

  if (valid) {
    lines <- c(lines, "✓ All validation checks passed.")
  } else {
    lines <- c(lines, "✗ Validation issues found:")
    lines <- c(lines, paste("  •", all_issues))
  }

  if (length(all_warnings) > 0) {
    lines <- c(lines, "", "Warnings:")
    lines <- c(lines, paste("  ⚠", all_warnings))
  }

  list(
    valid   = valid,
    report  = paste(lines, collapse = "\n"),
    details = details
  )
}
