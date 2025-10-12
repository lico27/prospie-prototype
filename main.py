from src.database_builder import get_data

if __name__ == "__main__":
    funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas, grants, funder_grants, recipient_grants, recipients, recipient_areas = get_data()

    for df in [funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas, grants, funder_grants, recipient_grants, recipients, recipient_areas]:
        print(df.head())