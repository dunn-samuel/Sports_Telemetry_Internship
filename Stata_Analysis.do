
**************************************************************************
* RESEARCH INTERNSHIP: UK SPORTS VIEWERSHIP DATA COLLECTION AND ANALYSIS *
**************************************************************************

* Stata Do-File
* Intern: Samuel Dunn | Supervisor: Dr. Peter Dawson

* PART 1: DATA PREPARATION & PANEL SPECIFICATION *

* Import clean dataset
import excel "Cleaned_Dataset.xlsx", sheet("final_merged_internship_dataset") firstrow clear

* Encode categorical string variables
encode Sport, gen(sport_id)
encode Competition, gen(comp_id)
encode Day_of_Week, gen(day_id)
encode Stage, gen(stage_id)

* Generate unique match identifier for clustering standard errors
egen match_id = group(Date comp_id Home_Entity Away_Entity)

* Sort chronologically and generate sequential time identifier
sort match_id UK_Time
bysort match_id: gen time_id = _n

* Declare panel structure (Match ID = panel, Time ID = sequence)
xtset match_id time_id

* PART 2: DESCRIPTIVE & SUMMARY STATISTICS *

* Summary statistics for continuous and dummy variables
estpost summarize Viewer_Count Log_Viewer_Count UOH_Score UK_Involved Is_Televised
esttab using "Summary_Statistics.rtf", replace ///
    cells("count mean(fmt(2)) sd(fmt(2)) min(fmt(2)) max(fmt(2))") ///
    title("Table 1: Summary Statistics of UK Audience Demand") ///
    nomtitle nonumber label

* Decompose variance into between-match and within-match variation
xtsum Viewer_Count Log_Viewer_Count UOH_Score UK_Involved Is_Televised

* Average viewers by sport
estpost tabstat Viewer_Count, by(Sport) statistics(mean count) columns(statistics)
esttab using "Descriptive_Tables.rtf", replace ///
    cells("mean(fmt(0) label(Mean Viewers)) count(fmt(0) label(Observations))") ///
    title("Descriptive Table 1a: Average Viewer Count by Sport") ///
    nomtitle nonumber label

* Average viewers by UK involvement
estpost tabstat Viewer_Count, by(UK_Involved) statistics(mean count) columns(statistics)
esttab using "Descriptive_Tables.rtf", append ///
    cells("mean(fmt(0) label(Mean Viewers)) count(fmt(0) label(Observations))") ///
    title("Descriptive Table 1b: Average Viewer Count by UK Involvement") ///
    nomtitle nonumber label

* Dataset composition by competition
estpost tabulate Competition
esttab using "Descriptive_Tables.rtf", append ///
    cells("b(label(Freq.)) pct(label(%) fmt(2))") ///
    title("Descriptive Table 2: Snapshot Distribution by Competition") ///
    nomtitle nonumber label

* PART 3: VISUALISATIONS *

* Figure 4.1: Audience variation by UK involvement across sports
graph bar (mean) Viewer_Count, ///
    over(UK_Involved, relabel(1 "Non-UK" 2 "UK Involved")) ///
    over(Sport, label(labsize(small))) ///
    asyvars ///
    title("Audience Demand: UK vs Non-UK Involvement by Sport") ///
    ytitle("Mean Viewers") ///
    legend(order(1 "Non-UK" 2 "UK Involved") rows(1) position(6)) ///
    blabel(bar, format(%9.0fc) size(vsmall)) ///
    scheme(s2color)
graph export "Audience_UK_Involved.png", replace as(png) width(1200)

* Figure 4.4: Intra-match audience retention timeline
tostring Game_Time, replace
gen match_phase = .
replace match_phase = 3 if Game_Time == "HT"
replace match_phase = 6 if Game_Time == "FT"
replace match_phase = 7 if strpos(Game_Time, "ET") > 0
replace match_phase = 2 if strpos(Game_Time, "45+") > 0
replace match_phase = 5 if strpos(Game_Time, "90+") > 0

gen clock_num = real(Game_Time)
replace match_phase = 1 if clock_num >= 0  & clock_num <= 23 & match_phase == .
replace match_phase = 2 if clock_num >= 24 & clock_num <= 45 & match_phase == .
replace match_phase = 4 if clock_num >= 46 & clock_num <= 68 & match_phase == .
replace match_phase = 5 if clock_num >= 69 & clock_num <= 90 & match_phase == .

label define phase_lbl 1 "0-23 mins" 2 "24-45+ mins" 3 "Half Time" 4 "46-68 mins" 5 "69-90+ mins" 6 "Full Time" 7 "Extra Time & Penalties"
label values match_phase phase_lbl

