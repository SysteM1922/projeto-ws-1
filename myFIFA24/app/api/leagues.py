from .utils import select

def get_leagues() -> list[dict]:
    query = """
    PREFIX fifalg: <http://fifa24/league/guid/> 
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?label ?image
    WHERE {
	    ?league fifalp:label ?label .
	    ?league fifalp:imageUrl ?image .
    }
    ORDER BY ?label
    """

    return select(query)


def get_leagues_by_name(name: str) -> dict:
    query = f"""
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT ?league ?label ?image
    WHERE {{
        ?league fifalp:label ?label .
        FILTER regex(?label, "{name}", "i")
        ?league fifalp:imageUrl ?image .
    }}
    ORDER BY ?label
    """

    return select(query)


def get_league_by_guid(guid: str) -> dict:
    query = f"""
    PREFIX fifalg: <http://fifa24/league/guid/>
    PREFIX fifalp: <http://fifa24/league/pred/>

    SELECT  ?league ?label ?image
    WHERE {{
        ?league fifalp:label ?label .
        FILTER (?league = <{guid}>)
        ?league fifalp:imageUrl ?image .
    }}
    """

    return select(query)