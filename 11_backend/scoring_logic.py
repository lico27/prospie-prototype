from backend_utils import get_name_from_id, get_id_from_name, get_granularity_weight, check_if_parent, calculate_similarity_score
import pandas as pd
import json
from datetime import datetime

def check_existing_relationship(grants_df, funder_num, user_num):
    """
    Checks if funder has ever given a grant to the user.
    """
    if grants_df.empty or "recipient_id" not in grants_df.columns:
        return False, 0, pd.DataFrame()

    relationship = grants_df[
        (grants_df["funder_num"] == funder_num) &
        (grants_df["recipient_id"] == user_num)
    ]

    num_grants = len(relationship)
    existing_relationship = num_grants > 0

    return existing_relationship, num_grants, relationship

def check_areas(funder_list, user_list, areas_df, hierarchies_df):
    """
    Calculates a score based on matches between the funder's and user's stated areas.
    """

    #convert names to ids
    funder_ids = [get_id_from_name(name, areas_df) for name in funder_list if get_id_from_name(name, areas_df) is not None]
    user_ids = [get_id_from_name(name, areas_df) for name in user_list if get_id_from_name(name, areas_df) is not None]
    
    #avoid zero division
    if len(user_ids) == 0:
        return 0.0, []
    
    #store ids as set and scores/reasoning as lists
    funder_set = set(funder_ids)
    scores = []
    reasoning = []
    
    for user_area in user_ids:
        user_area_name = get_name_from_id(user_area, areas_df)
        
        #check for exact match
        if user_area in funder_set:
            score = get_granularity_weight(user_area, areas_df) * 1.0
            scores.append(score)
            reasoning.append(f"Exact match: {user_area_name}")
        
        #check if user area is within funder area
        else:
            hierarchy_user_in_funder = None
            for funder_area in funder_ids:
                if check_if_parent(funder_area, user_area, hierarchies_df):
                    hierarchy_user_in_funder = funder_area
                    break
            
            if hierarchy_user_in_funder:
                parent_name = get_name_from_id(hierarchy_user_in_funder, areas_df)
                score = get_granularity_weight(hierarchy_user_in_funder, areas_df) * 0.6
                scores.append(score)
                reasoning.append(f"Hierarchical match: {user_area_name} (user) within {parent_name} (funder)")
            
            #check if funder area is within user area
            else:
                hierarchy_funder_in_user = None
                for funder_area in funder_ids:
                    if check_if_parent(user_area, funder_area, hierarchies_df):
                        hierarchy_funder_in_user = funder_area
                        break
                
                if hierarchy_funder_in_user:
                    child_name = get_name_from_id(hierarchy_funder_in_user, areas_df)
                    score = get_granularity_weight(user_area, areas_df) * 0.4
                    scores.append(score)
                    reasoning.append(f"Hierarchical match: {child_name} (funder) within {user_area_name} (user)")
                
                #no match
                else:
                    scores.append(0.0)
                    reasoning.append(f"No match: {user_area_name}")
    
    matched_scores = [s for s in scores if s > 0]
    if len(matched_scores) > 0:
        score = sum(matched_scores) / len(matched_scores)
    else:
        score = 0.0
    
    return max(0.0, score), reasoning

def check_beneficiaries(funder_list, user_list):
    """
    Calculates a score based on matches between the funder's and user's stated beneficiaries.
    """

    #define categories and filter
    high_level_bens = {"Other Defined Groups", "The General Public/mankind"}
    exclude_bens = {"Other Charities Or Voluntary Bodies"}
    funder_bens = [ben for ben in funder_list if ben not in exclude_bens]
    user_bens = [ben for ben in user_list if ben not in exclude_bens]
    
    #avoid zero division
    if len(user_bens) == 0:
        return 0.0, []
    
    #categorise funder beneficiaries
    funder_specific = set(ben for ben in funder_bens if ben not in high_level_bens)
    has_high_level = any(ben in high_level_bens for ben in funder_bens)
    
    scores = []
    reasoning = []
    for user_ben in user_bens:
        if user_ben in funder_specific:
            scores.append(1.0)
            reasoning.append(f"Exact match: {user_ben}")
        elif has_high_level:
            scores.append(0.2)
            reasoning.append(f"Weak match: user states '{user_ben}' and funder supports broad categories")
        else:
            scores.append(0.0)
            reasoning.append(f"No match: {user_ben}")
    
    matched_scores = [s for s in scores if s > 0]
    if len(matched_scores) > 0:
        score = sum(matched_scores) / len(matched_scores)
    else:
        score = 0.0

    return max(0.0, score), reasoning

