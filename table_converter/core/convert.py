# -*- coding: utf-8 -*-

import json
import os

from collections import OrderedDict

import pandas as pd
from icecream import ic

map_loaders: dict[str, callable] = {}
def register_loader(
    ext: str,
):
    def decorator(loader):
        map_loaders[ext] = loader
        return loader
    return decorator

map_savers: dict[str, callable] = {}
def register_saver(
    ext: str,
):
    def decorator(saver):
        map_savers[ext] = saver
        return saver
    return decorator

@register_loader('.xlsx')
def load_excel(
    input_file: str,
):
    df = pd.read_excel(input_file)
    return df

@register_saver('.json')
def save_json(
    df: pd.DataFrame,
    output_file: str,
):
    df.to_json(
        output_file,
        orient='records',
        force_ascii=False,
        indent=2,
    )

@register_saver('.jsonl')
def save_jsonl(
    df: pd.DataFrame,
    output_file: str,
):
    df.to_json(
        output_file,
        orient='records',
        lines=True,
        force_ascii=False,
    )

def set_field_value(
    data: OrderedDict,
    field: str,
    value: any,
):
    if '.' in field:
        field, rest = field.split('.', 1)
        if field not in data:
            data[field] = OrderedDict()
        set_field_value(data[field], rest, value)
    else:
        data[field] = value

def get_field_value(
    data: OrderedDict,
    field: str,
    default: any = None,
    raise_error: bool = True,
):
    if field in data:
        return data[field]
    if '.' in field:
        field, rest = field.split('.', 1)
        if field in data:
            return get_field_value(data[field], rest)
    if raise_error:
        raise KeyError(f'Field not found: {field}, existing fields: {data.keys()}')
    return default

def remap_df(
    df: pd.DataFrame,
    column_map: OrderedDict,
):
    #ic()
    ic(df.columns)
    ic(column_map)
    new_rows = []
    for index, row in df.iterrows():
        new_row = OrderedDict()
        mapped_set = set()
        for column in column_map.keys():
            set_field_value(new_row, column, row[column_map[column]])
            mapped_set.add(column_map[column])
        rest = OrderedDict()
        for column in df.columns:
            if column not in mapped_set:
                if column == '__file__':
                    set_field_value(new_row, '__debug__.__file__', row['__file__'])
                rest[column] = row[column]
        set_field_value(new_row, '__debug__.__rest__', rest)
        new_rows.append(new_row)
    new_df = pd.DataFrame(new_rows)
    ic(new_df.columns)
    ic(new_df.iloc[0])
    #ic(df)
    #ic(new_df)
    return new_df

def apply_fields_split_by_newline(
    df: pd.DataFrame,
    fields: list[str],
):
    new_rows = []
    for index, row in df.iterrows():
        new_row = OrderedDict(row)
        for field in fields:
            value = get_field_value(row, field)
            if isinstance(value, str):
                new_value = value.split('\n')
                set_field_value(new_row, field, new_value)
        new_rows.append(new_row)
    new_df = pd.DataFrame(new_rows)
    return new_df

def convert(
    input_files: list[str],
    output_file: str | None = None,
    pickup_columns: str | None = None,
    fields_split_by_newline: str | None = None,
):
    ic()
    ic(input_files)
    df_list = []
    column_map: OrderedDict | None = None
    list_fields_split_by_newline = None
    if pickup_columns:
        column_map = OrderedDict()
        fields = pickup_columns.split(',')
        for field in fields:
            if '=' in field:
                dst, src = field.split('=')
                column_map[dst] = src
            else:
                column_map[field] = field
    if fields_split_by_newline:
        list_fields_split_by_newline = fields_split_by_newline.split(',')
    if output_file:
        ext = os.path.splitext(output_file)[1]
        if ext not in map_savers:
            raise ValueError(f'Unsupported file type: {ext}')
        saver = map_savers[ext]
    for input_file in input_files:
        ic(input_file)
        if not os.path.exists(input_file):
            raise FileNotFoundError(f'File not found: {input_file}')
        ext = os.path.splitext(input_file)[1]
        ic(ext)
        if ext not in map_loaders:
            raise ValueError(f'Unsupported file type: {ext}')
        df = map_loaders[ext](input_file)
        #ic(df)
        ic(len(df))
        ic(df.columns)
        ic(df.iloc[0])
        if '__file__' not in df.columns:
            df['__file__'] = input_file
        if column_map:
            df = remap_df(df, column_map)
        if list_fields_split_by_newline:
            df = apply_fields_split_by_newline(df, list_fields_split_by_newline)
        df_list.append(df)
    all_df = pd.concat(df_list)
    #ic(all_df)
    ic(len(all_df))
    ic(all_df.columns)
    ic(all_df.iloc[0])
    if output_file:
        ic('Saing to: ', output_file)
        saver(all_df, output_file)
