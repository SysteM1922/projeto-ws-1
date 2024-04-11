import json
from utils import query as make_query


def get_teams() -> list[dict]:
    query = """
    PREFIX fifatp: <http://fifa24/team/pred/>
    PREFIX fifalp: <http://fifa24/league/pred/>


    SELECT ?teamId ?teamLabel ?teamURL ?teamLeague ?teamLeagueLabel ?teamLeagueURL
    WHERE {
    	?teamId fifatp:label ?teamLabel .
        ?teamId fifatp:league ?teamLeague .
        ?teamId fifatp:imageUrl ?teamURL .
        ?teamLeague fifalp:label ?teamLeagueLabel .
        ?teamLeague fifalp:imageUrl ?teamLeagueURL
    }"""

    result = make_query(query)

    return result


def get_teams_by_name(name: str) -> dict:
    query = f"""
    PREFIX fifatp: <http://fifa24/team/pred/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?teamId ?teamLabel ?teamURL ?teamLeague ?teamLeagueLabel ?teamLeagueURL  
    WHERE {{
        ?teamId fifatp:label ?teamLabel .
        FILTER regex(?teamLabel, "{name}", "i")
        ?teamId fifatp:league ?teamLeague .
        ?teamId fifatp:imageUrl ?teamURL .
        ?teamLeague fifalp:label ?teamLeagueLabel .
        ?teamLeague fifalp:imageUrl ?teamLeagueURL
    }}"""

    result = make_query(query)

    return result


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

    result = make_query(query)

    return result


def get_teams_by_league_guid(guid: str) -> list[dict]:
    query = f"""
    PREFIX fifatg: <http://fifa24/team/guid/>
    PREFIX fifatp: <http://fifa24/team/pred/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?teamId ?teamLabel ?teamURL ?teamLeague ?teamLeagueLabel ?teamLeagueURL
    WHERE {{
        ?teamId fifatp:label ?teamLabel .
        ?teamId fifatp:league ?teamLeague .
        FILTER (?teamLeague = <{guid}>)
        ?teamId fifatp:imageUrl ?teamURL .
        ?teamLeague fifalp:label ?teamLeagueLabel .
        ?teamLeague fifalp:imageUrl ?teamLeagueURL
    }}"""

    result = make_query(query)

    return result
