from src.database_builder import get_data

if __name__ == "__main__":
    funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas, grants, funder_grants, recipients, recipient_grants, recipient_areas = get_data()

    for df in [funders, beneficiaries, funder_beneficiaries, causes, funder_causes, areas, funder_areas, grants, funder_grants, recipients, recipient_grants, recipient_areas]:
        print(df.head(20))

    