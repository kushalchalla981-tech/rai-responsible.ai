# Sample Datasets for RAI Audit Platform

This directory contains sample datasets designed to test the Responsible AI Audit Platform's fairness and bias detection capabilities.

## Available Datasets

### 1. Hiring Dataset (`hiring_dataset.csv`)
**Domain:** Hiring / Employment
**Rows:** 150
**Columns:** 6

**Features:**
- `age`: Applicant age (26-50)
- `gender`: Male/Female
- `experience_years`: Years of work experience (1-20)
- `education_level`: Bachelor, Master, PhD
- `previous_company`: Previous employer (Company A-Z)
- `hired`: Binary outcome (0=Not Hired, 1=Hired)

**Protected Attributes for Testing:**
- `gender`: Test for gender bias in hiring decisions
- `age`: Test for age discrimination

**Target Attribute:**
- `hired`: The hiring decision

**Usage Example:**
```
Mode: Direct
Domain: Hiring
Target Attribute: hired
Protected Attributes: gender, age
```

---

### 2. Lending Dataset (`lending_dataset.csv`)
**Domain:** Lending / Financial Services
**Rows:** 100
**Columns:** 10

**Features:**
- `applicant_id`: Unique identifier
- `age`: Applicant age (26-50)
- `income`: Annual income ($40,000 - $150,000)
- `credit_score`: Credit score (650-835)
- `debt_to_income`: Debt-to-income ratio (0.10-0.48)
- `employment_years`: Years employed (1-21)
- `home_ownership`: Owner/Renter
- `loan_amount`: Requested loan amount ($7,000 - $80,000)
- `loan_purpose`: Debt Consolidation, Home Improvement, Medical, Education
- `approved`: Binary outcome (0=Rejected, 1=Approved)

**Protected Attributes for Testing:**
- `age`: Test for age-based lending discrimination
- `home_ownership`: Test for housing status bias

**Target Attribute:**
- `approved`: Loan approval decision

**Usage Example:**
```
Mode: Direct
Domain: Lending
Target Attribute: approved
Protected Attributes: age, home_ownership
```

---

### 3. Healthcare Dataset (`healthcare_dataset.csv`)
**Domain:** Healthcare
**Rows:** 100
**Columns:** 11

**Features:**
- `patient_id`: Unique identifier
- `age`: Patient age (26-50)
- `gender`: Male/Female
- `race`: White, Black, Hispanic
- `insurance_type`: Private, Medicaid, Medicare
- `income_level`: High, Medium, Low
- `education`: College, High School
- `comorbidities`: Number of comorbid conditions (0-2)
- `treatment_recommended`: Recommended treatment (0/1)
- `treatment_received`: Actual treatment received (0/1)
- `readmitted_30_days`: Readmission within 30 days (0/1)

**Protected Attributes for Testing:**
- `gender`: Test for gender bias in treatment
- `race`: Test for racial disparities in healthcare
- `insurance_type`: Test for insurance-based discrimination
- `income_level`: Test for socioeconomic bias

**Target Attributes:**
- `treatment_received`: Whether treatment was actually provided
- `readmitted_30_days`: Patient readmission outcome

**Usage Example:**
```
Mode: Direct
Domain: Healthcare
Target Attribute: treatment_received
Protected Attributes: race, gender, insurance_type
```

---

## How to Use These Datasets

### Step 1: Start the Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Start the Frontend
```bash
cd frontend
npm run dev
```

### Step 3: Upload a Dataset
1. Open http://localhost:3000 in your browser
2. Click "Upload Dataset" button
3. Select one of the CSV files from this directory
4. Wait for upload to complete

### Step 4: Configure and Run an Audit
1. Select the uploaded dataset from the list
2. Configure audit parameters:
   - **Audit Mode**: Direct (recommended for these datasets)
   - **Domain**: Choose appropriate domain (Hiring, Lending, Healthcare)
   - **Target Attribute**: Select the outcome column
   - **Protected Attributes**: Select attributes to test for bias
   - **Confidence Threshold**: 0.9 (default)
3. Click "Run Audit"

### Step 5: Review Results
- View metrics and findings in the results panel
- Check for bias indicators (red = at risk, green = safe)
- Review subgroup breakdowns for detailed analysis

---

## Testing Scenarios

### Scenario 1: Gender Bias in Hiring
```
Dataset: hiring_dataset.csv
Mode: Direct
Domain: Hiring
Target: hired
Protected: gender
Expected: May show demographic parity differences
```

### Scenario 2: Age Discrimination in Lending
```
Dataset: lending_dataset.csv
Mode: Direct
Domain: Lending
Target: approved
Protected: age
Expected: May show bias against older/younger applicants
```

### Scenario 3: Racial Disparities in Healthcare
```
Dataset: healthcare_dataset.csv
Mode: Direct
Domain: Healthcare
Target: treatment_received
Protected: race
Expected: May show unequal treatment across racial groups
```

### Scenario 4: Proxy Detection
```
Dataset: Any dataset
Mode: Proxy
Target: Any outcome
Protected: Any protected attribute
Expected: Detect features that correlate with protected attributes
```

---

## Dataset Characteristics

### Data Quality
- All datasets have 100+ rows (minimum requirement for audits)
- No missing values
- Consistent data types
- Realistic value ranges

### Bias Patterns
These datasets are designed with intentional patterns to demonstrate:
- **Demographic Parity Differences**: Different selection rates across groups
- **Equal Opportunity Issues**: Different true positive rates
- **Proxy Correlations**: Features that may indirectly encode protected attributes

### Limitations
- Synthetic data for demonstration purposes
- Simplified scenarios compared to real-world complexity
- May not reflect actual bias patterns in production systems

---

## Creating Your Own Datasets

To create custom datasets for testing:

1. **Format**: CSV file with header row
2. **Minimum Size**: 100 rows
3. **Required Columns**:
   - At least one target attribute (binary or continuous)
   - At least one protected attribute (categorical)
   - Additional features for analysis

4. **Example Structure**:
```csv
feature1,feature2,protected_attribute,target_attribute
value1,value2,group_A,1
value3,value4,group_B,0
...
```

5. **Upload**: Use the platform's upload interface

---

## Troubleshooting

### Upload Errors
- Ensure file is in CSV format
- Check minimum 100 rows requirement
- Verify no missing values in critical columns
- Check file encoding (UTF-8 recommended)

### Audit Errors
- Ensure target attribute exists in dataset
- Verify protected attributes are categorical
- Check confidence threshold is between 0.0 and 1.0
- Confirm dataset has sufficient samples per group

### No Results
- Try different audit modes (Direct, Proxy, Limited)
- Adjust confidence threshold
- Check if protected attribute has sufficient variation
- Verify target attribute has both positive and negative values

---

## Additional Resources

- [Platform Documentation](../frontend/README.md)
- [Backend API Documentation](../backend/README.md)
- [Fairness Metrics Guide](https://fairlearn.org/main/user_guide/fairness.html)
- [AI Ethics Resources](https://www.microsoft.com/en-us/ai/ai-principles)

---

## License

These sample datasets are provided for testing and educational purposes as part of the RAI Audit Platform.