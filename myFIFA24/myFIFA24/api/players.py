import json
from utils import query as make_query

def get_players_by_ovr(start: int = 0, limit: int = 1000, ascending: bool = False) -> list[dict]:
    order = "ASC" if ascending else "DESC"
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
    ORDER BY {order}(?ovr) ?name
    OFFSET {start}
    LIMIT {limit}
    """

    result = make_query(query)

    for player in result:
        player["stats"] = json.loads(player["stats"])

    return result

"""
def get_players_by_nationality(start: int = 0, limit: int = 1000, ascending: bool = False, nationality: str = None) -> list[dict]:
    order = "ASC" if ascending else "DESC"
    pass

def get_players_by_team(start: int = 0, limit: int = 1000, ascending: bool = False, team: str = None) -> list[dict]:
    order = "ASC" if ascending else "DESC"
    pass

def get_players_by_league(start: int = 0, limit: int = 1000, ascending: bool = False, league: str = None) -> list[dict]:
    order = "ASC" if ascending else "DESC"
    pass

def get_players_by_position(start: int = 0, limit: int = 1000, ascending: bool = False, positions: list[str] = None) -> list[dict]:
    order = "ASC" if ascending else "DESC"
    pass

def get_players_by_stat(start: int = 0, limit: int = 1000, ascending: bool = False, stat: str = None) -> list[dict]:
    order = "ASC" if ascending else "DESC"
    pass

def get_players_by_name(start: int = 0, limit: int = 1000, name: str = None) -> list[dict]:
    pass

This funstions should by grouped as filters for the get_players_by_ovr function.    
"""

def get_player_by_guid(guid: str) -> dict:
    pass

def get_players_by_team_guid(guid: str) -> list[dict]:
    pass

def get_players_base_info_by_name(name: str) -> dict:
    pass




