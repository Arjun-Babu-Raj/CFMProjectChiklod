# Tests for analysisWorkflow.R
# Run with: source("tests/test-analysisWorkflow.R")
# Requires: R/inputValidation.R, R/assumptionChecker.R, R/analysisWorkflow.R

base_dir <- dirname(sys.frame(1)$ofile)
source(file.path(base_dir, "..", "R", "inputValidation.R"),  local = FALSE)
source(file.path(base_dir, "..", "R", "assumptionChecker.R"), local = FALSE)
source(file.path(base_dir, "..", "R", "analysisWorkflow.R"),  local = FALSE)

# ── Simple test harness ────────────────────────────────────────────────────────

.test_pass <- 0L
.test_fail <- 0L

expect_true <- function(cond, msg = "") {
  if (isTRUE(cond)) {
    .test_pass <<- .test_pass + 1L
    cat(sprintf("  PASS: %s\n", msg))
  } else {
    .test_fail <<- .test_fail + 1L
    cat(sprintf("  FAIL: %s\n", msg))
  }
}

expect_false <- function(cond, msg = "") expect_true(!cond, msg)

run_test <- function(name, expr) {
  cat(sprintf("\n[TEST] %s\n", name))
  tryCatch(expr, error = function(e) {
    .test_fail <<- .test_fail + 1L
    cat(sprintf("  ERROR: %s\n", conditionMessage(e)))
  })
}

set.seed(42)

# ── describe_variable ─────────────────────────────────────────────────────────

run_test("describe_variable – basic stats", {
  r <- describe_variable(mtcars$mpg, "mpg")
  expect_true(r$n == 32L,               "n == 32")
  expect_true(r$n_missing == 0L,        "no missing")
  expect_true(r$mean > 0,               "mean > 0")
  expect_true(r$sd > 0,                 "sd > 0")
  expect_true(r$q1 <= r$median,         "q1 <= median")
  expect_true(r$median <= r$q3,         "median <= q3")
  expect_true(r$iqr >= 0,               "iqr >= 0")
})

run_test("describe_variable – with NAs", {
  x <- c(1:10, NA, NA)
  r <- describe_variable(x, "x")
  expect_true(r$n == 10L,        "n excludes NAs")
  expect_true(r$n_missing == 2L, "missing count correct")
})

run_test("describe_variable – all NA returns NAs", {
  r <- describe_variable(rep(NA_real_, 5), "v")
  expect_true(r$n == 0L,         "n == 0 for all-NA")
  expect_true(is.na(r$mean),     "mean is NA")
})

run_test("describe_variable – single value", {
  r <- describe_variable(rep(5, 3), "v")
  expect_true(r$mean == 5,       "mean == 5")
  expect_true(r$range == 0,      "range == 0")
})

# ── frequency_table ───────────────────────────────────────────────────────────

run_test("frequency_table – iris Species", {
  ft <- frequency_table(iris$Species, "Species")
  expect_true(is.data.frame(ft),       "returns data.frame")
  expect_true(nrow(ft) == 3,           "3 species")
  expect_true(all(ft$count == 50),     "each species has 50 rows")
  expect_true(abs(sum(ft$percent) - 100) < 0.1, "percents sum to ~100")
})

run_test("frequency_table – with NAs excluded", {
  x <- c("A", "B", NA, "A")
  ft <- frequency_table(x, "x")
  expect_true(sum(ft$count) == 3, "NAs excluded from counts")
})

# ── missing_data_report ───────────────────────────────────────────────────────

run_test("missing_data_report – airquality", {
  r <- missing_data_report(airquality)
  expect_true(is.data.frame(r),           "returns data.frame")
  expect_true("n_missing" %in% names(r),  "has n_missing")
  ozone <- r[r$variable == "Ozone", ]
  expect_true(ozone$n_missing > 0,        "Ozone has missing values")
})

run_test("missing_data_report – no missing", {
  r <- missing_data_report(mtcars)
  expect_true(all(r$n_missing == 0), "mtcars has no missing values")
})

# ── run_descriptive_phase ─────────────────────────────────────────────────────

run_test("run_descriptive_phase – numeric only", {
  r <- run_descriptive_phase(mtcars, numeric_vars = c("mpg", "wt"))
  expect_true(length(r$numeric_stats) == 2,  "two numeric summaries")
  expect_true(nchar(r$report) > 0,           "report is non-empty")
})