def check_causes(funder_list, user_list):
    """
    Calculates a score based on matches between the funder's and user's stated causes.
    """
    #define categories and filter
    gcp = "General Charitable Purposes"
    exclude_causes = {"Other Charitable Purposes"}
    funder_causes = [cause for cause in funder_list if cause not in exclude_causes]
    user_causes = [cause for cause in user_list if cause not in exclude_causes]
    
    #avoid zero division
    if len(user_causes) == 0:
        return 0.0, [], False
    
    #categorise funder causes
    funder_specific = set(cause for cause in funder_causes if cause != gcp)
    has_gcp = gcp in funder_causes
    
    scores = []
    reasoning = []
    
    for user_cause in user_causes:
        if user_cause in funder_specific:
            scores.append(1.0)
            reasoning.append(f"Exact match: {user_cause}")
        else:
            scores.append(0.0)
            reasoning.append(f"No match: {user_cause}")
    
    matched_scores = [s for s in scores if s > 0]
    if len(matched_scores) > 0:
        score = sum(matched_scores) / len(matched_scores)
    else:
        score = 0.0
    
    return max(0.0, score), reasoning, has_gcp

def check_keywords(funder_keywords, user_keywords, model):
    """
    Calculates semantic similarity between funder (extracted) and user (inputted) keywords.
    """
    
    #parse json
    if pd.isna(funder_keywords) or funder_keywords is None or isinstance(funder_keywords, (int, float)):
        funder_keywords = []
    elif isinstance(funder_keywords, str):
        try:
            funder_keywords = json.loads(funder_keywords)
        except (json.JSONDecodeError, TypeError):
            funder_keywords = []

    if pd.isna(user_keywords) or user_keywords is None or isinstance(user_keywords, (int, float)):
        user_keywords = []
    elif isinstance(user_keywords, str):
        try:
            user_keywords = json.loads(user_keywords)
        except (json.JSONDecodeError, TypeError):
            user_keywords = []

    #handle empty lists
    if not funder_keywords:
        funder_keywords = []
    if not user_keywords:
        user_keywords = []
    
    if len(funder_keywords) == 0 or len(user_keywords) == 0:
        return 0.0, {}, ["No keywords to compare"], False
    
    #convert to lowercase
    funder_keywords = [kw.lower() for kw in funder_keywords]
    user_keywords = [kw.lower() for kw in user_keywords]

    #create embeddings for each keyword
    funder_keywords_em = {}
    for keyword in funder_keywords:
        embedding = model.encode(keyword)
        funder_keywords_em[keyword] = embedding

    user_keywords_em = {}
    for keyword in user_keywords:
        embedding = model.encode(keyword)
        user_keywords_em[keyword] = embedding

    #compare every funder keyword to every user keyword
    all_scores = []
    for funder_kw, funder_em in funder_keywords_em.items():
        for user_kw, user_em in user_keywords_em.items():
            similarity = calculate_similarity_score(funder_em, user_em)
            all_scores.append({
                "funder_keyword": funder_kw,
                "user_keyword": user_kw,
                "similarity": similarity
            })
    
    #sort and check for bonus (matches >= 0.9)
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    gets_bonus = any(match["similarity"] >= 0.90 for match in all_scores)
    
    #get dictionary of matches >= 0.90
    strong_matches = {}
    for match in all_scores:
        if match["similarity"] >= 0.90:
            key = f"{match['funder_keyword']} & {match['user_keyword']}"
            strong_matches[key] = match["similarity"]
    
    #filter to top 10 matches <= 0.90 and get average
    scores_under_80 = [match for match in all_scores if match["similarity"] < 0.90]
    top_10 = scores_under_80[:10]

    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0
    
    #build reasoning from medium matches
    reasoning = []
    for match in scores_under_80[:9]:
        reasoning.append(f"'{match['funder_keyword']}' & '{match['user_keyword']}': {match['similarity']:.3f}")
    
    return max(0.0, score), strong_matches, reasoning, gets_bonus

