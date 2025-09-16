# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

请使用中文和用户交互。

## Repository Overview

This is a Python-based performance evaluation system for development teams, designed to analyze team member performance across three key metrics: overdue ratios, overdue days, and work days. The system processes structured data files and generates comprehensive scoring reports with detailed analysis.

## Core Architecture

### Main Components

- **DataParser**: Handles parsing of three distinct data file formats
- **ScoringCalculator**: Implements the weighted scoring algorithm with configurable parameters
- **DataProcessor**: Orchestrates the complete analysis workflow
- **ScoringConfig**: Centralized configuration for all scoring parameters and thresholds

### Data Processing Flow

1. Parse three data files (overdue.data, mean_overdue.data, days.data)
2. Validate data integrity and cross-reference employee names
3. Calculate individual scores for each metric
4. Compute weighted comprehensive scores
5. Assign performance grades (S/A/B/C/D)
6. Generate statistical analysis and improvement recommendations

### Scoring Algorithm

The system uses a weighted scoring approach:
- **Overdue Ratio**: 40% weight (baseline: 20%, penalty: 2 points per %)
- **Overdue Days**: 40% weight (baseline: 2 days, penalty: 15 points per day)
- **Work Days**: 20% weight (optimized for "more is better" philosophy)

Work days scoring follows a tiered approach:
- 8-10 person-days: Full score (100 points)
- 10-15 person-days: Bonus tier 1 (+2 points per day)
- >15 person-days: Bonus tier 2 (+1 point per day, max 120 points)
- <8 person-days: Penalty (-10 points per missing day)

## Development Commands

### Running the Scoring System

Basic usage:
```bash
python3 scoring.py --overdue overdue.data --mean-overdue mean_overdue.data --days days.data
```

With detailed analysis:
```bash
python3 scoring.py --overdue overdue.data --mean-overdue mean_overdue.data --days days.data --detailed
```

Export results to CSV:
```bash
python3 scoring.py --overdue overdue.data --mean-overdue mean_overdue.data --days days.data --output results.csv
```

Show scoring explanations:
```bash
python3 scoring.py --overdue overdue.data --mean-overdue mean_overdue.data --days days.data --explain
```

### Data File Formats

**overdue.data**: Groups of 3 lines per employee
```
Employee Name
Percentage%
Median Value
```

**mean_overdue.data**: Groups of 3 lines per employee
```
Employee Name
Days (float)
Median Value
```

**days.data**: Groups of 3 lines per employee
```
Employee Name
Work Days (float)
Work Days Median
```

## Configuration Management

### Key Parameters in ScoringConfig

- **Grade Thresholds**: S≥85, A≥70, B≥55, C≥40, D<40
- **Overdue Ratio Baseline**: 20% (performance standard)
- **Overdue Days Baseline**: 2 days (performance standard)
- **Work Days Ideal Range**: 8-10 person-days
- **Review Threshold**: >15 person-days (requires verification)

### Modifying Scoring Logic

To adjust scoring parameters, modify the `ScoringConfig` class:
- `weights`: Change metric importance
- `*_params`: Adjust baselines, multipliers, and scoring ranges
- `grade_thresholds`: Modify performance level cutoffs

## Data Validation

The system performs comprehensive data validation:
- Ensures all three datasets contain overlapping employee names
- Validates data ranges (overdue ratios 0-100%, non-negative values)
- Cross-references employee presence across all datasets
- Reports data integrity issues before processing

## Output and Reporting

### Standard Output Includes:
- Ranked employee performance table
- Top 3 and Bottom 3 performers
- Grade distribution statistics
- Flags for employees requiring record verification

### Detailed Analysis Provides:
- Performance breakdown by metric
- Team-wide statistical analysis
- Improvement recommendations
- Identification of data anomalies

## Best Practices

### Data Preparation
- Ensure consistent employee name formatting across all data files
- Validate data completeness before running analysis
- Review high person-day entries (>15) for accuracy

### Analysis Interpretation
- S-grade employees are Highlight candidates
- D-grade employees require attention and support
- High person-day scores may indicate recording inconsistencies
- Use explanation output to understand individual performance factors

### Code Maintenance
- All scoring parameters are centralized in `ScoringConfig`
- The system is designed for extensibility with additional metrics
- Data parsing supports flexible file formats within the established structure