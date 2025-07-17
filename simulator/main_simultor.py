import os
import pandas as pd
import numpy as np
import argparse
from utils.project_enums import BoneQuality, MuscleStrength, DiseaseStage, Complications, SurgeryStatus


def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patients-num", default=50, type=int, help="number of patients to simulate")
    parser.add_argument("--days-interval", default=15, type=int, help="treatment days interval")
    parser.add_argument("--output-dir", default='simulator_datasets', type=str, help="simulation output directory")

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.patients_num <= 0 or args.patients_num > 100:
        raise ValueError("patients_num must be between 1 and 100")

    if args.days_interval <= 0 or args.days_interval > 100:
        raise ValueError("days_interval must be between 1 and 100")

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)


def vary_value(val, low=0, high=1, max_change=0.05):
    change = np.random.uniform(-max_change, max_change)
    new_val = val + change
    return np.clip(new_val, low, high)


def init_patients_dataset(n_patients: int, n_days: int) -> pd.DataFrame:

    p_day = []
    for patient_id in range(100, n_patients + 101):

        # first day initiation
        bone_quality = np.random.choice(BoneQuality, p=[0.3, 0.5, 0.2])
        frailty_level = np.random.uniform(0, 1)
        muscle_strength = np.random.choice(MuscleStrength, p=[0.3, 0.5, 0.2])
        disease_progression = np.random.choice(DiseaseStage, p=[0.4, 0.3, 0.2, 0.1])
        surgery_status = 'No'
        complications = 'No'
        sfr_score = np.random.uniform(0.2, 0.6)
        frax_score = np.random.uniform(5, 20)
        functional_independence = np.random.uniform(70, 100)
        pain_level = np.random.randint(0, 5)
        economic_burden = 0
        cumulative_suffering = 0
        fracture_event = 'No'
        mortality_risk = np.random.uniform(0.005, 0.02)
        decision = 'Wait'
        notes = ''

        # simulate surgery
        is_surgery = np.random.choice(SurgeryStatus, p=[0.95, 0.05])
        surgery_day = np.random.randint(1, n_days) if is_surgery else 0

        for day in range(1, n_days + 1):

            # Surgery and complications
            if day == surgery_day:
                surgery_status = 'Yes'
                decision = 'Surgery'
                notes = 'Surgery done today'
            else:
                decision = 'Wait'
                notes = ''

            # if surgery done it may cause issues - worse health but may be better/worse in x days ?
            if surgery_status == 'Yes' and day in range(surgery_day, n_days + 1):
                complications = np.random.choice(Complications, p=[0.85, 0.15])

            # Bone quality - can be better ?
            if np.random.rand() < 0.05:
                bone_quality = np.random.choice(BoneQuality)

            # Frailty - bone quality and Fragility are the same ? depends on each other ?
            frailty_level = vary_value(frailty_level, 0, 1)

            # Muscle strength - can be better ?
            if np.random.rand() < 0.1:
                muscle_strength = np.random.choice(MuscleStrength)

            # Disease progression - tend to be equal or worse
            if np.random.rand() < 0.1:
                idx = disease_progression.value
                if idx < len(DiseaseStage) - 1:
                    disease_progression = DiseaseStage[idx + 1]

            # SFR - how it is changed ?
            sfr_score = vary_value(sfr_score, 0.1, 0.7, 0.02)

            # FRAX - how it is changed ?
            frax_score = vary_value(frax_score, 1, 30, 1)

            # Functional independence - decrease after surgery but can improve after surgery
            if surgery_status == 'Yes' and day >= 5:
                functional_independence = max(functional_independence - np.random.uniform(5, 10), 30)
            else:
                functional_independence = max(functional_independence - np.random.uniform(0, 3), 30)

            # Pain level - decrease after surgery if no complications but might increase while the decease getting worse
            if surgery_status == 'Yes' and complications == 'No' and day >= 6:
                pain_level = max(pain_level - 1, 0)
            else:
                pain_level = min(pain_level + np.random.choice([0, 1]), 10)
            cumulative_suffering += pain_level * (1 + frailty_level)

            # financial costs
            economic_burden += np.random.uniform(50, 200)

            # friction event - higher probability for these with higher SFR, FRAX and frailty
            fracture_prob = max(0.01, 0.05 * (1 - sfr_score) + 0.03 * (frax_score / 30) + 0.1 * frailty_level)
            fracture_event = 'Yes' if np.random.rand() < fracture_prob else 'No'

            # Death probability depends on decease, friction and complications
            mortality_risk = 0.01 + 0.05 * (DiseaseStage.index(disease_progression) / (len(DiseaseStage) - 1))
            if fracture_event == 'Yes':
                mortality_risk += 0.1
            if complications == 'Yes':
                mortality_risk += 0.1

            # Append patient day status
            p_day.append({
                'Patient_ID': patient_id,
                'Day': day,
                'Bone_Quality': bone_quality,
                'Frailty_Level': round(frailty_level, 3),
                'Muscle_Strength': muscle_strength,
                'Disease_Progression': disease_progression,
                'Surgery_Status': surgery_status,
                'Complications': complications,
                'SFR_Score': round(sfr_score, 3),
                'FRAX_Score': round(frax_score, 2),
                'Functional_Independence': round(functional_independence, 1),
                'Pain_Level': pain_level,
                'Economic_Burden': round(economic_burden, 2),
                'Cumulative_Suffering': round(cumulative_suffering, 2),
                'Fracture_Event': fracture_event,
                'Mortality_Risk': round(mortality_risk, 3),
                'Decision': decision,
                'Notes': notes
            })

    return pd.DataFrame(p_day)


def main(args: argparse.Namespace):

    validate_args(args)

    df_patients = init_patients_dataset(args.patients_num, args.days_interval)

    # if exists delete and create new one
    df_patients.to_csv(os.path.join(args.output_dir, 'patients.csv'), index=False)

if __name__ == "__main__":

    np.random.seed(42)
    parsed_args = setup()
    main(parsed_args)