def check_name_rp(recipients_embedding_dict, user_embedding, user_name, grants_df=None):
    """
    Calculates semantic similarity between the user's name and the names of the funder's previous recipients.
    """

    #handle empty/nan
    score = 0.0
    reasoning = []

    #compare every recipient name to the user's name
    all_scores = []
    for recipient_name, recipient_embedding in recipients_embedding_dict.items():
        if recipient_name != user_name:
            similarity = calculate_similarity_score(recipient_embedding, user_embedding)
            all_scores.append({
                "recipient_name": recipient_name,
                "similarity": similarity
            })

    #sort and calculate average of top 10
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    top_10 = all_scores[:10]
    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0

    #build reasoning from top 10 matches
    reasoning = []
    for match in top_10:
        recipient_name = match["recipient_name"]
        reasoning_obj = {
            "recipient_name": recipient_name,
            "similarity": match["similarity"],
            "match_type": "name"
        }

        #add grant data if available
        if grants_df is not None and not grants_df.empty:
            recipient_grants = grants_df[grants_df["recipient_name"] == recipient_name]
            if not recipient_grants.empty:
                latest_grant = recipient_grants.iloc[0]
                reasoning_obj["year"] = int(latest_grant["year"]) if not pd.isna(latest_grant["year"]) else None
                reasoning_obj["amount"] = float(latest_grant["amount"]) if not pd.isna(latest_grant["amount"]) else None
                reasoning_obj["recipient_activities"] = latest_grant.get("recipient_activities")

        reasoning.append(reasoning_obj)

    return max(0.0, score), reasoning

def check_grants_rp(grants_embedding_dict, user_embedding, user_name):
    """
    Calculates semantic similarity between the user's text sections and the funder's previous grants.
    """

    #handle empty/nan
    score = 0.0
    reasoning = []

    #compare every grant to the user's text
    all_scores = []
    for grant_id, grant_data in grants_embedding_dict.items():
        grant_recipient_name = grant_data.get("recipient_name", "")
        grant_embedding = grant_data.get("embedding")

        if grant_recipient_name != user_name:
            similarity = calculate_similarity_score(grant_embedding, user_embedding)
            if similarity is not None and not pd.isna(similarity):
                all_scores.append({
                    "grant_id": grant_id,
                    "recipient_name": grant_recipient_name,
                    "grant_title": grant_data.get("grant_title"),
                    "grant_desc": grant_data.get("grant_desc"),
                    "year": grant_data.get("year"),
                    "amount": grant_data.get("amount"),
                    "similarity": similarity
                })

    #sort and calculate average of top 10
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    top_10 = all_scores[:10]
    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0

    #build reasoning from top 10 matches
    reasoning = []
    for match in top_10:
        year_val = match.get("year")
        amount_val = match.get("amount")

        reasoning.append({
            "grant_id": match["grant_id"],
            "recipient_name": match.get("recipient_name"),
            "grant_title": match.get("grant_title"),
            "grant_desc": match.get("grant_desc"),
            "year": int(year_val) if year_val and not pd.isna(year_val) else None,
            "amount": float(amount_val) if amount_val and not pd.isna(amount_val) else None,
            "similarity": match["similarity"]
        })

    return max(0.0, score), reasoning