preserve
drop if match_phase == .
collapse (mean) Viewer_Count, by(match_phase)
twoway (connected Viewer_Count match_phase, lwidth(thick) msize(large) mcolor(navy) lcolor(navy)), ///
    title("Audience Retention by Match Time") ///
    ytitle("Mean Viewers") ///
    xtitle("Match Phase") ///
    xlabel(1 2 3 4 5 6 7, valuelabel angle(30)) ///
    scheme(s2color)
graph export "Audience_True_Timeline.png", replace as(png) width(1200)
restore

* Figure 4.3: Audience demand by competition stage
gen macro_stage = "Other"
replace macro_stage = "Finals" if strpos(Stage, "Final") > 0 | strpos(Stage, "3rd Place") > 0 | strpos(Stage, "Grand Prix") > 0
replace macro_stage = "Late Knockouts" if strpos(Stage, "Semi") > 0 | strpos(Stage, "Quarter") > 0
replace macro_stage = "Early Knockouts" if strpos(Stage, "RO16") > 0 | strpos(Stage, "RO32") > 0 | strpos(Stage, "Round of 16") > 0 | strpos(Stage, "Fourth Round") > 0
replace macro_stage = "Early Tournament" if strpos(Stage, "Group") > 0 | strpos(Stage, "Day") > 0 | strpos(Stage, "Round 1") > 0 | strpos(Stage, "Round 2") > 0
replace macro_stage = "Qualifying/Practice" if strpos(Stage, "Qualifying") > 0 | strpos(Stage, "Practice") > 0
encode macro_stage, gen(macro_stage_id)

graph bar (mean) Viewer_Count, ///
    over(macro_stage, sort(1) descending label(angle(30) labsize(small))) ///
    title("Average UK Audience Demand by Stage of Competition") ///
    ytitle("Mean Viewers") ///
    blabel(bar, format(%9.0fc) size(vsmall)) ///
    scheme(s2color)
graph export "Audience_By_Stage.png", replace as(png) width(1200)

* Figure 4.2: 24-hour broadcast distribution
preserve
capture confirm string variable UK_Time
if _rc == 0 {
    gen hour = real(substr(UK_Time, 1, 2))
}
else {
    gen hour = hh(UK_Time)
}
drop if missing(hour)
collapse (mean) Viewer_Count, by(hour)

twoway (bar Viewer_Count hour, barwidth(0.7) fcolor(navy) lcolor(navy)), ///
    title("Average UK Audience Demand by Time of Day") ///
    ytitle("Mean Viewers") ///
    xtitle("Hour of Day (UK Time)") ///
    xlabel(0(2)23, valuelabel) ///
    xscale(range(0 23)) ///
    scheme(s2color)
graph export "Audience_By_Time_OfDay.png", replace as(png) width(1200)
restore

* PART 4: REGRESSION ANALYSIS *

* Model 1: Baseline Pooled OLS
eststo m1: reg Log_Viewer_Count UK_Involved UOH_Score i.sport_id i.day_id, vce(robust)

* Model 2: Pooled OLS with clustered standard errors
eststo m2: reg Log_Viewer_Count UK_Involved UOH_Score i.sport_id i.day_id, vce(cluster match_id)

* Model 3: Random Effects panel model
eststo m3: xtreg Log_Viewer_Count UK_Involved UOH_Score i.day_id, re vce(cluster match_id)

* Model 4: Random Effects with time-interval fixed effects (Preferred baseline)
eststo m4: xtreg Log_Viewer_Count UK_Involved UOH_Score i.day_id i.time_id, re vce(cluster match_id)

* Model 5: Interaction model (UK Involved x UOH Score)
eststo m5: xtreg Log_Viewer_Count c.UOH_Score##i.UK_Involved i.day_id i.time_id, re vce(cluster match_id)

* PART 5: POST-ESTIMATION TESTS & TABLES *

* Breusch-Pagan LM test for Random Effects
quietly xtreg Log_Viewer_Count UK_Involved UOH_Score i.day_id, re
xttest0

* Export baseline regression results to RTF
esttab m1 m2 m3 m4 m5 using "Regression_Results.rtf", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    title("Table 2: Regression Analysis of Audience Demand") ///
    mtitle("Pooled OLS" "OLS (Clustered)" "Random Effects" "RE (Time Controls)" "RE (Interaction)") ///
    addnotes("Standard errors in parentheses. Models 2 to 5 clustered at the event level.")

* PART 6: MODEL EXTENSIONS (M6 & M7) *

* Model 6: Sub-sample heterogeneity (Sport interaction & star quality in H2H sports)
eststo m6: xtreg Log_Viewer_Count i.UK_Involved##i.sport_id Top_6 UOH_Score i.day_id i.time_id ///
    if inlist(Sport, "Football", "Rugby", "Tennis"), re vce(cluster match_id)

* Model 7: Quadratic non-linear UOH model
eststo m7: xtreg Log_Viewer_Count UK_Involved c.UOH_Score##c.UOH_Score i.day_id i.time_id, re vce(cluster match_id)

