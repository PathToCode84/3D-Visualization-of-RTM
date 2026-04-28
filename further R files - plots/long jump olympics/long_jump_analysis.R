rm(list=ls())
setwd("/Users/mia8425/Documents/Studium/6. Semester SS 2026/SE Seminar/further R files - plots/long jump olympics")

data = read.csv("Combined_Olympics_Long_Jump_Results.csv")
head(data)


data$Jump_1_Final[data$Jump_1_Final == "x"] <- NA
data$Jump_1_Final <- as.numeric(data$Jump_1_Final)

data$Jump_2_Final[data$Jump_2_Final == "x"] <- NA
data$Jump_2_Final <- as.numeric(data$Jump_2_Final)

# select extreme results on jump 1
data$extreme = ifelse(data$Jump_1_Final > 7.9, TRUE, FALSE)

mean(data$Jump_1_Final[ data$extreme ],na.rm = TRUE)
mean(data$Jump_2_Final[ data$extreme ],na.rm = TRUE)
