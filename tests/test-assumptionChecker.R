# Tests for assumptionChecker.R
# Run with: source("tests/test-assumptionChecker.R")
# Requires: R/assumptionChecker.R

source(file.path(dirname(sys.frame(1)$ofile), "..", "R", "assumptionChecker.R"),
       local = FALSE)

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

set.seed(123)

# ── test_normality ─────────────────────────────────────────────────────────────

run_test("test_normality – normal data (rnorm)", {
  x <- rnorm(50)
  r <- test_normality(x, "x")
  expect_true(r$test %in% c("Shapiro-Wilk", "Kolmogorov-Smirnov"),
              "recognised test used")
  expect_true(is.numeric(r$statistic), "statistic is numeric")
  expect_true(is.numeric(r$p_value),   "p_value is numeric")
  expect_true(is.logical(r$normal),    "normal is logical")
})

run_test("test_normality – clearly non-normal (exponential)", {
  x <- rexp(50, rate = 5)
  r <- test_normality(x)
  # Exponential distribution is very non-normal; this should often fail
  expect_true(nchar(r$interpretation) > 0, "interpretation is non-empty")
})

run_test("test_normality – too few observations", {
  r <- test_normality(c(1, 2), "v")
  expect_true(is.na(r$statistic), "NA statistic for n < 3")
  expect_true(is.na(r$normal),    "NA normal for n < 3")
})

run_test("test_normality – with NA values handled", {
  x <- c(rnorm(40), NA, NA)
  r <- test_normality(x)
  expect_true(is.numeric(r$p_value), "NAs handled; p_value numeric")
})

run_test("test_normality – large sample uses KS or SW", {
  x <- rnorm(200)
  r <- test_normality(x, alpha = 0.05)
  expect_true(r$test %in% c("Shapiro-Wilk", "Kolmogorov-Smirnov"), "valid test for n=200")
})

# ── test_normality_by_group ────────────────────────────────────────────────────

run_test("test_normality_by_group – iris", {
  r <- test_normality_by_group(iris, "Sepal.Length", "Species")
  expect_true(length(r$results) == 3,        "three groups in iris")
  expect_true(is.logical(r$all_normal),      "all_normal is logical")
  expect_true(nchar(r$summary) > 0,          "summary is non-empty")
})

run_test("test_normality_by_group – missing outcome_var errors", {
  tryCatch({
    test_normality_by_group(iris, "bad_var", "Species")
    .test_fail <<- .test_fail + 1L
    cat("  FAIL: should have errored\n")
  }, error = function(e) {
    .test_pass <<- .test_pass + 1L
    cat("  PASS: correctly errored on bad outcome_var\n")
  })
})

# ── test_homogeneity ───────────────────────────────────────────────────────────

run_test("test_homogeneity – iris (3 groups)", {
  r <- test_homogeneity(iris, "Sepal.Length", "Species")
  expect_true(r$test == "Levene",             "correct test name")
  expect_true(is.numeric(r$statistic),        "statistic is numeric")
  expect_true(is.numeric(r$p_value),          "p_value is numeric")
  expect_true(is.logical(r$equal_variances),  "equal_variances is logical")
})

run_test("test_homogeneity – mtcars by am (2 groups)", {
  mtcars2 <- mtcars
  mtcars2$am <- as.factor(mtcars2$am)
  r <- test_homogeneity(mtcars2, "mpg", "am")
  expect_true(r$df1 == 1L,  "df1 == 1 for 2 groups")
  expect_true(r$df2 > 0,    "df2 > 0")
})

run_test("test_homogeneity – missing group_var errors", {
  tryCatch({
    test_homogeneity(iris, "Sepal.Length", "bad_col")
    .test_fail <<- .test_fail + 1L
    cat("  FAIL: should have errored\n")
  }, error = function(e) {
    .test_pass <<- .test_pass + 1L
    cat("  PASS: correctly errored on missing group_var\n")
  })
})

# ── test_homogeneity_bartlett ──────────────────────────────────────────────────

run_test("test_homogeneity_bartlett – iris", {
  r <- test_homogeneity_bartlett(iris, "Sepal.Length", "Species")
  expect_true(r$test == "Bartlett",            "correct test name")
  expect_true(is.numeric(r$statistic),         "statistic numeric")
  expect_true(is.numeric(r$p_value),           "p_value numeric")
  expect_true(is.logical(r$equal_variances),   "equal_variances logical")
})

# ── test_independence ──────────────────────────────────────────────────────────

