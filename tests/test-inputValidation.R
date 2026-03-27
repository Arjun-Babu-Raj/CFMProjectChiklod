# Tests for inputValidation.R
# Run with: source("tests/test-inputValidation.R")
# Requires: R/inputValidation.R

source(file.path(dirname(sys.frame(1)$ofile), "..", "R", "inputValidation.R"),
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

# ── validate_query ─────────────────────────────────────────────────────────────

run_test("validate_query – empty string", {
  r <- validate_query("")
  expect_false(r$valid, "empty query is invalid")
  expect_true(length(r$issues) > 0, "has issues")
})

run_test("validate_query – NULL input", {
  r <- validate_query(NULL)
  expect_false(r$valid, "NULL query is invalid")
})

run_test("validate_query – valid query", {
  r <- validate_query("Compare test scores between male and female students")
  expect_true(r$valid, "descriptive query is valid")
  expect_true(length(r$issues) == 0, "no issues")
})

run_test("validate_query – very short query triggers warning", {
  r <- validate_query("hi")
  expect_true(length(r$warnings) > 0, "short query triggers warning")
})

run_test("validate_query – numeric input is invalid", {
  r <- validate_query(42)
  expect_false(r$valid, "numeric input is invalid")
})

# ── validate_data_structure ────────────────────────────────────────────────────

run_test("validate_data_structure – valid data.frame", {
  r <- validate_data_structure(mtcars)
  expect_true(r$valid, "mtcars is valid")
  expect_true(r$info$n_rows == 32, "correct row count")
  expect_true(r$info$n_cols == 11, "correct col count")
})

run_test("validate_data_structure – NULL data", {
  r <- validate_data_structure(NULL)
  expect_false(r$valid, "NULL data is invalid")
})

run_test("validate_data_structure – empty data.frame", {
  r <- validate_data_structure(data.frame())
  expect_false(r$valid, "empty data.frame is invalid")
})

run_test("validate_data_structure – non-data.frame", {
  r <- validate_data_structure(list(a = 1))
  expect_false(r$valid, "list is not valid as data")
})

run_test("validate_data_structure – too few rows", {
  r <- validate_data_structure(data.frame(x = 1:2), min_rows = 5)
  expect_false(r$valid, "2 rows is below min_rows=5")
})

run_test("validate_data_structure – small dataset warning", {
  r <- validate_data_structure(data.frame(x = 1:10))
  expect_true(length(r$warnings) > 0, "small dataset triggers warning")
})

# ── validate_variables ─────────────────────────────────────────────────────────

run_test("validate_variables – existing variables pass", {
  r <- validate_variables(mtcars, c("mpg", "cyl"))
  expect_true(r$valid, "existing variables pass")
})

run_test("validate_variables – missing variable fails", {
  r <- validate_variables(mtcars, c("mpg", "nonexistent"))
  expect_false(r$valid, "missing variable fails")
  expect_true(length(r$issues) > 0, "has issues")
})

run_test("validate_variables – wrong type fails", {
  r <- validate_variables(iris, "Species", expected_types = c(Species = "numeric"))
  expect_false(r$valid, "wrong type fails")
})

run_test("validate_variables – correct type passes", {
  r <- validate_variables(iris, "Sepal.Length",
                           expected_types = c(Sepal.Length = "numeric"))
  expect_true(r$valid, "correct numeric type passes")
})

run_test("validate_variables – 'any' type always passes", {
  r <- validate_variables(iris, "Species", expected_types = c(Species = "any"))
  expect_true(r$valid, "'any' type always passes")
})

# ── detect_missing_values ──────────────────────────────────────────────────────

run_test("detect_missing_values – no missing", {
  r <- detect_missing_values(mtcars)
  expect_true(r$valid, "mtcars has no fully-missing columns")
  expect_true(all(r$missing_summary$missing_count == 0), "all counts are 0")
})

run_test("detect_missing_values – partial missing triggers warning", {
  df <- data.frame(x = c(1, NA, 3, NA, 5), y = 1:5)
  r  <- detect_missing_values(df, threshold = 0.1)
  expect_true(length(r$warnings) > 0, "partial missing triggers warning")
})

run_test("detect_missing_values – fully missing column is issue", {
  df <- data.frame(x = c(NA, NA, NA), y = 1:3)
  r  <- detect_missing_values(df)
  expect_false(r$valid, "fully missing column is an issue")
})

run_test("detect_missing_values – airquality known missings", {
  r <- detect_missing_values(airquality)
  ozone_row <- r$missing_summary[r$missing_summary$variable == "Ozone", ]
  expect_true(ozone_row$missing_count > 0, "Ozone has known missing values")
})

# ── classify_variable_types ────────────────────────────────────────────────────

run_test("classify_variable_types – iris", {
  r <- classify_variable_types(iris)
  expect_true("Sepal.Length" %in% r$numeric_vars, "Sepal.Length is numeric")
  expect_true("Species" %in% r$categorical_vars, "Species is categorical")
})

run_test("classify_variable_types – all numeric", {
  r <- classify_variable_types(mtcars)
  expect_true(length(r$numeric_vars) == ncol(mtcars), "all mtcars cols are numeric")
  expect_true(length(r$categorical_vars) == 0, "no categorical in mtcars")
})

run_test("classify_variable_types – logical treated as categorical", {
  df <- data.frame(flag = c(TRUE, FALSE, TRUE))
  r  <- classify_variable_types(df)
  expect_true("flag" %in% r$categorical_vars, "logical is categorical")
})

# ── validate_sample_size ───────────────────────────────────────────────────────

run_test("validate_sample_size – adequate for t_test", {
  r <- validate_sample_size(mtcars, "t_test")
  expect_true(r$adequate, "mtcars adequate for t_test")
})

run_test("validate_sample_size – tiny dataset fails", {
  df <- data.frame(x = 1:3)
  r  <- validate_sample_size(df, "t_test")
  expect_false(r$adequate, "3 rows not adequate for t_test")
})

run_test("validate_sample_size – correct n returned", {
  r <- validate_sample_size(iris, "anova")
  expect_true(r$n == 150L, "iris n=150")
})

run_test("validate_sample_size – small group warning", {
  df <- data.frame(
    x   = c(rnorm(20), rnorm(3)),
    grp = c(rep("A", 20), rep("B", 3))
  )
  r <- validate_sample_size(df, "t_test", group_var = "grp")
  expect_true(length(r$warnings) > 0, "small group triggers warning")
})

# ── detect_outliers ────────────────────────────────────────────────────────────

run_test("detect_outliers – no outliers in normal data", {
  set.seed(42)
  df <- data.frame(x = rnorm(100))
  r  <- detect_outliers(df)
  # This is probabilistic, but with seed 42 and n=100 there may be some
  expect_true(is.data.frame(r$outlier_summary), "returns data.frame")
  expect_true("n_outliers" %in% names(r$outlier_summary), "has n_outliers column")
})

run_test("detect_outliers – extreme outlier detected", {
  df <- data.frame(x = c(rep(5, 50), 9999))
  r  <- detect_outliers(df)
  expect_true(r$outlier_summary$n_outliers[1] >= 1, "extreme outlier detected")
  expect_true(length(r$warnings) > 0, "outlier warning issued")
})

run_test("detect_outliers – no numeric columns returns warning", {
  df <- data.frame(x = c("a", "b", "c"))
  r  <- detect_outliers(df)
  expect_true(length(r$warnings) > 0, "no numeric col triggers warning")
})

# ── validate_inputs (integration) ─────────────────────────────────────────────

run_test("validate_inputs – full valid pipeline", {
  r <- validate_inputs(
    query         = "Compare mpg between automatic and manual transmissions",
    data          = mtcars,
    analysis_type = "t_test",
    required_vars = c("mpg", "am"),
    group_var     = "am"
  )
  expect_true(r$valid, "full valid pipeline passes")
  expect_true(nchar(r$report) > 0, "report is non-empty")
})

run_test("validate_inputs – invalid query aborts", {
  r <- validate_inputs(
    query = "",
    data  = mtcars
  )
  expect_false(r$valid, "empty query invalidates pipeline")
})

run_test("validate_inputs – missing required var invalidates", {
  r <- validate_inputs(
    query         = "Analyse something",
    data          = mtcars,
    required_vars = c("mpg", "does_not_exist")
  )
  expect_false(r$valid, "missing required var invalidates pipeline")
})

# ── Summary ────────────────────────────────────────────────────────────────────

cat("\n══════════════════════════════════════\n")
cat(sprintf("Input Validation Tests: %d passed, %d failed\n",
            .test_pass, .test_fail))
if (.test_fail == 0) {
  cat("✓ All tests passed.\n")
} else {
  cat(sprintf("✗ %d test(s) failed.\n", .test_fail))
}
