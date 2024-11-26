'''
This function is used to search for a column value in a row. It will first search in the '__debug__' field, then in the '__debug__.__original__' field, and finally in the row itself. If the value is found, it will be set in the row and returned.
'''

from .. constants import (
    INPUT_FIELD,
    STAGING_FIELD,
)

from collections import OrderedDict

def search_column_value(
    row: OrderedDict,
    column: str,
):
    if f'{STAGING_FIELD}.{column}' in row:
        value = row[f'{STAGING_FIELD}.{column}']
        return value, True
    if f'{STAGING_FIELD}.{INPUT_FIELD}.{column}' in row:
        value = row[f'{STAGING_FIELD}.{INPUT_FIELD}.{column}']
        return value, True
    if column in row:
        value = row[column]
        return value, True
    return None, False