import pandas as pd

def build_areas_tables(df):
    # Define expected columns for each area type
    expected_columns = {
        'country_continent': ['country', 'continent'],
        'local_authority': ['local_authority', 'metropolitan_county'],
        'region': ['region']
    }
    
    # Helper function to ensure columns exist
    def normalize_and_ensure_columns(df_exploded, col_name, expected_cols):
        normalized_df = pd.json_normalize(df_exploded[col_name])
        
        # If DataFrame is empty or missing expected columns, add them
        for expected_col in expected_cols:
            if expected_col not in normalized_df.columns:
                normalized_df[expected_col] = None
        
        # Ensure only expected columns are present (in case there are extras)
        normalized_df = normalized_df.reindex(columns=expected_cols)
        normalized_df.columns = ['area_' + col for col in normalized_df.columns]
        
        return normalized_df
    
    # Explode and normalize area lists
    exploded_df_country_continent = df.explode("country_continent")
    country_continent_df = normalize_and_ensure_columns(
        exploded_df_country_continent, "country_continent", 
        expected_columns['country_continent']
    )

    exploded_df_local_authority = df.explode("local_authority")
    local_authority_df = normalize_and_ensure_columns(
        exploded_df_local_authority, "local_authority", 
        expected_columns['local_authority']
    )

    exploded_df_region = df.explode("region")
    region_df = normalize_and_ensure_columns(
        exploded_df_region, "region", 
        expected_columns['region']
    )

    # Reset indexes and combine
    exploded_df_country_continent = exploded_df_country_continent.reset_index(drop=True)
    country_continent_df = country_continent_df.reset_index(drop=True)

    exploded_df_local_authority = exploded_df_local_authority.reset_index(drop=True)
    local_authority_df = local_authority_df.reset_index(drop=True)

    exploded_df_region = exploded_df_region.reset_index(drop=True)
    region_df = region_df.reset_index(drop=True)

    areas_df = pd.concat([exploded_df_country_continent, country_continent_df, 
                          local_authority_df, region_df], axis=1)

    # Drop unnecessary columns and rows
    areas_df = areas_df.drop(columns=["name", "website", "activities", "objectives", 
                                      "income", "expenditure", "classifications", 
                                      "country_continent", "local_authority", "region", 
                                      "area_welsh_ind"], errors='ignore')
    areas_df.columns = [col.replace("area_", "") for col in areas_df.columns]

    area_columns = ["country", "continent", "region", "local_authority", "metropolitan_county"]

    for col in area_columns:
        if col in areas_df.columns:
            areas_df[col] = areas_df[col].apply(lambda x: None if x == [] or pd.isna(x) else x)

    area_types = {
        "local_authority": "local_authority",
        "metropolitan_county": "metropolitan_county",
        "region": "region",
        "country": "country",
        "continent": "continent"
    }

    areas = []
    for _, row in areas_df.iterrows():
        for column, area_type in area_types.items():
            if column in areas_df.columns and pd.notna(row[column]) and row[column]:
                areas.append({
                    "registered_num": row["registered_num"],
                    "area_name": row[column],
                    "area_type": area_type
                })

    # Create full dataframe with all records
    all_areas = pd.DataFrame(areas)

    # Create unique areas table (no registered_num, no duplicates)
    areas = all_areas[["area_name", "area_type"]].drop_duplicates().reset_index(drop=True)
    areas = areas.rename(columns={"area_type": "area_level"})
    areas["area_id"] = range(401, 401 + len(areas))

    # Create funder_areas by merging back
    funder_areas = all_areas.merge(
        areas.rename(columns={"area_level": "area_type"}),
        on=["area_name", "area_type"]
    )[["registered_num", "area_id"]]
      
    return funder_areas, areas