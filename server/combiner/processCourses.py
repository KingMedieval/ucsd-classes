import pandas as pd
import re


def split_multipart_courses(df):
    """
    Splits multi-part courses in the DataFrame into separate rows for each part,
    handling units separated by '/', '-', '–', ',', or ';'.

    Parameters:
    - df: pandas DataFrame containing course data with a 'subj_course_id' column.

    Returns:
    - A new pandas DataFrame with multi-part courses split into individual rows.
    """
    # List to collect the new rows
    new_rows = []

    for _, row in df.iterrows():
        subj_course_id = str(row['subj_course_id']).strip()  # Ensure it's a string and strip whitespace
        units = str(row['units']).strip()  # Ensure it's a string and strip whitespace

        # Standardize hyphens and en-dashes to a common separator
        subj_course_id_standardized = subj_course_id.replace('–', '-').replace('—', '-')

        if '-' in subj_course_id_standardized:
            # Split the subj_course_id by hyphens
            tokens = subj_course_id_standardized.split('-')

            # Process the first token to get base_id and first_part
            first_token = tokens[0]
            match = re.match(r'([A-Za-z]+\s*\d+)([A-Za-z]*)', first_token)
            if match:
                base_id = match.group(1)
                first_part = match.group(2)

                # Get the parts: first_part plus the remaining tokens
                parts = [first_part] + tokens[1:]
                parts = [part.strip() for part in parts if part.strip()]  # Clean parts

                # Handle ranges like 'A–B' where parts may be single letters
                expanded_parts = []
                for part in parts:
                    if len(part) == 1 and part.isalpha():
                        expanded_parts.append(part)
                    elif len(part) == 2 and part[0] == '–' and part[1].isalpha():
                        expanded_parts.append(part[1])
                    else:
                        expanded_parts.append(part)

                # Generate the list of course parts
                if len(expanded_parts) == 2 and all(len(p) == 1 for p in expanded_parts):
                    # If it's a range like 'A-B', expand it
                    start_part = expanded_parts[0]
                    end_part = expanded_parts[1]
                    part_sequence = [chr(c) for c in range(ord(start_part), ord(end_part) + 1)]
                else:
                    part_sequence = expanded_parts

                # Standardize units string by replacing en-dashes with hyphens
                units_standardized = units.replace('–', '-').replace('—', '-')

                # Split units into a list using '/', ',', or ';' as separators
                units_list = re.split(r'[\/,;]', units_standardized)
                units_list = [u.strip() for u in units_list if u.strip()]

                # Further split units that are formatted like '4-4-4'
                expanded_units_list = []
                for unit in units_list:
                    unit = unit.strip()
                    # Check if the unit is a sequence like '4-4-4'
                    if unit.count('-') >= len(part_sequence) - 1 and re.fullmatch(r'(\d+-)+\d+', unit):
                        # Split the unit string on hyphens
                        sub_units = unit.split('-')
                        expanded_units_list.extend(sub_units)
                    else:
                        expanded_units_list.append(unit)

                units_list = expanded_units_list

                # Extend units_list if necessary
                if len(units_list) < len(part_sequence):
                    units_list.extend([units_list[-1]] * (len(part_sequence) - len(units_list)))

                # Create new rows for each part
                for i, part in enumerate(part_sequence):
                    new_row = row.copy()
                    new_row['subj_course_id'] = base_id + part
                    new_row['units'] = units_list[i] if i < len(units_list) else units_list[-1]
                    new_rows.append(new_row)
            else:
                # If parsing fails, keep the row as is
                new_rows.append(row)
        else:
            # No hyphen in subj_course_id, keep the row as is
            new_rows.append(row)

    # Create a new DataFrame from new_rows
    new_df = pd.DataFrame(new_rows)
    return new_df


def split_course_numbers_with_slash(df):
    """
    Splits courses where the course number is followed by a slash and another number, e.g., 'CHIN 160/260',
    into separate rows. Only applies when numbers are separated by a slash '/'.

    Parameters:
    - df: pandas DataFrame containing course data.

    Returns:
    - A new pandas DataFrame with the specified courses split into individual rows.
    """
    new_rows = []
    for _, row in df.iterrows():
        subj_course_id = str(row['subj_course_id']).strip()

        # Match pattern: course prefix, space, number(s), '/', number(s)
        match = re.match(r'^([A-Za-z]+\s*)(\d+)/(\d+)$', subj_course_id)
        if match:
            prefix = match.group(1)
            number1 = match.group(2)
            number2 = match.group(3)

            # Create new rows for each course number
            for number in [number1, number2]:
                new_row = row.copy()
                new_row['subj_course_id'] = prefix + number
                new_rows.append(new_row)
        else:
            # If pattern doesn't match, keep the row as is
            new_rows.append(row)

    # Create a new DataFrame from new_rows
    new_df = pd.DataFrame(new_rows)
    return new_df


