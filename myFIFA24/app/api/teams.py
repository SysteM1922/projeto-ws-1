import json
from .utils import select

def get_teams() -> list[dict]:
    query = """
    PREFIX fifatp: <http://fifa24/team/pred/>
    PREFIX fifalp: <http://fifa24/league/pred/>


    SELECT ?teamId ?teamLabel ?teamImage ?leagueId ?leagueLabel ?leagueImage
    WHERE {
    	?teamId fifatp:label ?teamLabel .
        ?teamId fifatp:league ?leagueId .
        ?teamId fifatp:imageUrl ?teamImage .
        ?leagueId fifalp:label ?leagueLabel .
        ?leagueId fifalp:imageUrl ?leagueImage .
    }
    ORDER BY ?leagueLabel ?teamLabel
    """

    result = select(query)

    ret = []
    leagues = {}

    for team in result:
        league_id = team["leagueId"]
        if league_id not in leagues:
            leagues[league_id] = {
                "id": league_id,
                "label": team["leagueLabel"],
                "image": team["leagueImage"],
                "teams": []
            }

        leagues[league_id]["teams"].append({
            "id": team["teamId"],
            "label": team["teamLabel"],
            "image": team["teamImage"]
        })

    for league in leagues.values():
        ret.append(league)

    return ret


def get_team_by_guid(guid: str) -> dict:
    query = f"""
    PREFIX fifatg: <http://fifa24/team/guid/> 
    PREFIX fifatp: <http://fifa24/team/pred/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?team ?teamLabel ?teamURL ?teamLeague ?teamLeagueLabel ?teamLeagueURL
    WHERE {{
        ?team fifatp:label ?teamLabel .
        FILTER (?team = <{guid}>)
        ?team fifatp:league ?teamLeague .
        ?team fifatp:imageUrl ?teamURL .
        ?teamLeague fifalp:label ?teamLeagueLabel .
        ?teamLeague fifalp:imageUrl ?teamLeagueURL .
    }}"""

    return select(query)


def get_teams_by_league_guid(guid: str) -> list[dict]:
    query = f"""
    PREFIX fifatg: <http://fifa24/team/guid/>
    PREFIX fifatp: <http://fifa24/team/pred/>
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?team ?label ?image
    WHERE {{
        ?team fifatp:label ?label .
        ?team fifatp:league ?league .
        FILTER (?league = fifalg:{guid})
        ?team fifatp:imageUrl ?image .
    }}
    ORDER BY ?label
    """

    result = select(query)

    for team in result:
        team["id"] = team["team"].split("/")[-1]

    return result
