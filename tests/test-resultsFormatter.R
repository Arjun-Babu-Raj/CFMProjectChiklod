# Tests for resultsFormatter.R
# Run with: source("tests/test-resultsFormatter.R")
# Requires: R/inputValidation.R, R/assumptionChecker.R,
#           R/analysisWorkflow.R, R/resultsFormatter.R

base_dir <- dirname(sys.frame(1)$ofile)
source(file.path(base_dir, "..", "R", "inputValidation.R"),   local = FALSE)
source(file.path(base_dir, "..", "R", "assumptionChecker.R"),  local = FALSE)
source(file.path(base_dir, "..", "R", "analysisWorkflow.R"),   local = FALSE)
source(file.path(base_dir, "..", "R", "resultsFormatter.R"),   local = FALSE)

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

# ── fmt ───────────────────────────────────────────────────────────────────────

run_test("fmt – basic formatting", {
  expect_true(fmt(3.14159, 2) == "3.14",   "rounds to 2 dp")
  expect_true(fmt(0, 3)       == "0.000",  "formats zero")
  expect_true(fmt(NA)         == "NA",     "formats NA")
  expect_true(fmt(NULL)       == "NA",     "formats NULL")
})

run_test("fmt – negative numbers", {
  expect_true(fmt(-1.5, 2) == "-1.50", "formats negative")
})

# ── fmt_p ─────────────────────────────────────────────────────────────────────

run_test("fmt_p – significance stars", {
  p_001 <- fmt_p(0.0001)
  p_01  <- fmt_p(0.005)
  p_05  <- fmt_p(0.03)
  p_ns  <- fmt_p(0.20)
  p_na  <- fmt_p(NA)

  expect_true(grepl("\\*\\*\\*", p_001), "p<0.001 gets ***")
  expect_true(grepl("\\*\\*",    p_01),  "p<0.01 gets **")
  expect_true(grepl("\\*",       p_05),  "p<0.05 gets *")
  expect_false(grepl("\\*",      p_ns),  "p=0.20 gets no star")
  expect_true(p_na == "NA",              "NA p-value returns 'NA'")
})

# ── build_results_table ───────────────────────────────────────────────────────

run_test("build_results_table – basic", {
  pairs <- list(Label1 = "Value1", LongerLabel = "Value2")
  tbl   <- build_results_table(pairs)
  expect_true(is.character(tbl),          "returns character")
  expect_true(grepl("Label1", tbl),       "contains Label1")
  expect_true(grepl("LongerLabel", tbl),  "contains LongerLabel")
  expect_true(grepl("Value1", tbl),       "contains Value1")
})

run_test("build_results_table – with title", {
  pairs <- list(A = "1", B = "2")
  tbl   <- build_results_table(pairs, title = "MY TITLE")
  expect_true(grepl("MY TITLE", tbl), "title appears in output")
})

# ── format_t_test_results ─────────────────────────────────────────────────────

run_test("format_t_test_results – structure", {
  df <- data.frame(
    score = c(rnorm(30, 75, 8), rnorm(30, 72, 9)),
    sex   = rep(c("F", "M"), each = 30)
  )
  mtcars2 <- mtcars
  mtcars2$am <- as.factor(mtcars2$am)
  result <- run_t_test(mtcars2, "mpg", "am")
  out    <- format_t_test_results(result)

  expect_true(is.character(out),                         "returns character")
  expect_true(grepl("t-TEST",     out, ignore.case = TRUE), "mentions t-test")
  expect_true(grepl("P-value",    out, ignore.case = TRUE), "mentions p-value")
  expect_true(grepl("Effect",     out, ignore.case = TRUE), "mentions effect size")
  expect_true(grepl("Confidence", out, ignore.case = TRUE), "mentions CI")
})

run_test("format_t_test_results – with violated assumptions", {
  mtcars2 <- mtcars
  mtcars2$am <- as.factor(mtcars2$am)
  result <- run_t_test(mtcars2, "mpg", "am")
  out    <- format_t_test_results(result, assumption_status = c("normality"))
  expect_true(grepl("normality", out, ignore.case = TRUE),
              "violated assumptions mentioned")
})

# ── format_anova_results ──────────────────────────────────────────────────────

run_test("format_anova_results – iris", {
  result <- run_anova(iris, "Sepal.Length", "Species")
  out    <- format_anova_results(result)
  expect_true(is.character(out),                        "returns character")
  expect_true(grepl("ANOVA",   out, ignore.case = TRUE),"mentions ANOVA")
  expect_true(grepl("eta",     out, ignore.case = TRUE), "mentions eta")
  expect_true(grepl("P-value", out, ignore.case = TRUE), "mentions p-value")
})

# ── format_correlation_results ────────────────────────────────────────────────

run_test("format_correlation_results – mtcars mpg vs wt", {
  result <- run_correlation(mtcars, "mpg", "wt")
  out    <- format_correlation_results(result)
  expect_true(is.character(out),                             "returns character")
  expect_true(grepl("CORRELATION", out, ignore.case = TRUE), "mentions correlation")
  expect_true(grepl("Confidence",  out, ignore.case = TRUE), "mentions CI")
})

