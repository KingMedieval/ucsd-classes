import re
from typing import List, Optional
import pandas as pd

log_file = 'error_log.txt'

def log_error(error_message: str):
    """Logs errors to a file."""
    with open(log_file, 'a') as f:
        f.write(error_message + '\n')

def parse_course_number(course_number: str) -> str:
    """Parses a course number string to extract the subject and course code."""
    try:
        parts = course_number.split('/')
        first_part = parts[0].strip()
        pattern = r'^([A-Z]+)\s*(\d+[A-Z]*)$'
        match = re.match(pattern, first_part)

        if match:
            subject_code = match.group(1)
            course_num = match.group(2)
            result = f'{subject_code} {course_num}'
        else:
            course_num_match = re.search(r'(\d+[A-Z]*)$', course_number)
            if course_num_match:
                course_num = course_num_match.group(1)
                subject_code_match = re.match(r'^([A-Z]+)', first_part)
                if subject_code_match:
                    subject_code = subject_code_match.group(1)
                    result = f'{subject_code} {course_num}'
                else:
                    result = first_part
            else:
                result = first_part

        print(f"Input: {course_number}")
        print(f"Parsed Result: {result}")
        return result
    except Exception as e:
        log_error(f"Error in parse_course_number for {course_number}: {str(e)}")
        return course_number

def check_multipart_course(course_number: str):
    """Checks if a course is multipart and logs it."""
    try:
        if '-' in course_number:
            print(f"Detected multipart course: {course_number}")
            exit(1)
    except Exception as e:
        log_error(f"Error in check_multipart_course for {course_number}: {str(e)}")

def extract_credits(units: str) -> List[int]:
    """Extracts a list of credit options from a units string."""
    try:
        print(f"Extracting credits from: {units}")
        units = units.replace('–', '-')
        if '/' in units:
            parts = units.split('/')
            result = set()
            for part in parts:
                if '-' in part:
                    start, end = map(int, re.findall(r'\d+', part))
                    result.update(range(start, end + 1))
                elif part.isdigit():
                    result.add(int(part))
            credits = sorted(result)
            print(f"Extracted credits from '{units}': {credits}")
            return credits
        elif '-' in units:
            start, end = map(int, re.findall(r'\d+', units))
            credits = list(range(start, end + 1))
            print(f"Extracted range credits: {credits}")
            return credits
        elif 'or' in units:
            credits = list(map(int, re.findall(r'\d+', units)))
            print(f"Extracted 'or' credits: {credits}")
            return credits
        elif 'to' in units:
            start, end = map(int, re.findall(r'\d+', units))
            credits = list(range(start, end + 1))
            print(f"Extracted 'to' credits: {credits}")
            return credits
        credits = list(map(int, units.split(', ')))
        print(f"Extracted list credits: {credits}")
        return credits
    except Exception as e:
        log_error(f"Error in extract_credits for {units}: {str(e)}")
        return []

def extract_prereqs(description: str) -> Optional[str]:
    """Extracts prerequisites from a course description."""
    try:
        match = re.search(r"Prerequisites: (.*)", description)
        prereqs = match.group(1) if match else None
        print(f"Extracted prerequisites from description: {prereqs}")
        return prereqs
    except Exception as e:
        log_error(f"Error in extract_prereqs for description: {str(e)}")
        return None

def extract_schedule(meetings: str) -> List[str]:
    """Extracts schedule types from a meetings string."""
    try:
        schedule = list(set(re.findall(r"\b[A-Z]{2}\b", meetings)))
        print(f"Extracted schedule types from meetings: {meetings} -> {schedule}")
        return schedule
    except Exception as e:
        log_error(f"Error in extract_schedule for meetings: {str(e)}")
        return []

def process_gpa(instructor: str, term: str, grades_df: pd.DataFrame, capes_df: pd.DataFrame) -> Optional[List[float]]:
    """Processes GPA data for an instructor and term."""
    try:
        print(f"Processing GPA for instructor: {instructor}, term: {term}")
        grade_row = grades_df[(grades_df['instructor'] == instructor) & (grades_df['Term'] == term)]
        if not grade_row.empty:
            print(f"Found GPA entry in grades.tsv for {instructor}, {term}")
            grade_dist = grade_row.iloc[0]['Grade distribution']
            if isinstance(grade_dist, str):
                grades = list(map(float, re.findall(r"[0-9]+(?:\.[0-9]+)?", grade_dist)))
                if len(grades) == 14:
                    print(f"Grades from grades.tsv: {grades}")
                    return grades

        print(f"Looking for fallback GPA in CAPEs.tsv for {instructor}, {term}")
        cape_row = capes_df[(capes_df['instructor'] == instructor) & (capes_df['term'] == term)]
        if not cape_row.empty:
            avg_gpa = cape_row.iloc[0]['avg_grade_rec']
            if avg_gpa != -1:
                fallback_gpa = [0] * 13 + [avg_gpa]
                print(f"Grades from CAPEs.tsv fallback: {fallback_gpa}")
                return fallback_gpa

        print(f"No GPA data found for {instructor} in {term}.")
        return None
    except Exception as e:
        log_error(f"Error in process_gpa for {instructor}, {term}: {str(e)}")
        return None