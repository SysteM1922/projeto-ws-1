import json
from utils import query as make_query


def get_leagues() -> list[dict]:
    query = """
    PREFIX fifalg: <http://fifa24/league/guid/> 
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?leagueLabel ?leagueURL
    WHERE {
	    ?league fifalp:label ?leagueLabel .
	    ?league fifalp:imageUrl ?leagueURL
    }"""

    result = make_query(query)

    return result


def get_leagues_by_name(name: str) -> dict:
    query = f"""
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?leagueLabel ?leagueURL
    WHERE {{
        ?league fifalp:label ?leagueLabel .
        ?league fifalp:imageUrl ?leagueURL
        FILTER regex(?leagueLabel, "{name}", "i")
    }}"""

    result = make_query(query)

    return result


def get_league_by_guid(guid: str) -> dict:
    query = f"""
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT  ?league ?leagueLabel ?leagueURL
    WHERE {{
        ?league fifalp:label ?leagueLabel .
        ?league fifalp:imageUrl ?leagueURL .
        FILTER (?league = <{guid}>)
    }}"""

    result = make_query(query)

    return result


def main():
    print(get_league_by_guid("http://fifa24/league/guid/1"))


if __name__ == "__main__":
    main()
