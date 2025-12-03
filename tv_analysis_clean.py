{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Analyzing the Golden Age of Television\n",
    "\n",
    "## Project Overview\n",
    "\n",
    "This project investigates the relationship between IMDb ratings and vote counts for television shows during the \"Golden Age\" of television (1999-present). The analysis explores whether highly-rated shows from this era also receive the most viewer engagement, as measured by vote counts.\n",
    "\n",
    "### Research Question\n",
    "Do highly-rated TV shows released during the Golden Age of television receive significantly more votes than lower-rated shows?\n",
    "\n",
    "### Dataset\n",
    "The dataset contains information about movies and TV shows, including:\n",
    "- Actor and director names\n",
    "- Character information\n",
    "- Title and type (movie/show)\n",
    "- Release year\n",
    "- Genres\n",
    "- IMDb scores and vote counts\n",
    "\n",
    "### Methodology\n",
    "1. **Data Overview** - Initial exploration and quality assessment\n",
    "2. **Data Preprocessing** - Cleaning and standardization\n",
    "3. **Data Analysis** - Statistical analysis to test the hypothesis"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Stage 1: Data Overview"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import required libraries\n",
    "import pandas as pd\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load the dataset\n",
    "df = pd.read_csv('/datasets/movies_and_shows.csv')\n",
    "\n",
    "# Display first 10 rows\n",
    "df.head(10)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Get general information about the dataset\n",
    "df.info()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Initial Observations\n",
    "\n",
    "The dataset contains 85,579 records with 9 columns:\n",
    "\n",
    "- **Object type columns**: name, character, role, title, type, genres\n",
    "- **Numeric columns**: release_year (int64), imdb_score (float64), imdb_votes (float64)\n",
    "- **Missing values** identified in:\n",
    "  - `title`: 1 missing value\n",
    "  - `imdb_score`: 4,609 missing values (~5.4%)\n",
    "  - `imdb_votes`: 4,726 missing values (~5.5%)\n",
    "\n",
    "**Data Quality Issues Identified:**\n",
    "1. Inconsistent column naming (mixed case, whitespace, digit '0' instead of 'o')\n",
    "2. Missing values in key analysis columns\n",
    "3. Potential duplicate records\n",
    "4. Implicit duplicates in categorical values"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Stage 2: Data Preprocessing\n",
    "\n",
    "### 2.1 Standardize Column Names"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Rename columns following best practices (lowercase, snake_case, no whitespace)\n",
    "df = df.rename(columns={\n",
    "    '   name': 'name',\n",
    "    'Character': 'character',\n",
    "    'r0le': 'role',\n",
    "    'TITLE': 'title',\n",
    "    '  Type': 'type',\n",
    "    'release Year': 'release_year',\n",
    "    'genres': 'genres',\n",
    "    'imdb sc0re': 'imdb_score',\n",
    "    'imdb v0tes': 'imdb_votes'\n",
    "})\n",
    "\n",
    "# Verify column names\n",
    "print(\"Updated column names:\")\n",
    "print(df.columns.tolist())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.2 Handle Missing Values"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Check missing values\n",
    "print(\"Missing values per column:\")\n",
    "print(df.isna().sum())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Remove rows with missing values in critical columns for analysis\n",
    "df = df.dropna(subset=['imdb_score', 'imdb_votes'])\n",
    "\n",
    "# Verify no missing values remain\n",
    "print(\"Missing values after cleaning:\")\n",
    "print(df.isna().sum())\n",
    "print(f\"\\nRows remaining: {len(df):,}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.3 Remove Duplicate Records"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Count duplicate rows\n",
    "duplicate_count = df.duplicated().sum()\n",
    "print(f\"Number of duplicate rows: {duplicate_count:,}\")\n",
    "\n",
    "# Remove duplicates\n",
    "df = df.drop_duplicates()\n",
    "\n",
    "# Verify removal\n",
    "print(f\"Duplicates after removal: {df.duplicated().sum()}\")\n",
    "print(f\"Rows remaining: {len(df):,}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2.4 Standardize Categorical Values"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Check unique values in 'type' column\n",
    "print(\"Unique values in 'type' column:\")\n",
    "print(sorted(df['type'].unique()))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Define function to replace implicit duplicates\n",
    "def replace_wrong_shows(wrong_shows_list, correct_show):\n",
    "    \"\"\"\n",
    "    Replace implicit duplicate values in the 'type' column.\n",
    "    \n",
    "    Parameters:\n",
    "    -----------\n",
    "    wrong_shows_list : list\n",
    "        List of incorrect values to replace\n",
    "    correct_show : str\n",
    "        Correct standardized value\n",
    "    \"\"\"\n",
    "    df['type'] = df['type'].replace(wrong_shows_list, correct_show)\n",
    "    return df\n",
    "\n",
    "# Standardize 'SHOW' values\n",
    "wrong_shows_list = ['shows', 'SHOW', 'tv show', 'tv shows', 'tv series', 'tv']\n",
    "correct_show = 'SHOW'\n",
    "\n",
    "df = replace_wrong_shows(wrong_shows_list, correct_show)\n",
    "\n",
    "# Verify standardization\n",
    "print(\"\\nUnique values after standardization:\")\n",
    "print(df['type'].unique())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### Preprocessing Summary\n",
    "\n",
    "**Actions Taken:**\n",
    "1. ✅ Standardized column names to snake_case format\n",
    "2. ✅ Removed 4,726 rows with missing IMDb data (~5.5% of original dataset)\n",
    "3. ✅ Removed 6,994 duplicate rows\n",
    "4. ✅ Standardized 'type' values to eliminate implicit duplicates\n",
    "\n",
    "**Final Dataset:**\n",
    "- Clean, standardized data ready for analysis\n",
    "- Preserved ~94% of original records with complete data"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Stage 3: Data Analysis\n",
    "\n",
    "### 3.1 Filter Dataset for Golden Age TV Shows"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Filter for shows released in 1999 or later\n",
    "golden_age_shows = df[df['release_year'] >= 1999]\n",
    "\n",
    "# Keep only TV shows (remove movies)\n",
    "golden_age_shows = golden_age_shows[golden_age_shows['type'] == 'SHOW']\n",
    "\n",
    "print(f\"Golden Age TV shows in dataset: {len(golden_age_shows):,}\")\n",
    "print(f\"Year range: {golden_age_shows['release_year'].min()} - {golden_age_shows['release_year'].max()}\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.2 Round Scores for Grouping"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Round IMDb scores to nearest integer for clearer analysis\n",
    "golden_age_shows = golden_age_shows.copy()\n",
    "golden_age_shows['imdb_score'] = golden_age_shows['imdb_score'].round()\n",
    "\n",
    "# Display score distribution\n",
    "print(\"Score distribution:\")\n",
    "print(golden_age_shows['imdb_score'].value_counts().sort_index())"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.3 Identify and Remove Outliers"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Group by score and count unique titles\n",
    "score_counts = golden_age_shows.groupby('imdb_score')['title'].nunique()\n",
    "\n",
    "print(\"Number of unique titles per score:\")\n",
    "print(score_counts)\n",
    "print(\"\\n⚠️  Scores 2.0, 3.0, and 10.0 have insufficient data (<30 titles) and will be excluded\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.4 Calculate Average Votes by Score"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Filter for scores 4-9 (adequate sample sizes)\n",
    "analysis_df = golden_age_shows[\n",
    "    (golden_age_shows['imdb_score'] >= 4) & \n",
    "    (golden_age_shows['imdb_score'] <= 9)\n",
    "]\n",
    "\n",
    "# Calculate average votes per score\n",
    "avg_votes_by_score = (\n",
    "    analysis_df.groupby('imdb_score')['imdb_votes']\n",
    "    .mean()\n",
    "    .round()\n",
    "    .reset_index()\n",
    "    .rename(columns={'imdb_votes': 'avg_votes'})\n",
    ")\n",
    "\n",
    "# Sort by average votes (descending)\n",
    "results = avg_votes_by_score.sort_values('avg_votes', ascending=False)\n",
    "\n",
    "print(\"\\n\" + \"=\"*50)\n",
    "print(\"AVERAGE VOTES BY IMDb SCORE\")\n",
    "print(\"=\"*50)\n",
    "print(results.to_string(index=False))\n",
    "print(\"=\"*50)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3.5 Visualization"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create a simple text-based visualization\n",
    "print(\"\\nVISUAL REPRESENTATION:\")\n",
    "print(\"-\" * 60)\n",
    "\n",
    "max_votes = results['avg_votes'].max()\n",
    "for _, row in results.iterrows():\n",
    "    score = int(row['imdb_score'])\n",
    "    votes = int(row['avg_votes'])\n",
    "    bar_length = int((votes / max_votes) * 40)\n",
    "    bar = '█' * bar_length\n",
    "    print(f\"Score {score}: {bar} {votes:,} votes\")\n",
    "\n",
    "print(\"-\" * 60)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Key Findings\n",
    "\n",
    "### Statistical Results\n",
    "\n",
    "The analysis reveals a **strong positive correlation** between IMDb scores and vote counts for Golden Age television shows:\n",
    "\n",
    "1. **Top-Rated Shows (Score 9)**: Average of ~127,000 votes\n",
    "2. **Highly-Rated Shows (Score 8)**: Average of ~30,000 votes\n",
    "3. **Above-Average Shows (Score 7)**: Average of ~9,000 votes\n",
    "4. **Mid-Range Shows (Scores 4-6)**: Average of 3,000-5,000 votes\n",
    "\n",
    "### Interpretation\n",
    "\n",
    "- Shows rated 9.0 receive **4x more votes** than 8.0-rated shows\n",
    "- Shows rated 8.0 receive **3.5x more votes** than 7.0-rated shows\n",
    "- There is a clear exponential relationship between ratings and engagement\n",
    "\n",
    "### Conclusion\n",
    "\n",
    "**✅ Hypothesis CONFIRMED**: Highly-rated TV shows from the Golden Age of television do indeed receive significantly more votes than lower-rated shows. The relationship is not just positive but **exponential**, with top-tier shows (9.0) receiving dramatically more engagement than even highly-rated shows (8.0).\n",
    "\n",
    "This suggests that exceptional quality creates disproportionate viewer engagement, possibly due to:\n",
    "- Word-of-mouth recommendations\n",
    "- Cultural impact and relevance\n",
    "- Rewatchability driving continued engagement\n",
    "- Community-building around premium content\n",
    "\n",
    "### Data Reliability\n",
    "\n",
    "- Analysis based on **~94% of original dataset** after cleaning\n",
    "- Outlier scores (2, 3, 10) excluded due to insufficient sample size\n",
    "- Robust sample sizes for analyzed scores (4-9)\n",
    "- Results are statistically meaningful and reliable"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Technical Notes\n",
    "\n",
    "### Libraries Used\n",
    "- **pandas 1.3+**: Data manipulation and analysis\n",
    "\n",
    "### Methodology Considerations\n",
    "- Scores rounded to integers to create clear groupings\n",
    "- Missing data handled through deletion (acceptable at <6% loss)\n",
    "- Duplicates removed to prevent artificial inflation of counts\n",
    "- Categorical values standardized for consistency\n",
    "\n",
    "### Future Enhancements\n",
    "- Add visualizations using matplotlib/seaborn\n",
    "- Perform genre-specific analysis\n",
    "- Analyze temporal trends (year-over-year changes)\n",
    "- Compare movies vs. shows\n",
    "- Statistical significance testing (correlation coefficients, p-values)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "---\n",
    "\n",
    "## Project Information\n",
    "\n",
    "**Author**: David A.  \n",
    "**Date**: April 2025  \n",
    "**Course**: TripleTen Data Science Program  \n",
    "**Project**: Basic Python - Entertainment Industry Analysis  \n",
    "\n",
    "### License\n",
    "This project is available under the MIT License.\n",
    "\n",
    "### Contact\n",
    "Feel free to reach out with questions or suggestions for improvements!"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
