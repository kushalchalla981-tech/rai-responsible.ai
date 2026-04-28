import pandas as pd
import numpy as np
import os

np.random.seed(42)  # Reproducible realistic distributions

def generate_hiring(num_rows=2500):
    """Hiring dataset mimicking US private sector hiring patterns (EEOC 2024 data)"""
    data = {
        "applicant_id": range(1, num_rows + 1),
        "age": np.random.randint(18, 67, num_rows),
        "gender": np.random.choice(
            ["Male", "Female", "Non-binary"], 
            num_rows, 
            p=[0.47, 0.49, 0.04]
        ),
        "race": np.random.choice(
            ["White", "Black", "Hispanic", "Asian", "Other"],
            num_rows,
            p=[0.58, 0.12, 0.19, 0.06, 0.05]  # US Census 2024
        ),
        "education": np.random.choice(
            ["High School", "Bachelor", "Master", "PhD"],
            num_rows,
            p=[0.32, 0.42, 0.20, 0.06]
        )
    }
    df = pd.DataFrame(data)
    # Realistic bias: White applicants 22% more likely to be hired, Female 8% less
    df["hired"] = df.apply(
        lambda r: 1 if np.random.rand() < (
            0.52  # Base hire rate
            + (0.22 if r["race"] == "White" else 0)
            - (0.08 if r["gender"] == "Female" else 0)
            + (0.15 if r["education"] in ["Master", "PhD"] else 0)
        ) else 0,
        axis=1
    )
    return df

def generate_healthcare(num_rows=2500):
    """Healthcare dataset mimicking US hospital treatment approval (CMS 2024 data)"""
    data = {
        "patient_id": range(1, num_rows + 1),
        "age": np.random.randint(18, 85, num_rows),
        "gender": np.random.choice(
            ["Male", "Female", "Non-binary"],
            num_rows,
            p=[0.47, 0.49, 0.04]
        ),
        "race": np.random.choice(
            ["White", "Black", "Hispanic", "Asian", "Other"],
            num_rows,
            p=[0.58, 0.12, 0.19, 0.06, 0.05]
        ),
        "insurance_type": np.random.choice(
            ["Private", "Medicare", "Medicaid", "Uninsured"],
            num_rows,
            p=[0.56, 0.23, 0.18, 0.03]
        )
    }
    df = pd.DataFrame(data)
    # Realistic bias: Black/Hispanic 18% less likely, Uninsured 25% less likely
    df["treatment_approved"] = df.apply(
        lambda r: 1 if np.random.rand() < (
            0.65  # Base approval rate
            - (0.18 if r["race"] in ["Black", "Hispanic"] else 0)
            - (0.25 if r["insurance_type"] == "Uninsured" else 0)
            + (0.08 if r["age"] > 55 else 0)
        ) else 0,
        axis=1
    )
    return df

def generate_lending(num_rows=2500):
    """Lending dataset mimicking US mortgage/lending approval (FFIEC 2024 data)"""
    data = {
        "applicant_id": range(1, num_rows + 1),
        "age": np.random.randint(21, 72, num_rows),
        "gender": np.random.choice(
            ["Male", "Female", "Non-binary"],
            num_rows,
            p=[0.47, 0.49, 0.04]
        ),
        "race": np.random.choice(
            ["White", "Black", "Hispanic", "Asian", "Other"],
            num_rows,
            p=[0.58, 0.12, 0.19, 0.06, 0.05]
        ),
        "income_bracket": np.random.choice(
            ["Low", "Medium", "High"],
            num_rows,
            p=[0.30, 0.52, 0.18]
        )
    }
    df = pd.DataFrame(data)
    # Realistic bias: Black/Hispanic 21% less likely, Female 9% less likely
    df["loan_approved"] = df.apply(
        lambda r: 1 if np.random.rand() < (
            0.58  # Base approval rate
            - (0.21 if r["race"] in ["Black", "Hispanic"] else 0)
            - (0.09 if r["gender"] == "Female" else 0)
            + (0.20 if r["income_bracket"] == "High" else 0)
        ) else 0,
        axis=1
    )
    return df

def generate_insurance(num_rows=2500):
    """Insurance dataset mimicking US health/auto insurance approval (NAIC 2024 data)"""
    data = {
        "applicant_id": range(1, num_rows + 1),
        "age": np.random.randint(18, 78, num_rows),
        "gender": np.random.choice(
            ["Male", "Female", "Non-binary"],
            num_rows,
            p=[0.47, 0.49, 0.04]
        ),
        "race": np.random.choice(
            ["White", "Black", "Hispanic", "Asian", "Other"],
            num_rows,
            p=[0.58, 0.12, 0.19, 0.06, 0.05]
        ),
        "policy_type": np.random.choice(
            ["Health", "Auto", "Life", "Home"],
            num_rows,
            p=[0.40, 0.30, 0.18, 0.12]
        )
    }
    df = pd.DataFrame(data)
    # Realistic bias: Older applicants 12% less likely, Black/Hispanic 16% less likely
    df["policy_approved"] = df.apply(
        lambda r: 1 if np.random.rand() < (
            0.68  # Base approval rate
            - (0.16 if r["race"] in ["Black", "Hispanic"] else 0)
            - (0.12 if r["age"] > 62 else 0)
            + (0.10 if r["policy_type"] == "Auto" else 0)
        ) else 0,
        axis=1
    )
    return df

if __name__ == "__main__":
    os.makedirs("datasets", exist_ok=True)

    generate_hiring().to_csv("datasets/hiring_dataset.csv", index=False)
    generate_healthcare().to_csv("datasets/healthcare_dataset.csv", index=False)
    generate_lending().to_csv("datasets/lending_dataset.csv", index=False)
    generate_insurance().to_csv("datasets/insurance_dataset.csv", index=False)

    print("4 domain datasets generated successfully")
    print(f"Hiring rows: {len(pd.read_csv('datasets/hiring_dataset.csv'))}")
    print(f"Healthcare rows: {len(pd.read_csv('datasets/healthcare_dataset.csv'))}")
    print(f"Lending rows: {len(pd.read_csv('datasets/lending_dataset.csv'))}")
    print(f"Insurance rows: {len(pd.read_csv('datasets/insurance_dataset.csv'))}")
