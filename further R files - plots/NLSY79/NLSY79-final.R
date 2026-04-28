# Set working directory
setwd("/Users/mia8425/Documents/Studium/6. Semester SS 2026/SE Seminar/further R files - plots/NLSY79")
pdf("NLSY79-plot.pdf", width = 8, height = 5)

# downloaded from https://www.nlsinfo.org/investigator/pages/search
# .dat file is not accepted for submission
new_data <- read.table('NLSY79-final.dat', sep=' ')
names(new_data) <- c('C0000100',
  'C0000200',
  'C0005300',
  'C0005400',
  'C0005700',
  'C0006500',
  'C0006600',
  'C0006800',
  'C0006900',
  'C0007010',
  'C0007020',
  'C0007030',
  'C0007040',
  'C0007041',
  'C0007042',
  'C0007043',
  'C0007044',
  'C0007045',
  'C0007046',
  'C0007047',
  'C0007048',
  'C0007049',
  'C0007050',
  'C0007052',
  'C0007053',
  'C0007055',
  'C0007056',
  'C0407900',
  'C0408000',
  'C0577600',
  'C0577700',
  'C0606300',
  'C0606400',
  'C0606600',
  'C0826400',
  'C0826500',
  'C0826700',
  'C1016700',
  'C1016800',
  'C1017000',
  'C1220200',
  'C1220300',
  'C1220500',
  'C1532700',
  'C1532800',
  'C1533000',
  'C1779300',
  'C1779400',
  'C1779600',
  'C2288500',
  'C2288600',
  'C2288800',
  'C2552200',
  'C2553200',
  'C2820800',
  'C2821700',
  'C3130300',
  'C3131200',
  'C3553300',
  'C3554200',
  'C3601100',
  'C3601200',
  'C3634400',
  'C3635200',
  'C3897900',
  'C3898800',
  'C3981100',
  'C3981200',
  'C4012900',
  'C4013700',
  'C5147800',
  'C5148700',
  'C5524800',
  'C5524900',
  'C5556900',
  'C5557700',
  'C5725100',
  'C5725900',
  'Y2267000')

# Handle missing values

new_data[new_data == -1] = NA  # Refused
new_data[new_data == -2] = NA  # Dont know
new_data[new_data == -3] = NA  # Invalid missing
new_data[new_data == -7] = NA  # Missing

#********************************************************************************************************

# Produce summaries for the raw (uncategorized) data file
#summary(new_data)

#************************************************************************************************************
library(dplyr)
library(ggplot2)
library(childsds)


################################################### Extract and standardize data
# Age is in months
# Weight is in pounds (ounces ignored)

nd <- new_data %>%
  mutate(
    child_id = C0000100,
    sex      = C0005400,  # 1 = male, 2 = female
    # Age in months, pick child-supplement age CS. if not available, fall back to mother-supplement MS
    age1986 = coalesce(C0006500, C0006600),
    age1988 = coalesce(C0006800, C0006900),
    age1990 = coalesce(C0007010, C0007020),
    age1992 = coalesce(C0007030, C0007040),
    age1994 = coalesce(C0007041, C0007042),
    age1996 = coalesce(C0007043, C0007044),
    age1998 = coalesce(C0007045, C0007046),
    age2000 = coalesce(C0007047, C0007048),
    age2004 = coalesce(C0007052, C0007053),
    age2002 = coalesce(C0007049, C0007050),
    age2006 = coalesce(C0007055, C0007056),
    age2008 = coalesce(C3601100, C3601200),
    age2010 = coalesce(C3981100, C3981200),
    age2012 = coalesce(C5524800, C5524900),
    # Heights in inches
    # total inches = feet * 12 + inches
    hgt1986 = C0577600,                           # already total inches
    hgt1988 = C0606300 * 12 + C0606400,           
    hgt1990 = C0826400 * 12 + C0826500,
    hgt1992 = C1016700 * 12 + C1016800,
    hgt1994 = C1220200 * 12 + C1220300,
    hgt1996 = C1532700 * 12 + C1532800,
    hgt1998 = C1779300 * 12 + C1779400,
    hgt2000 = C2288500 * 12 + C2288600,
    hgt2002 = C2552200,
    hgt2004 = C2820800,                           
    hgt2006 = coalesce(C3130300, C3553300),       # CS, then MS
    hgt2008 = coalesce(C3634400, C3897900),
    hgt2010 = coalesce(C4012900, C5147800),
    hgt2012 = coalesce(C5556900, C5725100),
    # Weights in pounds (ounces omitted)
    wgt1986 = C0577700,
    wgt1988 = C0606600,
    wgt1990 = C0826700,
    wgt1992 = C1017000,
    wgt1994 = C1220500,
    wgt1996 = C1533000,
    wgt1998 = C1779600,
    wgt2000 = C2288800,
    wgt2002 = C2553200,
    wgt2004 = C2821700,
    wgt2006 = coalesce(C3131200, C3554200),
    wgt2008 = coalesce(C3635200, C3898800),
    wgt2010 = coalesce(C4013700, C5148700),
    wgt2012 = coalesce(C5557700, C5725900)
  )