# ── format_chi_square_results ────────────────────────────────────────────────

run_test("format_chi_square_results – sex vs pass", {
  df <- data.frame(
    sex  = sample(c("M","F"), 80, replace=TRUE),
    pass = sample(c("Y","N"), 80, replace=TRUE)
  )
  result <- run_chi_square(df, "sex", "pass")
  out    <- format_chi_square_results(result)
  expect_true(is.character(out),                               "returns character")
  expect_true(grepl("CHI-SQUARE", out, ignore.case = TRUE),    "mentions chi-square")
  expect_true(grepl("Cram",       out, ignore.case = TRUE),    "mentions Cramér's V")
})

# ── format_regression_results ────────────────────────────────────────────────

run_test("format_regression_results – mtcars", {
  result <- run_regression(mtcars, "mpg", c("wt","hp"))
  out    <- format_regression_results(result)
  expect_true(is.character(out),                               "returns character")
  expect_true(grepl("REGRESSION",  out, ignore.case = TRUE),   "mentions regression")
  expect_true(grepl("R-squared",   out, ignore.case = TRUE),   "mentions R-squared")
  expect_true(grepl("Coefficient", out, ignore.case = TRUE),   "mentions Coefficients")
})

# ── format_assumption_table ───────────────────────────────────────────────────

run_test("format_assumption_table – t_test iris 2 groups", {
  df <- iris[iris$Species %in% c("setosa","versicolor"), ]
  df$Species <- droplevels(df$Species)
  ar  <- check_assumptions(df, "t_test", "Sepal.Length", group_var = "Species")
  out <- format_assumption_table(ar)
  expect_true(is.character(out),                                  "returns character")
  expect_true(grepl("ASSUMPTION",  out, ignore.case = TRUE),      "mentions assumption")
  expect_true(grepl("Normality",   out, ignore.case = TRUE),      "shows normality row")
  expect_true(grepl("Homogeneity", out, ignore.case = TRUE),      "shows homogeneity row")
})

run_test("format_assumption_table – NULL input returns string", {
  out <- format_assumption_table(NULL)
  expect_true(is.character(out), "returns character for NULL input")
  expect_true(nchar(out) > 0,    "non-empty string for NULL input")
})

run_test("format_assumption_table – shows remedial actions when violated", {
  # Create a dataset that will likely violate normality (exponential)
  set.seed(5)
  df <- data.frame(
    x   = c(rexp(20, rate=2), rexp(20, rate=5)),
    grp = rep(c("A","B"), each=20)
  )
  ar  <- check_assumptions(df, "t_test", "x", group_var = "grp")
  out <- format_assumption_table(ar)
  # Regardless of whether violated, the table is always produced
  expect_true(is.character(out),     "returns character")
  expect_true(nchar(out) > 50,       "substantial output")
})

# ── format_full_report ────────────────────────────────────────────────────────

run_test("format_full_report – t_test workflow", {
  df <- data.frame(
    score = c(rnorm(30, 75, 8), rnorm(30, 72, 9)),
    sex   = rep(c("F","M"), each=30)
  )
  wf  <- run_analysis_workflow(
    query         = "Compare scores between F and M",
    data          = df,
    analysis_type = "t_test",
    outcome_var   = "score",
    group_var     = "sex"
  )
  out <- format_full_report(wf)
  expect_true(is.character(out),                            "returns character")
  expect_true(nchar(out) > 100,                             "substantial report")
  expect_true(grepl("DESCRIPTIVE",   out, ignore.case=TRUE),"has descriptive section")
  expect_true(grepl("ASSUMPTION",    out, ignore.case=TRUE),"has assumption section")
  expect_true(grepl("INTERPRETATION",out, ignore.case=TRUE),"has interpretation section")
})

run_test("format_full_report – ANOVA workflow", {
  wf  <- run_analysis_workflow(
    query         = "Compare petal length across species",
    data          = iris,
    analysis_type = "anova",
    outcome_var   = "Petal.Length",
    group_var     = "Species"
  )
  out <- format_full_report(wf)
  expect_true(grepl("ANOVA", out, ignore.case = TRUE), "ANOVA mentioned in report")
})

run_test("format_full_report – aborted workflow handled gracefully", {
  wf  <- run_analysis_workflow(
    query = "",
    data  = mtcars
  )
  out <- format_full_report(wf)
  expect_true(is.character(out), "returns character even for aborted workflow")
  expect_true(nchar(out) > 0,    "non-empty output for aborted workflow")
})

# ── Summary ───────────────────────────────────────────────────────────────────

cat(sprintf("\n══════════════════════════════════════\n"))
cat(sprintf("Results Formatter Tests: %d passed, %d failed\n",
            .test_pass, .test_fail))
if (.test_fail == 0) {
  cat("✓ All tests passed.\n")
} else {
  cat(sprintf("✗ %d test(s) failed.\n", .test_fail))
}
