import json
import pandas as pd
from helper_functions import (
    log_error, parse_course_number, extract_credits, extract_prereqs,
    extract_schedule, process_gpa, format_term
)

# Load the data files
term_files = [
    'FA22.tsv', 'FA23.tsv', 'FA24.tsv', 'S122.tsv', 'S123.tsv', 'S124.tsv',
    'S222.tsv', 'S223.tsv', 'S224.tsv', 'S323.tsv', 'S324.tsv', 'SP22.tsv',
    'SP23.tsv', 'SP24.tsv', 'WI23.tsv', 'WI24.tsv', 'WI25.tsv'
]
courses_path = 'processed_courses.tsv'
capes_path = 'CAPEs.tsv'
grades_path = 'grades.tsv'

print("Loading data files...")
try:
    term_dataframes = {term: pd.read_csv(term, sep='\t') for term in term_files}
    courses_df = pd.read_csv(courses_path, sep='\t')
    capes_df = pd.read_csv(capes_path, sep='\t')
    grades_df = pd.read_csv(grades_path, sep='\t')
    print("Data files loaded successfully.")
except Exception as e:
    log_error(f"Error loading data files: {e}")
    raise

# Mapping of term codes to human-readable names
term_name_mapping = {
    "FA": "Fall",
    "SP": "Spring",
    "WI": "Winter",
    "S1": "Summer 1",
    "S2": "Summer 2",
    "S3": "Summer 3"
}

# Processing courses
print("Processing courses...")
output_path = 'courses_output.json'
try:
    with open(output_path, 'w') as json_file:
        json_file.write('[\n')
        first_entry = True

        for _, course in courses_df.iterrows():
            try:
                subj_course_id = course['subj_course_id']
                subj_course_id = parse_course_number(subj_course_id)
                terms = set()
                instructor_map = {}
                crns = []
                sched = []

                for term_name, term_df in term_dataframes.items():
                    term_courses = term_df[term_df['subj_course_id'] == subj_course_id]
                    for _, term_course in term_courses.iterrows():
                        term_code = term_name.split('.')[0]
                        formatted_term = format_term(term_code, term_name_mapping)
                        terms.add(formatted_term)
                        crns.append(term_course['sec_id'])
                        sched.extend(extract_schedule(term_course['meetings']))
                        instructor = term_course['instructor']

                        if instructor:
                            if formatted_term not in instructor_map:
                                instructor_map[formatted_term] = []
                            if instructor not in instructor_map[formatted_term]:
                                instructor_map[formatted_term].append(instructor)

                sched = list(set(sched))

                instructor_formatted = {
                    term: sorted(instructor_map[term]) if term in instructor_map else []
                    for term in terms
                }

                gpa_formatted = {
                    instructor: {
                        term: process_gpa(instructor, term, subj_course_id, grades_df, capes_df)
                        for term in instructor_map if instructor in instructor_map[term]
                    }
                    for term_instructors in instructor_map.values() for instructor in term_instructors
                }

                course_entry = {
                    "terms": sorted(terms),
                    "instructor": instructor_formatted,
                    "crn": crns,
                    "sched": sched,
                    "description": course['description'],
                    "title": course['course_name'],
                    "subjectCode": subj_course_id.split()[0],
                    "courseCode": subj_course_id.split()[1],
                    "credits": extract_credits(course['units']),
                    "gened": [],
                    "gpa": gpa_formatted,
                    "prereqs": ([extract_prereqs(course['description'])] if extract_prereqs(course['description']) else []),
                    "fullTitle": f"{subj_course_id} {course['course_name']}",
                    "detailId": f"{subj_course_id.replace(' ', '')}{course['course_name'].replace(' ', '')}"
                }

                if not first_entry:
                    json_file.write(',\n')
                json.dump(course_entry, json_file, indent=4)
                first_entry = False

            except Exception as e:
                log_error(f"Error processing course", {"subj_course_id": course.get('subj_course_id'), "error": str(e)})
        json_file.write('\n]')
    print("Output saved successfully.")
except Exception as e:
    log_error(f"Error saving output to file: {e}")
