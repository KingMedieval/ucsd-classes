import re
import pandas as pd
from typing import List, Optional, Dict, Any

log_file = 'error_log.txt'

def log_error(error_message: str, additional_info: Optional[Dict[str, Any]] = None):
    """Logs errors to a file with optional additional context."""
    with open(log_file, 'a') as f:
        f.write(f"Error: {error_message}\n")
        if additional_info:
            f.write(f"Context: {additional_info}\n")
        f.write("\n")

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
        return match.group(1) if match else None
    except Exception as e:
        log_error(f"Error extracting prerequisites: {e}", {"description": description})
        return None

def extract_schedule(meetings: str) -> List[str]:
    """Extracts schedule types from a meetings string."""
    try:
        return list(set(re.findall(r"\b[A-Z]{2}\b", meetings)))
    except Exception as e:
        log_error(f"Error extracting schedule: {e}", {"meetings": meetings})
        return []

def process_gpa(instructor: str, term: str, course_id: str, grades_df: pd.DataFrame, capes_df: pd.DataFrame) -> Optional[List[float]]:
    """
    Processes GPA data for a specific instructor, term, and course.

    Parameters:
        instructor (str): The name of the instructor.
        term (str): The term (e.g., Fall 2023).
        course_id (str): The course identifier.
        grades_df (pd.DataFrame): The grades data.
        capes_df (pd.DataFrame): The CAPEs data.

    Returns:
        Optional[List[float]]: The GPA distribution or None if not found.
    """
    try:
        # Filter for specific course, instructor, and term in grades
        grade_row = grades_df[
            (grades_df['instructor'] == instructor) &
            (grades_df['Term'] == term) &
            (grades_df['subj_course_id'] == course_id)
        ]
        if not grade_row.empty:
            grade_dist = grade_row.iloc[0]['Grade distribution']
            if isinstance(grade_dist, str):
                grades = list(map(float, re.findall(r"[0-9]+(?:\.[0-9]+)?", grade_dist)))
                if len(grades) == 14:
                    return grades

        # Fall back to CAPEs for specific course, instructor, and term
        cape_row = capes_df[
            (capes_df['instructor'] == instructor) &
            (capes_df['term'] == term) &
            (capes_df['subj_course_id'] == course_id)
        ]
        if not cape_row.empty:
            avg_gpa = cape_row.iloc[0]['avg_grade_rec']
            if avg_gpa != -1:
                return [0] * 13 + [avg_gpa]

        return None
    except Exception as e:
        log_error(f"Error processing GPA", {
            "instructor": instructor,
            "term": term,
            "course_id": course_id,
            "error": str(e)
        })
        return None

def format_term(term_code: str, term_mapping: Dict[str, str]) -> str:
    """Converts a term code to a human-readable format."""
    try:
        term_prefix = term_code[:2]
        year = "20" + term_code[2:4]
        return f"{term_mapping.get(term_prefix, term_prefix)} {year}"
    except Exception as e:
        log_error(f"Error formatting term: {e}", {"term_code": term_code})
        return term_code