run_test("run_descriptive_phase – categorical only", {
  r <- run_descriptive_phase(iris, categorical_vars = "Species")
  expect_true(length(r$frequency_tables) == 1, "one frequency table")
})

run_test("run_descriptive_phase – mixed", {
  r <- run_descriptive_phase(iris,
         numeric_vars     = c("Sepal.Length", "Petal.Length"),
         categorical_vars = "Species")
  expect_true(length(r$numeric_stats) == 2,    "two numeric stats")
  expect_true(length(r$frequency_tables) == 1, "one freq table")
  expect_true(is.data.frame(r$missing_report), "missing report is data.frame")
})

# ── run_t_test ────────────────────────────────────────────────────────────────

run_test("run_t_test – mtcars mpg by am", {
  mtcars2 <- mtcars
  mtcars2$am <- as.factor(mtcars2$am)
  r <- run_t_test(mtcars2, "mpg", "am")
  expect_true(is.numeric(r$statistic),      "statistic is numeric")
  expect_true(is.numeric(r$p_value),        "p_value is numeric")
  expect_true(r$p_value >= 0 && r$p_value <= 1, "p_value in [0,1]")
  expect_true(is.numeric(r$cohen_d),        "cohen_d is numeric")
  expect_true(length(r$conf_int) == 2,      "conf_int has 2 elements")
  expect_true(r$ns[1] + r$ns[2] == 32L,    "group sizes sum to n")
})

run_test("run_t_test – wrong number of groups errors", {
  tryCatch({
    run_t_test(iris, "Sepal.Length", "Species")
    .test_fail <<- .test_fail + 1L
    cat("  FAIL: should have errored with 3 groups\n")
  }, error = function(e) {
    .test_pass <<- .test_pass + 1L
    cat("  PASS: correctly errored with 3 groups\n")
  })
})

run_test("run_t_test – significant result flagged", {
  # Known significant difference (manual vs automatic mpg)
  mtcars2 <- mtcars
  mtcars2$am <- as.factor(mtcars2$am)
  r <- run_t_test(mtcars2, "mpg", "am")
  expect_true(r$significant == (r$p_value < 0.05), "significant flag matches p-value")
})

# ── run_anova ────────────────────────────────────────────────────────────────

run_test("run_anova – iris Sepal.Length by Species", {
  r <- run_anova(iris, "Sepal.Length", "Species")
  expect_true(r$test_name == "One-way ANOVA",  "correct test name")
  expect_true(r$F_stat > 0,                    "F statistic > 0")
  expect_true(r$p_value < 0.001,               "iris groups differ significantly")
  expect_true(r$eta_squared > 0,               "eta_squared > 0")
  expect_true(r$eta_squared <= 1,              "eta_squared <= 1")
  expect_true(length(r$group_stats) == 3,      "three groups in results")
})

run_test("run_anova – effect size interpretation returned", {
  r <- run_anova(iris, "Sepal.Length", "Species")
  expect_true(r$effect_label %in% c("negligible","small","medium","large"),
              "effect label is valid")
})

# ── run_correlation ───────────────────────────────────────────────────────────

run_test("run_correlation – Pearson mtcars mpg vs wt", {
  r <- run_correlation(mtcars, "mpg", "wt")
  expect_true(abs(r$r) > 0.7,           "strong correlation mpg-wt")
  expect_true(r$r < 0,                  "negative correlation")
  expect_true(r$p_value < 0.001,        "significant")
  expect_true(length(r$conf_int) == 2,  "conf_int has 2 elements")
})

run_test("run_correlation – Spearman method", {
  r <- run_correlation(mtcars, "mpg", "wt", method = "spearman")
  expect_true(r$test_name == "Spearman Correlation", "Spearman name")
})

# ── run_chi_square ────────────────────────────────────────────────────────────

run_test("run_chi_square – sex vs pass", {
  set.seed(42)
  df <- data.frame(
    sex  = sample(c("M", "F"), 100, replace = TRUE),
    pass = sample(c("Y", "N"), 100, replace = TRUE)
  )
  r <- run_chi_square(df, "sex", "pass")
  expect_true(r$test_name == "Chi-square Test of Independence", "correct test name")
  expect_true(is.numeric(r$chi2),     "chi2 is numeric")
  expect_true(r$df >= 1L,             "df >= 1")
  expect_true(is.numeric(r$cramers_v),"cramers_v numeric")
})