######################################## Reshapeing (one row per child per wave)
# years becomes a column instead of having multiple columns of the same
# info for the different years

years <- c(1986, 1988, 1990, 1992, 1994, 1996, 1998, 2000, 2004, 2006, 2008, 2010, 2012) 

long <- bind_rows(lapply(years, function(yr) {
  nd %>%
    select(
      child_id, sex,
      age = paste0("age", yr),
      hgt = paste0("hgt", yr),
      wgt = paste0("wgt", yr)
    ) %>%
    mutate(wave = yr)
}))

################################### Filter for Elementary school aged children
# (and to clean up the height/weight observations)
# Range filters to remove data entry errors
#   Height: 36-72 inches (3 to 6 feet)
#   Weight: 25-200 lbs (13kg to 90kg)
# These are very broad because I want to include over und underweight kids

hw_clean <- long %>% 
  filter(!is.na(age), 
        !is.na(hgt), 
        !is.na(wgt), 
        !is.na(sex), 
        hgt >= 36, hgt <= 72, 
        wgt >= 25, wgt <= 200) 

elem <- hw_clean %>% filter(age >= 72, age <= 131)
# see how many observations we have per wave
elem %>% count(wave)

################################################ Create 2-year observation pairs 
# Join each observation with the same child's observation 2 years later

pairs <- elem %>%
  rename(age_start = age, hgt_start = hgt, wgt_start = wgt, wave_start = wave) %>%
  inner_join(
    # at end age children can be older than elem
    hw_clean %>%
      rename(age_end = age, hgt_end = hgt, wgt_end = wgt, wave_end = wave),
    by = "child_id",
    relationship = "many-to-many"
    # to first get all possible start-end pairs for each child
  ) %>%
  # we need to keep only 2-year observation pairs
  filter(wave_end == wave_start + 2) %>%
  select(-sex.y) %>%
  rename(sex = sex.x)
  # would otherwise be duplicate


pairs_only_elem <- elem %>%
  rename(age_start = age, hgt_start = hgt, wgt_start = wgt, wave_start = wave) %>%
  inner_join(
    # at end age children canNOT be older than elem
    elem %>%
      rename(age_end = age, hgt_end = hgt, wgt_end = wgt, wave_end = wave),
    by = "child_id",
    relationship = "many-to-many"
    # to first get all possible start-end pairs for each child
  ) %>%
  # we need to keep only 2-year observation pairs
  filter(wave_end == wave_start + 2) %>%
  select(-sex.y) %>%
  rename(sex = sex.x)
  # would otherwise be duplicate

