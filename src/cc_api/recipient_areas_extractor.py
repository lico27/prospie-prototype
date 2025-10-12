import pandas as pd
from .areas_table_builder import transform_area_columns

def build_areas_tables(df):

    areas, all_areas = transform_area_columns(df)

    #create unique ids for areas
    areas["area_id"] = range(401, 401 + len(areas))

    #build join table
    funder_areas = all_areas.merge(
        areas.rename(columns={"area_level": "area_type"}),
        on=["area_name", "area_type"]
    )[["registered_num", "area_id"]].drop_duplicates()
      
    return funder_areas, areas

