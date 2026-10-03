#!/usr/bin/env python3
"""Summarize one week of clinic encounters and save the two report files."""

from pathlib import Path

from vitals_tools import (
    count_patients,
    mean_systolic,
    patients_at_or_above,
    systolic_readings,
)


DATA_PATH = Path("data") / "clinic_encounters.csv"
OUTPUT_DIR = Path("output")


def read_encounters(data_path):
    rows = data_path.read_text(encoding="utf-8").splitlines()
    encounters = []
    skipped = 0
    for row in rows[1:]:                      # rows[0] is the header
        if not row.strip():
            print("Skipping a blank row.")
            skipped += 1
            continue
        fields = row.strip().split(",")
        if len(fields) != 3:
            print(f"Skipping a row with {len(fields)} fields: {row.strip()}")
            skipped += 1
            continue
        patient_id, visit_date, raw_systolic = fields
        try:
            systolic = int(raw_systolic)
        except ValueError as error:
            print(f"Skipping {patient_id}: {error}")
            skipped += 1
            continue
        if not 60 <= systolic <= 250:
            print(f"Skipping {patient_id}: {systolic} mmHg is outside 60-250")
            skipped += 1
            continue
        encounters.append(
            {"patient_id": patient_id, "visit_date": visit_date, "systolic": systolic}
        )
    return encounters, skipped


def main():
    encounters, skipped = read_encounters(DATA_PATH)
    assert encounters, f"no usable readings in {DATA_PATH}"

    readings = systolic_readings(encounters)
    report_lines = [
        f"Usable encounters: {len(encounters)}",
        f"Skipped rows: {skipped}",
        f"Patients seen: {count_patients(encounters)}",
        f"Mean systolic: {mean_systolic(readings):.1f} mmHg",
        f"Highest systolic: {max(readings)} mmHg",
        f"Lowest systolic: {min(readings)} mmHg",
    ]
    report_text = "\n".join(report_lines) + "\n"

    OUTPUT_DIR.mkdir(exist_ok=True)
    report_path = OUTPUT_DIR / "vitals_report.txt"
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(report_text)

    with open(report_path, encoding="utf-8") as report_file:
        saved_text = report_file.read()
    print(f"Read back from {report_path}:")
    print(saved_text, end="")

    cutoff = 180
    reason = "I chose 180 as the cutoff threshold because it is the hypertensive crisis threshold so readings at or above it are most urgent."
    followup_ids = patients_at_or_above(encounters, cutoff)

    followup_lines = [f"Cutoff: {cutoff} mmHg", f"Reason: {reason}"] + followup_ids
    followup_path = OUTPUT_DIR / "followup_list.txt"
    with open(followup_path, "w", encoding="utf-8") as followup_file:
        followup_file.write("\n".join(followup_lines) + "\n")

    print(f"Read back from {followup_path}:")
    print(followup_path.read_text(encoding="utf-8"), end="")

if __name__ == "__main__":
    main()
