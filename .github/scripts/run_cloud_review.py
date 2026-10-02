import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from review_engine import execute_review_batch
import location_day3_tasks

def main():
    print("=== DÉMARRAGE DU CODE REVIEW CLOUD : JOUR 3 (LOCATION PROJECT) ===")
    repo_root = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

    tasks = location_day3_tasks.create_tasks()
    batch_name = "CloudReview_Location_Day3_08Oct"

    count = execute_review_batch(repo_root, tasks, batch_name)
    print(f"=== CODE REVIEW CLOUD TERMINÉ : {count}/{len(tasks)} CONTRIBUTIONS POUSSÉES DANS LE CLOUD ===")

if __name__ == "__main__":
    main()