run_test("test_independence – regression residuals", {
  m <- lm(mpg ~ wt, data = mtcars)
  r <- test_independence(residuals(m))
  expect_true(r$test == "Durbin-Watson",    "correct test name")
  expect_true(is.numeric(r$statistic),      "statistic is numeric")
  expect_true(r$statistic > 0,              "DW statistic > 0")
  expect_true(is.logical(r$independent),    "independent is logical")
})

run_test("test_independence – uncorrelated residuals near 2", {
  # White noise should give DW near 2 (independent)
  set.seed(7)
  r <- test_independence(rnorm(100))
  expect_true(r$statistic > 1.0 && r$statistic < 3.0, "DW in plausible range")
})

run_test("test_independence – too few residuals", {
  r <- test_independence(c(0.1, 0.2))
  expect_true(is.na(r$statistic), "NA for < 3 residuals")
})

# ── assess_linearity ───────────────────────────────────────────────────────────

run_test("assess_linearity – strong linear relationship (mtcars)", {
  r <- assess_linearity(mtcars, "wt", "mpg")
  expect_true(is.numeric(r$pearson_r),       "pearson_r is numeric")
  expect_true(is.numeric(r$spearman_r),      "spearman_r is numeric")
  expect_true(is.numeric(r$p_value_pearson), "p_value numeric")
  expect_true(abs(r$pearson_r) > 0.7,        "strong negative correlation wt-mpg")
})

run_test("assess_linearity – missing variable errors", {
  tryCatch({
    assess_linearity(mtcars, "bad", "mpg")
    .test_fail <<- .test_fail + 1L
    cat("  FAIL: should have errored\n")
  }, error = function(e) {
    .test_pass <<- .test_pass + 1L
    cat("  PASS: correctly errored\n")
  })
})

run_test("assess_linearity – insufficient complete cases", {
  df <- data.frame(x = c(1, 2, NA, NA), y = c(1, NA, 3, NA))
  r  <- assess_linearity(df, "x", "y")
  expect_true(is.na(r$pearson_r), "NA returned for insufficient complete cases")
})

# ── check_multicollinearity ────────────────────────────────────────────────────

run_test("check_multicollinearity – mtcars (wt, hp)", {
  r <- check_multicollinearity(mtcars, "mpg", c("wt", "hp"))
  expect_true(length(r$vif_values) == 2,     "two VIF values returned")
  expect_true(all(r$vif_values >= 1),        "VIF >= 1")
  expect_true(is.logical(r$multicollinear),  "multicollinear is logical")
})

run_test("check_multicollinearity – single predictor returns VIF = 1", {
  r <- check_multicollinearity(mtcars, "mpg", "wt")
  expect_true(r$vif_values[1] == 1,          "single predictor VIF = 1")
  expect_false(r$multicollinear,             "not multicollinear with one predictor")
})

run_test("check_multicollinearity – missing variable returns issues", {
  r <- check_multicollinearity(mtcars, "mpg", c("wt", "bad_var"))
  expect_true(length(r$issues) > 0, "missing variable creates issues")
})

# ── check_assumptions ─────────────────────────────────────────────────────────

run_test("check_assumptions – t_test on iris (2 species)", {
  df <- iris[iris$Species %in% c("setosa", "versicolor"), ]
  df$Species <- droplevels(df$Species)
  r <- check_assumptions(df, "t_test", "Sepal.Length", group_var = "Species")
  expect_true(is.character(r$report),   "report is character")
  expect_true(nchar(r$report) > 0,      "report is non-empty")
  expect_true(is.character(r$violated), "violated is character vector")
})

run_test("check_assumptions – regression on mtcars", {
  r <- check_assumptions(mtcars, "regression", "mpg",
                          predictor_vars = c("wt", "hp"))
  expect_true("independence" %in% names(r$details) ||
              "linearity" %in% names(r$details),
              "regression checks include independence or linearity")
})

run_test("check_assumptions – anova on iris", {
  r <- check_assumptions(iris, "anova", "Petal.Length", group_var = "Species")
  expect_true("normality" %in% names(r$details),   "normality checked")
  expect_true("homogeneity" %in% names(r$details), "homogeneity checked")
})

run_test("check_assumptions – report always non-empty", {
  r <- check_assumptions(mtcars, "t_test", "mpg", group_var = "am")
  expect_true(nchar(r$report) > 50, "report has meaningful content")
})

# ── Summary ────────────────────────────────────────────────────────────────────

cat(sprintf("\n══════════════════════════════════════\n"))
cat(sprintf("Assumption Checker Tests: %d passed, %d failed\n",
            .test_pass, .test_fail))
if (.test_fail == 0) {
  cat("✓ All tests passed.\n")
} else {
  cat(sprintf("✗ %d test(s) failed.\n", .test_fail))
}