def split_course_numbers_with_commas(df):
    """
    Splits courses where the course number is followed by commas and other numbers or parts,
    e.g., 'LISP 5A, 5B, 5C, 5D', into separate rows. Only applies when commas are used to separate parts.

    Parameters:
    - df: pandas DataFrame containing course data.

    Returns:
    - A new pandas DataFrame with the specified courses split into individual rows.
    """
    new_rows = []
    for _, row in df.iterrows():
        subj_course_id = str(row['subj_course_id']).strip()

        if ',' in subj_course_id:
            # Split tokens by comma
            tokens = [token.strip() for token in subj_course_id.split(',')]
            # Process the first token to get base department and number
            first_token = tokens[0]
            match = re.match(r'^([A-Za-z]+)\s*(\d+)([A-Za-z]?)$', first_token)
            if match:
                base_dept = match.group(1)
                base_number = match.group(2)
                base_prefix = base_dept + ' ' + base_number
                # Now, create new rows
                for token in tokens:
                    token = token.strip()
                    if re.match(r'^[A-Za-z]+\s*\d+[A-Za-z]?$', token):
                        # Full course code, use as is
                        new_subj_course_id = token
                    elif re.match(r'^\d+[A-Za-z]?$', token):
                        # Token is like '5B', combine with base department
                        new_subj_course_id = base_dept + ' ' + token
                    elif re.match(r'^[A-Za-z]$', token):
                        # Token is like 'B', combine with base prefix
                        new_subj_course_id = base_prefix + token
                    else:
                        # Unhandled format, keep as is
                        new_subj_course_id = token
                    new_row = row.copy()
                    new_row['subj_course_id'] = new_subj_course_id
                    new_rows.append(new_row)
            else:
                # If pattern doesn't match, keep the row as is
                new_rows.append(row)
        else:
            # No comma in subj_course_id, keep the row as is
            new_rows.append(row)

    # Create a new DataFrame from new_rows
    return pd.DataFrame(new_rows)


def finalize_units(df):
    """
    Processes the 'units' column to remove duplicates and format the units appropriately.
    Only processes units with two or more dashes.
    If there are units with multiple dashes like '4-4-4', convert it to '4'.
    If there are different numbers, like '1-3-4', convert it to '1, 3, 4' (sorted and no duplicates).
    Leaves units with only one dash (e.g., '1-4') unchanged.

    Parameters:
    - df: pandas DataFrame containing course data.

    Returns:
    - The same DataFrame with the 'units' column processed.
    """
    def process_units(units):
        units = str(units).strip()
        # Standardize hyphens and en-dashes
        units = units.replace('–', '-').replace('—', '-')
        # Count the number of dashes
        dash_count = units.count('-')
        if dash_count < 2:
            # Leave units with less than two dashes unchanged
            return units
        else:
            # Split units by hyphens
            unit_numbers = re.split(r'-', units)
            unit_numbers = [u.strip() for u in unit_numbers if u.strip()]
            # Collect unique numbers
            unique_units = set(unit_numbers)
            if len(unique_units) == 1:
                return unique_units.pop()
            else:
                # Return sorted, comma-separated numbers without duplicates
                sorted_units = sorted(unique_units, key=lambda x: int(re.findall(r'\d+', x)[0]))
                return ', '.join(sorted_units)
    df['units'] = df['units'].apply(process_units)
    return df


# Load the dataset
file_path = 'courses.tsv'  # Replace with your file path
courses_df = pd.read_csv(file_path, sep='\t')

# Process the data
processed_courses_df = split_multipart_courses(courses_df)
processed_courses_df = split_course_numbers_with_slash(processed_courses_df)
processed_courses_df = split_course_numbers_with_commas(processed_courses_df)
processed_courses_df = finalize_units(processed_courses_df)

# Save the processed data
output_path = 'processed_courses.tsv'  # Replace with your desired output path
processed_courses_df.to_csv(output_path, sep='\t', index=False)

print(f"Processed file saved to {output_path}")