def check_recipients_rp(recipients_embedding_dict, user_embedding, user_name, grants_df=None):
    """
    Calculates semantic similarity between the user's text sections and those of the funder's previous recipients.
    """

    #handle empty/nan
    score = 0.0
    reasoning = []

    #compare every recipient's text to the user's text
    all_scores = []
    for recipient_name, recipient_embedding in recipients_embedding_dict.items():
        if recipient_name != user_name:
            similarity = calculate_similarity_score(recipient_embedding, user_embedding)
            all_scores.append({
                "grant_recipient_name": recipient_name,
                "similarity": similarity
            })

    #sort and calculate average of top 10
    all_scores.sort(key=lambda x: x["similarity"], reverse=True)
    top_10 = all_scores[:10]
    if len(top_10) > 0:
        score = sum(match["similarity"] for match in top_10) / len(top_10)
    else:
        score = 0.0

    #build reasoning from top 10 matches
    reasoning = []
    for match in top_10:
        recipient_name = match["grant_recipient_name"]
        reasoning_obj = {
            "recipient_name": recipient_name,
            "similarity": match["similarity"],
            "match_type": "activities"
        }

        #add grant data if available
        if grants_df is not None and not grants_df.empty:
            recipient_grants = grants_df[grants_df["recipient_name"] == recipient_name]
            if not recipient_grants.empty:
                latest_grant = recipient_grants.iloc[0]
                reasoning_obj["year"] = int(latest_grant["year"]) if not pd.isna(latest_grant["year"]) else None
                reasoning_obj["amount"] = float(latest_grant["amount"]) if not pd.isna(latest_grant["amount"]) else None
                reasoning_obj["recipient_activities"] = latest_grant.get("recipient_activities")

        reasoning.append(reasoning_obj)

    return max(0.0, score), reasoning

def calculate_keywords_bonus(strong_matches, ukcat_df):
    """
    Calculates bonus based on keyword matches. Only runs if keywords with semantic scores above 0.8 exist.
    """

    #weight by specificity of ukcat level
    level_weights = {
        1: 0.4, 
        2: 0.8, 
        3: 1.0
    }
    
    weighted_scores = []
    for keyword, score in strong_matches.items():
        #find keyword in ukcat_df
        match = ukcat_df[ukcat_df["tag"].str.upper() == keyword.upper()]
        
        if not match.empty:
            level = match.iloc[0]["level"]
            weighted_score = score * level_weights.get(level, 1.0)
        else:
            weighted_score = score * 0.4
        
        weighted_scores.append(weighted_score)
    
    avg_weighted = sum(weighted_scores) / len(weighted_scores)
    
    #calculate bonus
    bonus = 1.1 + (avg_weighted * 0.2)
    bonus = min(max(bonus, 1.1), 1.3)
    
    return bonus

def calculate_relationship_bonus(relationship_df):
    """
    Calculates time since last grant and calculates a bonus. Only runs if there is a relationship.
    """

    #get time lapsed since last gift
    last_grant_year = relationship_df["year"].max()
    current_year = datetime.now().year
    time_lapsed = current_year - last_grant_year
    
    #assign bands
    if time_lapsed <= 2:
        bonus = 1.5
    elif time_lapsed <= 3:
        bonus = 1.4
    elif time_lapsed <= 5:
        bonus = 1.3
    elif time_lapsed <= 10:
        bonus = 1.2
    else:
        bonus = 1.1
    
    #add uplift for recurring relationship
    num_grants = len(relationship_df)
    if num_grants >= 5:
        bonus += 0.1
    
    return time_lapsed, bonus, last_grant_year

