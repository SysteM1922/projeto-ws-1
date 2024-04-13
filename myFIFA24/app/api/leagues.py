from .utils import select

def get_leagues() -> list[dict]:
    query = """
    PREFIX fifalg: <http://fifa24/league/guid/> 
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?leagueLabel ?leagueURL
    WHERE {
	    ?league fifalp:label ?leagueLabel .
	    ?league fifalp:imageUrl ?leagueURL
    }"""

    return select(query)


def get_leagues_by_name(name: str) -> dict:
    query = f"""
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?leagueLabel ?leagueURL
    WHERE {{
        ?league fifalp:label ?leagueLabel .
        FILTER regex(?leagueLabel, "{name}", "i")
        ?league fifalp:imageUrl ?leagueURL .
    }}"""

    return select(query)


def get_league_by_guid(guid: str) -> dict:
    query = f"""
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT  ?league ?leagueLabel ?leagueURL
    WHERE {{
        ?league fifalp:label ?leagueLabel .
        FILTER (?league = <{guid}>)
        ?league fifalp:imageUrl ?leagueURL .
    }}"""

    return select(query)