# ── run_regression ────────────────────────────────────────────────────────────

run_test("run_regression – mtcars mpg ~ wt + hp", {
  r <- run_regression(mtcars, "mpg", c("wt", "hp"))
  expect_true(r$test_name == "Linear Regression", "correct test name")
  expect_true(r$r_squared > 0,              "R2 > 0")
  expect_true(r$r_squared <= 1,             "R2 <= 1")
  expect_true(nrow(r$coefficients) == 3,    "intercept + 2 predictors")
  expect_true(!is.null(r$fit),              "fit object returned")
})

# ── Effect size helpers ───────────────────────────────────────────────────────

run_test("effect size helpers – Cohen's d boundaries", {
  expect_true(interpret_effect_size_d(0.0)  == "negligible", "d=0 negligible")
  expect_true(interpret_effect_size_d(0.25) == "small",      "d=0.25 small")
  expect_true(interpret_effect_size_d(0.6)  == "medium",     "d=0.6 medium")
  expect_true(interpret_effect_size_d(1.0)  == "large",      "d=1.0 large")
  expect_true(interpret_effect_size_d(NA)   == "unknown",    "d=NA unknown")
})

run_test("effect size helpers – eta-squared", {
  expect_true(interpret_effect_size_eta2(0.001) == "negligible", "eta2 negligible")
  expect_true(interpret_effect_size_eta2(0.03)  == "small",      "eta2 small")
  expect_true(interpret_effect_size_eta2(0.10)  == "medium",     "eta2 medium")
  expect_true(interpret_effect_size_eta2(0.20)  == "large",      "eta2 large")
})

run_test("effect size helpers – Pearson r", {
  expect_true(interpret_effect_size_r(0.05) == "negligible", "r negligible")
  expect_true(interpret_effect_size_r(0.2)  == "small",      "r small")
  expect_true(interpret_effect_size_r(0.4)  == "medium",     "r medium")
  expect_true(interpret_effect_size_r(0.6)  == "large",      "r large")
})

# ── run_analysis_workflow (integration) ───────────────────────────────────────

run_test("run_analysis_workflow – t_test complete", {
  df <- data.frame(
    score = c(rnorm(30, 75, 8), rnorm(30, 72, 9)),
    sex   = rep(c("F", "M"), each = 30)
  )
  wf <- run_analysis_workflow(
    query         = "Compare test scores between male and female students",
    data          = df,
    analysis_type = "t_test",
    outcome_var   = "score",
    group_var     = "sex"
  )
  expect_true(!is.null(wf$validation),   "validation phase present")
  expect_true(!is.null(wf$descriptive),  "descriptive phase present")
  expect_true(!is.null(wf$assumptions),  "assumptions phase present")
  expect_true(!is.null(wf$test),         "test phase present")
  expect_true(nchar(wf$full_report) > 0, "full_report non-empty")
})

run_test("run_analysis_workflow – descriptive only (no test)", {
  wf <- run_analysis_workflow(
    query         = "Summarise the iris dataset",
    data          = iris,
    analysis_type = "descriptive"
  )
  expect_true(wf$validation$valid,        "valid inputs")
  expect_true(is.null(wf$test),           "no test for descriptive")
})

run_test("run_analysis_workflow – invalid query aborts early", {
  wf <- run_analysis_workflow(
    query = "",
    data  = mtcars
  )
  expect_false(wf$validation$valid, "invalid query aborts")
  expect_true(grepl("aborted", wf$full_report, ignore.case = TRUE),
              "full_report mentions abort")
})

run_test("run_analysis_workflow – regression complete", {
  wf <- run_analysis_workflow(
    query          = "Predict mpg from weight and horsepower",
    data           = mtcars,
    analysis_type  = "regression",
    outcome_var    = "mpg",
    predictor_vars = c("wt", "hp")
  )
  expect_true(!is.null(wf$test), "regression test performed")
  expect_true(wf$test$r_squared > 0, "R2 > 0")
})

# ── Summary ────────────────────────────────────────────────────────────────────

cat(sprintf("\n══════════════════════════════════════\n"))
cat(sprintf("Analysis Workflow Tests: %d passed, %d failed\n",
            .test_pass, .test_fail))
if (.test_fail == 0) {
  cat("✓ All tests passed.\n")
} else {
  cat(sprintf("✗ %d test(s) failed.\n", .test_fail))
}