* Append extension models to results table
esttab m6 m7 using "Regression_Results.rtf", append ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    title("Table 4: Heterogeneity, Quality of Play, and Non-Linearity") ///
    mtitle("Sport*UK & Stars" "Quadratic UOH") ///
    addnotes("Standard errors clustered at the event level. M6 restricted to discrete H2H sports.")

* PART 7: POST-ESTIMATION VISUALISATIONS *

* Figure 4.6: Predictive margins plot for non-linear UOH (Model 7)
quietly xtreg Log_Viewer_Count UK_Involved c.UOH_Score##c.UOH_Score i.day_id i.time_id, re
quietly margins, at(UOH_Score=(0.1(0.1)1))
marginsplot, ///
    title("Predictive Margins: The UOH Curve") ///
    ytitle("Expected UK Audience (Log Viewers)") ///
    xtitle("Pre-Match UOH Score (Uncertainty)") ///
    plotopts(lwidth(thick) msize(large) mcolor(navy) lcolor(navy)) ///
    ciopts(lcolor(gs10)) scheme(s2color)
graph export "UOH_Margins_Plot.png", replace as(png) width(1200)

* Figure 4.5: Standardized coefficient plot (Model 4)
capture ssc install coefplot
quietly egen z_Log_Viewer_Count = std(Log_Viewer_Count)
quietly egen z_UK_Involved = std(UK_Involved)
quietly egen z_UOH_Score = std(UOH_Score)
quietly xtreg z_Log_Viewer_Count z_UK_Involved z_UOH_Score i.day_id i.time_id, re vce(cluster match_id)

coefplot, drop(_cons *.day_id *.time_id) ///
    xline(0, lpattern(dash) lcolor(gs8)) ///
    title("Standardized Marginal Effects" "on UK Audience Demand", size(medium)) ///
    subtitle("Effect Sizes in Standard Deviations", size(small)) ///
    coeflabels(z_UK_Involved = "UK Athlete/Team Involved" z_UOH_Score = "Uncertainty of Outcome") ///
    msymbol(S) msize(large) mcolor(navy) ciopts(lcolor(navy) lwidth(thick)) ///
    scheme(s2color) graphregion(margin(medium))
graph export "Coefficient_Plot.png", replace as(png) width(1200)

* PART 8: ROBUSTNESS & SENSITIVITY CHECKS *

* Hausman Specification Test (FE vs. RE)
quietly xtreg Log_Viewer_Count UOH_Score i.day_id i.time_id, fe
estimates store fixed_model
quietly xtreg Log_Viewer_Count UOH_Score i.day_id i.time_id, re
estimates store random_model
hausman fixed_model random_model
	
* Football Exclusion 
eststo rob_nofootball: xtreg Log_Viewer_Count UK_Involved UOH_Score i.day_id i.time_id ///
    if Sport != "Football", re vce(cluster match_id)

* Weekend vs. Weekday Sub-Samples
gen is_weekend = (Day_of_Week == "Saturday" | Day_of_Week == "Sunday")
eststo rob_weekend: xtreg Log_Viewer_Count c.UOH_Score##i.is_weekend UK_Involved i.time_id, ///
    re vce(cluster match_id)
	
* Graduated Outlier Trimming (Threshold Invariance)
* Calculate the 99th, 95th, and 90th percentiles for viewer count
quietly summarize Viewer_Count, detail
global p99 = r(p99)
global p95 = r(p95)

eststo excl_1pct: xtreg Log_Viewer_Count UK_Involved UOH_Score i.day_id i.time_id ///
    if Viewer_Count < $p99, re vce(cluster match_id)

eststo excl_5pct: xtreg Log_Viewer_Count UK_Involved UOH_Score i.day_id i.time_id ///
    if Viewer_Count < $p95, re vce(cluster match_id)

* The Placebo Refutation Test (UOH)
set seed 999
bysort match_id: gen placebo_UOH = rnormal(0, 1) if _n == 1
bysort match_id: replace placebo_UOH = placebo_UOH[1]

eststo placebo_test: xtreg Log_Viewer_Count UK_Involved placebo_UOH i.day_id i.time_id, re vce(cluster match_id)

* Export Robustness and Refutation Table
esttab excl_1pct excl_5pct placebo_test rob_nofootball rob_weekend using "Robustness_And_Refutation.rtf", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) ///
    title("Table A.3: Robustness and Placebo Refutation Checks") ///
    mtitle("Excl. Top 1%" "Excl. Top 5%" "Placebo UOH" "Excl. Football" "Weekend Interaction") ///
    addnotes("Standard errors clustered at the event level. The Placebo model utilizes randomly shuffled UOH scores. Hausman test results detailed in text.")