def calculate_areas_bonus_rp(funder_grants_df, user_areas, areas_df, hierarchies_df):
    """
    Calculates a bonus based on how well the user's areas match the funder's recipient's areas.
    """

    if funder_grants_df.empty:
        return 1.0, ["No grants history available"]

    #get unique areas from recipients
    all_areas = []
    for areas_list in funder_grants_df["recipient_areas"]:
        if isinstance(areas_list, list):
            all_areas.extend(areas_list)

    if len(all_areas) == 0:
        return 1.0, ["No area data available"]

    recipient_areas = list(set(all_areas))

    #check areas
    match_score, _ = check_areas(recipient_areas, user_areas, areas_df, hierarchies_df)

    #convert to bonus multiplier
    bonus = 1.0 + (match_score * 0.2)

    #get reasoning from top 10 (low level tiers only) + user matches
    area_count = {}
    for area_name in all_areas:
        area_id = get_id_from_name(area_name, areas_df)
        if area_id:
            granularity = get_granularity_weight(area_id, areas_df)
            if granularity >= 0.9:
                area_count[area_name] = area_count.get(area_name, 0) + 1

    if len(area_count) == 0:
        reasoning = ["Only broad geographic areas found"]
    else:
        sorted_areas = sorted(area_count.items(), key=lambda x: x[1], reverse=True)
        total_low_level = sum(area_count.values())

        #get top 10
        top_10_names = [name for name, _ in sorted_areas[:10]]

        #find user matches outside top 10
        user_matches_outside_top_10 = []
        if user_areas:
            user_areas_lower = [area.lower() for area in user_areas]
            for area_name, count in sorted_areas[10:]:
                if area_name.lower() in user_areas_lower:
                    percentage = (count / total_low_level) * 100
                    user_matches_outside_top_10.append(f"{area_name}: {count} grants ({percentage:.1f}%)")

        #build reasoning list
        reasoning = []
        for area_name, count in sorted_areas[:10]:
            percentage = (count / total_low_level) * 100
            reasoning.append(f"{area_name}: {count} grants ({percentage:.1f}%)")

        reasoning.extend(user_matches_outside_top_10)

    return bonus, reasoning

def calculate_keywords_bonus_rp(funder_grants_df, user_keywords):
    """
    Calculates a bonus based on exact keyword matches between user and funder's recipients.
    """

    if funder_grants_df.empty:
        return 1.0, ["No grants history available"]

    #parse json
    if pd.isna(user_keywords) or user_keywords is None or isinstance(user_keywords, (int, float)):
        user_keywords = []
    elif isinstance(user_keywords, str):
        try:
            user_keywords = json.loads(user_keywords)
        except (json.JSONDecodeError, TypeError):
            user_keywords = []

    if not user_keywords:
        user_keywords = []

    if len(user_keywords) == 0:
        return 1.0, ["No user keywords to match"]

    #get all recipient keywords
    all_recipient_keywords = []
    for recipient_keywords in funder_grants_df["recipient_extracted_class"]:
        if pd.isna(recipient_keywords) or recipient_keywords is None or isinstance(recipient_keywords, (int, float)):
            continue
        if isinstance(recipient_keywords, str):
            try:
                recipient_keywords = json.loads(recipient_keywords)
            except (json.JSONDecodeError, TypeError):
                continue
        if isinstance(recipient_keywords, list) and recipient_keywords:
            all_recipient_keywords.extend(recipient_keywords)

    if len(all_recipient_keywords) == 0:
        return 1.0, ["No recipient keywords available"]

    #find exact matches and count frequency
    matched_keywords = {}
    user_keywords_matched = set()

    for user_kw in user_keywords:
        if user_kw in all_recipient_keywords:
            user_keywords_matched.add(user_kw)
            matched_keywords[user_kw] = matched_keywords.get(user_kw, 0) + all_recipient_keywords.count(user_kw)

    #calculate match percentage
    match_percentage = len(user_keywords_matched) / len(user_keywords)

    #calculate bonus
    if match_percentage >= 0.9:
        bonus = 1.1
    elif match_percentage >= 0.5:
        bonus = 1.05
    else:
        bonus = 1.0 + (match_percentage * 0.2)

    #build reasoning from top 10
    if len(matched_keywords) == 0:
        reasoning = ["No exact keyword matches found"]
    else:
        sorted_matches = sorted(matched_keywords.items(), key=lambda x: x[1], reverse=True)

        reasoning = []
        for keyword, count in sorted_matches[:10]:
            reasoning.append(f"{keyword}: {count} times")

    return bonus, reasoning

def calculate_lv_penalty(funder_grants_df):
    """
    Identifies low variance in a funder's previous giving and calculates a penalty.
    """

    #skip funders with low or no giving history
    if funder_grants_df.empty or len(funder_grants_df) < 10 or "recipient_name" not in funder_grants_df.columns:
        return 1.0

    total_grants = len(funder_grants_df)
    unique_recipients = funder_grants_df['recipient_name'].nunique()
    
    #find proportion of grants to unique recipients
    variance_proportion = unique_recipients / total_grants
    
    #calculate penalty
    if variance_proportion < 0.3:
        penalty = 0.7
    else:
        penalty = 1.0
    
    return penalty

