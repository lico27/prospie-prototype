from src.database_builder import get_data

if __name__ == "__main__":
    funders, funder_beneficiaries, beneficiaries, funder_causes, causes, funder_areas, areas = get_data()

    print(funders.head())