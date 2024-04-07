import json
from utils import query as make_query

def display_players(start: int = 0, limit: int = 1000) -> dict:
    query = f"""
    PREFIX playerPred: <http://fifa24/player/pred/>
    PREFIX nationalityPred: <http://fifa24/nationality/pred/>
    PREFIX teamPred: <http://fifa24/team/pred/>
    PREFIX positionPred: <http://fifa24/position/pred/>
    PREFIX statPred: <http://fifa24/stat/pred/>
    
    SELECT ?playerid ?name ?nationality ?team ?position ?ovr (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
    WHERE {{
        ?playerid playerPred:overallRating ?ovr .
        ?playerid playerPred:firstName ?fName .
        ?playerid playerPred:lastName ?lName .
        OPTIONAL {{ ?playerid playerPred:commonName ?cName . }}
        BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
        ?playerid playerPred:nationality ?nationalityid .
        ?playerid playerPred:team ?teamid .
        ?teamid teamPred:imageUrl ?team .
        ?playerid playerPred:position ?positionid .
        ?positionid positionPred:shortLabel ?position .
        ?playerid playerPred:stat ?stat .
    }}
    GROUP BY ?playerid ?name ?nationality ?team ?position ?ovr
    ORDER BY DESC(?ovr) ?name
    OFFSET {start}
    LIMIT {limit}
    """

    result = make_query(query)

    for player in result:
        player["stats"] = json.loads(player["stats"])

    return result