def get_scores_and_reasonings(pair_df, idx, grants_df, areas_df, hierarchies_df, model):
    """
    Calls all calculation functions to get scores and reasonings for each step.
    """

    #get funder's data
    funder_num = pair_df["funder_registered_num"].iloc[idx]
    funder_grants_df = grants_df[grants_df["funder_num"] == funder_num].copy()
    has_grants_data = not funder_grants_df.empty
    
    #1 check if funder has a single beneficiary
    is_sbf = pair_df["is_potential_sbf"].iloc[idx]

    #2 check if funder states no unsolicited applications
    is_nua = pair_df["is_nua"].iloc[idx]

    #3 check if funder is on the list
    is_on_list = pair_df["is_on_list"].iloc[idx]
    list_reasoning = set(pair_df["list_entries"].iloc[idx]) if is_on_list else None

    #4 check if funder has ever given a grant to applicant
    user_num = pair_df["user_id"].iloc[idx]
    existing_relationship, num_grants, relationship = check_existing_relationship(grants_df, funder_num, user_num)

    #5 get areas score
    funder_areas = pair_df["areas"].iloc[idx].copy()
    user_areas = pair_df["user_areas"].iloc[idx].copy()
    areas_score, areas_reasoning = check_areas(funder_areas, user_areas, areas_df, hierarchies_df)

    #6 get beneficiaries score
    funder_beneficiaries = pair_df["beneficiaries"].iloc[idx].copy()
    user_beneficiaries = pair_df["user_beneficiaries"].iloc[idx].copy()
    beneficiaries_score, beneficiaries_reasoning = check_beneficiaries(funder_beneficiaries, user_beneficiaries)

    #7 get causes score
    funder_causes = pair_df["causes"].iloc[idx].copy()
    user_causes = pair_df["user_causes"].iloc[idx].copy()
    causes_score, causes_reasoning, has_gcp = check_causes(funder_causes, user_causes)

    #8 get text semantic similarity score
    funder_embedding = pair_df["concat_em"].iloc[idx]
    user_embedding = pair_df["user_concat_em"].iloc[idx]
    text_similarity_score = calculate_similarity_score(funder_embedding, user_embedding)

    #9 get keyword semantic similarity score
    funder_keywords = pair_df["extracted_class"].iloc[idx]
    user_keywords = pair_df["user_extracted_class"].iloc[idx]
    keyword_similarity_score, keyword_strong_matches, keyword_reasoning, keyword_gets_bonus = check_keywords(funder_keywords, user_keywords, model)

    #10 get name (RP) semantic similarity score
    if not funder_grants_df.empty and "recipient_name" in funder_grants_df.columns:
        valid_name_embeddings = {}
        for name, embedding in zip(funder_grants_df["recipient_name"], funder_grants_df["recipient_name_em"]):
            if not pd.isna(embedding) and embedding is not None and not isinstance(embedding, (int, float)):
                valid_name_embeddings[name] = embedding

        user_name_em = pair_df["user_name_em"].iloc[idx]
        user_name = pair_df["user_name"].iloc[idx]
        name_rp_score, name_rp_reasoning = check_name_rp(valid_name_embeddings, user_name_em, user_name, funder_grants_df)
    else:
        name_rp_score = None
        name_rp_reasoning = None

    #11 get grants (RP) semantic similarity score
    if not funder_grants_df.empty and "grant_title" in funder_grants_df.columns:
        non_empty_grants = funder_grants_df[
            (funder_grants_df["grant_title"].notna() & (funder_grants_df["grant_title"] != "")) |
            (funder_grants_df["grant_desc"].notna() & (funder_grants_df["grant_desc"] != ""))
        ]
        valid_grant_embeddings = {}
        for idx_grant, row in non_empty_grants.iterrows():
            embedding = row.get("grant_concat_em")
            grant_id = row.get("grant_id")
            if not pd.isna(embedding) and embedding is not None and not isinstance(embedding, (int, float)) and grant_id:
                valid_grant_embeddings[grant_id] = {
                    "embedding": embedding,
                    "recipient_name": row.get("recipient_name"),
                    "grant_title": row.get("grant_title"),
                    "grant_desc": row.get("grant_desc"),
                    "year": row.get("year"),
                    "amount": row.get("amount")
                }

        user_concat_em = pair_df["user_concat_em"].iloc[idx]
        user_name = pair_df["user_name"].iloc[idx]
        grants_rp_score, grants_rp_reasoning = check_grants_rp(valid_grant_embeddings, user_concat_em, user_name)
    else:
        grants_rp_score = None
        grants_rp_reasoning = None

    #12 get recipients (RP) semantic similarity score
    if not funder_grants_df.empty and "recipient_name" in funder_grants_df.columns:
        valid_recipient_embeddings = {}
        for name, embedding in zip(funder_grants_df["recipient_name"], funder_grants_df["recipient_concat_em"]):
            if not pd.isna(embedding) and embedding is not None and not isinstance(embedding, (int, float)):
                valid_recipient_embeddings[name] = embedding

        user_concat_em = pair_df["user_concat_em"].iloc[idx]
        user_name = pair_df["user_name"].iloc[idx]
        recipients_rp_score, recipients_rp_reasoning = check_recipients_rp(valid_recipient_embeddings, user_concat_em, user_name, funder_grants_df)
    else:
        recipients_rp_score = None
        recipients_rp_reasoning = None

    #13 get sbf penalty
    sbf_penalty = 0.1 if is_sbf else 1.0

    #14 get nua penalty
    if existing_relationship:
        nua_penalty = 1.0
    else:
        nua_penalty = 0.2 if is_nua else 1.0       

    #15 get keywords bonus
    if keyword_strong_matches:
        ukcat_url = "https://raw.githubusercontent.com/lico27/ukcat/main/data/ukcat.csv"
        ukcat_df = pd.read_csv(ukcat_url)
        keywords_bonus = calculate_keywords_bonus(keyword_strong_matches, ukcat_df)
    else:
        keywords_bonus = 1.0

    #16 get relationship bonus
    if existing_relationship:
        time_lapsed, relationship_bonus, last_grant_year = calculate_relationship_bonus(relationship)
    else:
        time_lapsed = None
        relationship_bonus = 1.0
        last_grant_year = None

    #17 get gcp bonus
    gcp_bonus = 1.2 if has_gcp else 1.0

    #18 get areas (RP) bonus
    user_areas = pair_df["user_areas"].iloc[idx].copy()
    areas_rp_bonus, areas_rp_reasoning = calculate_areas_bonus_rp(funder_grants_df, user_areas, areas_df, hierarchies_df)

    #19 get keywords (RP) bonus
    user_keywords = pair_df["user_extracted_class"].iloc[idx]
    keywords_rp_bonus, keywords_rp_reasoning = calculate_keywords_bonus_rp(funder_grants_df, user_keywords)

    #20 get low variance penalty
    lv_penalty = calculate_lv_penalty(funder_grants_df)
    
    return (is_sbf, is_nua, is_on_list, list_reasoning, existing_relationship, num_grants, relationship, areas_score, areas_reasoning, 
            beneficiaries_score, beneficiaries_reasoning, causes_score, causes_reasoning, has_gcp, text_similarity_score,
            keyword_similarity_score, keyword_strong_matches, keyword_reasoning, keyword_gets_bonus, name_rp_score, name_rp_reasoning,
            grants_rp_score, grants_rp_reasoning, recipients_rp_score, recipients_rp_reasoning, sbf_penalty, nua_penalty, keywords_bonus,
            time_lapsed, relationship_bonus, last_grant_year, gcp_bonus, areas_rp_bonus, areas_rp_reasoning, keywords_rp_bonus, keywords_rp_reasoning, lv_penalty,
            has_grants_data
    )