cat("\nTotal 2-year transition pairs:", nrow(pairs), "including older kids at the end\n 
    and ", nrow(pairs_only_elem)," of total 2-year transition pairs including
    only elementary school children.")
cat("By transition:\n")
pairs %>%
  count(wave_start, wave_end, name = "n_pairs") %>%
  full_join(
    pairs_only_elem %>%
      count(wave_start, wave_end, name = "n_elem"),
    by = c("wave_start", "wave_end")
  ) %>%
  arrange(wave_start, wave_end)

## conclusion:
# I will leave it at pairs

############################ Compute BMI z-scores and classify weight categories
# using cdc.ref from childsds package
# BMI = weight_kg / height_m^2



calc_bmi_z <- function(wgt_lbs, hgt_in, age_months, sex) {
  bmi     <- (wgt_lbs * 0.453592) / ((hgt_in * 0.0254)^2)
  sex_chr <- ifelse(sex == 1, "male", "female")
  sds(bmi, age = age_months / 12, sex = sex_chr, item = "bmi", ref = cdc.ref)
  # stands for "standard deviation score"
}

classify_weight <- function(z) {
  # Cutoffs (CDC percentile-based referencing a ref pop)
  case_when(
    z <  -1.645 ~ "Underweight", # <5th percentile
    z <   1.036 ~ "Normal",      # 5th to < 85th percentile
    TRUE        ~ "Overweight"  # >= 85th percentile
  ) %>%
    factor(levels = c("Underweight", "Normal", "Overweight"))
}

pairs <- pairs %>%
  mutate(
    bmi_z_start = calc_bmi_z(wgt_start, hgt_start, age_start, sex),
    bmi_z_end   = calc_bmi_z(wgt_end,   hgt_end,   age_end,   sex),
    z_change    = bmi_z_end - bmi_z_start,
    weight_cat  = classify_weight(bmi_z_start),
    sex_label   = ifelse(sex == 1, "Boys", "Girls")
  ) %>%
  # to be on the safe side
  filter(is.finite(bmi_z_start), is.finite(bmi_z_end))

############################################################ Summary table
summary_tbl <- pairs %>%
  group_by(sex_label, weight_cat) %>%
  summarise(
    n            = n(),
    mean_z_start = mean(bmi_z_start, na.rm = TRUE),
    mean_z_end   = mean(bmi_z_end,   na.rm = TRUE),
    mean_change  = mean(z_change,    na.rm = TRUE),
    sd_change    = sd(z_change,      na.rm = TRUE),
    se_change    = sd_change / sqrt(n),
    ci_low       = mean_change - 1.96 * se_change,
    ci_high      = mean_change + 1.96 * se_change,
    .groups = "drop"
  )

summary_tbl %>% mutate(across(where(is.numeric), \(x) round(x, 2)))

############################################# Bar chart for overweight children
#   4th grade: 108-119 months (about 9 years)
#   5th grade: 120-131 months (about 10 years)

overweight_plot_data <- bind_rows(
  pairs %>%
    filter(weight_cat == "Overweight") %>%
    mutate(age_group = "Elementary school age"),
  pairs %>%
    filter(weight_cat == "Overweight", age_start >= 108, age_start <= 119) %>%
    mutate(age_group = "4th grade"),
  pairs %>%
    filter(weight_cat == "Overweight", age_start >= 120, age_start <= 131) %>%
    mutate(age_group = "5th grade")
) %>%
  mutate(
    age_group = factor(
      age_group,
      levels = c("Elementary school age", "4th grade", "5th grade")
    )
  ) %>%
  group_by(age_group, sex_label) %>%
  summarise(
    n = n(),
    bmi_z_start = mean(bmi_z_start, na.rm = TRUE),
    bmi_z_end = mean(bmi_z_end, na.rm = TRUE),
    .groups = "drop"
  )


overweight_plot_data_long <- bind_rows(
  overweight_plot_data %>%
    transmute(
      age_group,
      sex_label,
      n,
      timepoint = "Start",
      mean_bmi_z = bmi_z_start
    ),
  overweight_plot_data %>%
    transmute(
      age_group,
      sex_label,
      n,
      timepoint = "End",
      mean_bmi_z = bmi_z_end
    )
) %>%
  mutate(
    timepoint = factor(timepoint, levels = c("Start", "End")),
    sex_label = factor(sex_label, levels = c("Boys", "Girls"))
  )
overweight_plot <- ggplot(
  overweight_plot_data_long,
  aes(x = sex_label, y = mean_bmi_z, fill = timepoint)
) +
  geom_col(position = position_dodge(width = 0.7), width = 0.6) +
  geom_text(
    aes(label = round(mean_bmi_z, 2)),
    position = position_dodge(width = 0.7),
    vjust = -0.5,
    size = 3
  ) +
  geom_text(
    data = overweight_plot_data,
    aes(x = sex_label, y = -0.3, label = n),
    inherit.aes = FALSE,
    size = 3
  ) +
  annotate(
    "text",
    x = -Inf, 
    y = -0.3,
    label = "n",
    hjust = -0.2,
    size = 3
  )+
  facet_wrap(~ age_group, nrow = 1) +
  labs(
    x = NULL,
    y = "Mean BMI z-score",
    fill = NULL,
    title = "BMI z-scores at start and follow-up of 2 year observation period among overweight children"
    #caption = "Overweight is based on the first measurement (BMI z-score >= 85th percentile).\n4th and 5th grade are approximated from baseline age."
  ) +
  theme_minimal() +
  theme(legend.position = "bottom")
  

overweight_plot

dev.off()