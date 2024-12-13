from typing import List

def is_safe(report: List[int]) -> bool:
    if len(report) == 1:
        return True
    base_diff = report[1] - report[0]
    if base_diff == 0:
        return False
    is_ascending = base_diff > 0
    prev = report[0]
    for i, item in enumerate(report):
        if i == 0:
            continue
        diff = prev - item
        if diff == 0:
            return False
        if abs(diff) > 3:
            return False
        if (diff > 0 and is_ascending) or (diff < 0 and not is_ascending):
            return False
        prev = item
    return True


with open("puzzle.txt", "r") as fr:
    safe_reports = []
    for line in fr:
        report = [int(i) for i in line.split(' ')]
        if is_safe(report=report):
            safe_reports.append(report)
    print(len(safe_reports))  # solution a

with open("puzzle.txt", "r") as fr:
    safe_reports_extended = []
    for line in fr:
        report = [int(i) for i in line.split(' ')]
        if is_safe(report=report):
            safe_reports_extended.append(report)
            continue
        for i, item in enumerate(report):
            new_report = report.copy()
            new_report.pop(i)
            if is_safe(report=new_report):
                safe_reports_extended.append(report)
                break
    print(len(safe_reports_extended))  # solution b