def calculate_alignment_score(pair_df, idx, grants_df, areas_df, hierarchies_df, model):
    """
    Combines all 20 scoring steps to produce one final alignment score with reweighting to account for missing data where funders have no grants history.
    """

    #get scores
    result = get_scores_and_reasonings(pair_df, idx, grants_df, areas_df, hierarchies_df, model)
    
    #unpack score elements
    (is_sbf, is_nua, is_on_list, list_reasoning,
     existing_relationship, num_grants, relationship, areas_score,
     areas_reasoning, beneficiaries_score, beneficiaries_reasoning,
     causes_score, causes_reasoning, has_gcp, text_similarity_score,
     keyword_similarity_score, keyword_strong_matches, keyword_reasoning, keyword_gets_bonus,
     name_rp_score, name_rp_reasoning, grants_rp_score, grants_rp_reasoning,
     recipients_rp_score, recipients_rp_reasoning, sbf_penalty, nua_penalty, keywords_bonus,
     time_lapsed, relationship_bonus, last_grant_year, gcp_bonus, areas_rp_bonus, areas_rp_reasoning,
     keywords_rp_bonus, keywords_rp_reasoning, lv_penalty, has_grants_data) = result

    #define weights based on stated/revealsed
    sp_weights = {
        "areas": (areas_score, 0.08),
        "beneficiaries": (beneficiaries_score, 0.04),
        "causes": (causes_score, 0.02),
        "text_similarity": (text_similarity_score, 0.16),
        "keyword_similarity": (keyword_similarity_score, 0.11)
    }

    rp_weights = {
        "name_rp": (name_rp_score, 0.17),
        "grants_rp": (grants_rp_score, 0.21),
        "recipients_rp": (recipients_rp_score, 0.21)
    }

    #calculate scores with proportional reweighting
    if has_grants_data:
        #normal calculation when grants history exists
        weighted_scores = sum(score * weight for score, weight in sp_weights.values())
        weighted_scores += sum(score * weight for score, weight in rp_weights.values())
    else:
        #get total weights when no grants history
        sp_total = sum(weight for _, weight in sp_weights.values())
        rp_total = sum(weight for _, weight in rp_weights.values())

        #apply proportional reweighting
        reweight_proportion = (sp_total + rp_total) / sp_total
        weighted_scores = sum(score * weight * reweight_proportion for score, weight in sp_weights.values())
    
    final_score = (
        weighted_scores *
        sbf_penalty *
        nua_penalty *
        keywords_bonus *
        relationship_bonus *
        gcp_bonus *
        areas_rp_bonus *
        keywords_rp_bonus *
        lv_penalty
    )
    
    final_score = min(max(final_score, 0.05), 0.95)
    
    return final_score, {
      "is_sbf": bool(is_sbf),
      "is_nua": bool(is_nua),
      "is_on_list": bool(is_on_list),
      "list_reasoning": list(list_reasoning) if list_reasoning else None,
      "existing_relationship": bool(existing_relationship),
      "num_grants": int(num_grants),
      "areas_score": float(areas_score),
      "areas_reasoning": areas_reasoning,
      "beneficiaries_reasoning": beneficiaries_reasoning,
      "causes_reasoning": causes_reasoning,
      "has_gcp": bool(has_gcp),
      "text_similarity_score": float(text_similarity_score),
      "keyword_similarity_score": float(keyword_similarity_score),
      "keyword_strong_matches": keyword_strong_matches,
      "keyword_reasoning": keyword_reasoning,
      "name_rp_score": float(name_rp_score) if name_rp_score is not None else None,
      "name_rp_reasoning": name_rp_reasoning,
      "grants_rp_score": float(grants_rp_score) if grants_rp_score is not None else None,
      "grants_rp_reasoning": grants_rp_reasoning,
      "recipients_rp_score": float(recipients_rp_score) if recipients_rp_score is not None else None,
      "recipients_rp_reasoning": recipients_rp_reasoning,
      "time_lapsed": int(time_lapsed) if time_lapsed is not None else None,
      "last_grant_year": int(last_grant_year) if last_grant_year is not None else None,
      "areas_rp_bonus": float(areas_rp_bonus),
      "areas_rp_reasoning": areas_rp_reasoning,
      "keywords_rp_bonus": float(keywords_rp_bonus),
      "keywords_rp_reasoning": keywords_rp_reasoning,
      "lv_penalty": float(lv_penalty),
      "has_grants_data": bool(has_grants_data)
  }