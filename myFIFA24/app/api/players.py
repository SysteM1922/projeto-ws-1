import json
from utils import select

def get_players_by_prop(start: int = 0, limit: int = 100, ascending: bool = False, props: dict = None) -> list[dict]:
    order = "ASC" if ascending else "DESC"

    name = ""
    gender = ""
    nationality = ""
    team = ""
    position = ""
    extra_position = ""

    if props: 
        match props["prop"]:
            case "name":
                name += f'FILTER REGEX(?name, "{props["value"]}", "i")'
            case "nationality":
                nationality += f'FILTER(?nationalityid = <{props["value"]}>)'
            case "league":
                team = f'?teamid fifatp:league <{props["value"]}> .'
            case "team":
                team = f'FILTER(?teamid = <{props["value"]}>)'
            case "gender":
                gender = f'FILTER(?genderid = <{props["value"]}>)'
            case "position":
                position = f'FILTER(?positionid = <{props["value"]}>)'
                extra_position = f"""UNION {{
                ?playerid fifaplp:gender ?genderid .
                ?genderid fifagp:label ?gender .
                ?playerid fifaplp:altPos <{props["value"]}> .
                ?playerid fifaplp:position ?positionid .
                ?positionid fifapop:shortLabel ?position .
                ?playerid fifaplp:nationality ?nationalityid .
                ?nationalityid fifanp:label ?nationality .
                ?playerid fifaplp:team ?teamid .
                ?teamid fifatp:imageUrl ?team .
                ?playerid fifaplp:overallRating ?ovr .
                ?playerid fifaplp:firstName ?fName .
                ?playerid fifaplp:lastName ?lName .
                OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
                BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
                ?playerid fifaplp:skillMoves ?skills .
                ?playerid fifaplp:weakFootAbility ?weakfoot .
                ?playerid fifaplp:attackingWorkRate ?attwr .
                ?playerid fifaplp:defensiveWorkRate ?defwr .
                ?playerid fifaplp:stat ?stat .
                }}"""  

    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>
        PREFIX fifanp: <http://fifa24/nationality/pred/>
        PREFIX fifatp: <http://fifa24/team/pred/>
        PREFIX fifapop: <http://fifa24/position/pred/>
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?playerid ?name ?nationality ?team ?position ?ovr ?gender ?image ?skills ?weakfoot ?attwr ?defwr (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
        WHERE {{
            {{
            ?playerid fifaplp:gender ?genderid .
            {gender}
            ?genderid fifagp:label ?gender .
            ?playerid fifaplp:position ?positionid .
            {position}
            ?positionid fifapop:shortLabel ?position .
            ?playerid fifaplp:nationality ?nationalityid .
            {nationality}
            ?nationalityid fifanp:label ?nationality .
            ?playerid fifaplp:team ?teamid .
            {team}
            ?teamid fifatp:imageUrl ?team .
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            {name}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            ?playerid fifaplp:skillMoves ?skills .
            ?playerid fifaplp:weakFootAbility ?weakfoot .
            ?playerid fifaplp:attackingWorkRate ?attwr .
            ?playerid fifaplp:defensiveWorkRate ?defwr .
            ?playerid fifaplp:avatarUrl ?image .
            ?playerid fifaplp:stat ?stat .
            }}
            {extra_position}
        }}
        GROUP BY ?playerid ?name ?nationality ?team ?position ?ovr ?gender ?image ?skills ?weakfoot ?attwr ?defwr
        ORDER BY {order}(?ovr) ?name
        OFFSET {start}
        LIMIT {limit}
        """

    result = select(query)

    for player in result:
        player["stats"] = json.loads(player["stats"])

    return result

def get_player_by_guid(guid: str) -> dict:
    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>
        PREFIX fifanp: <http://fifa24/nationality/pred/>
        PREFIX fifatp: <http://fifa24/team/pred/>
        PREFIX fifapop: <http://fifa24/position/pred/>
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?playerid ?name ?nationality ?team ?position ?ovr ?gender ?card (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
        WHERE {{
            ?playerid fifaplp:gender ?genderid .
            FILTER(?playerid = <{guid}>)
            ?genderid fifagp:label ?gender .
            ?playerid fifaplp:position ?positionid .
            ?positionid fifapop:shortLabel ?position .
            ?playerid fifaplp:nationality ?nationalityid .
            ?nationalityid fifanp:label ?nationality .
            ?playerid fifaplp:team ?teamid .
            ?teamid fifatp:imageUrl ?team .
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            ?playerid fifaplp:shieldUrl ?card .
            ?playerid fifaplp:stat ?stat .
        }}
        GROUP BY ?playerid ?name ?nationality ?team ?position ?ovr ?gender ?card
        """

    result = select(query)

    if not result:
        return None
    
    player = result[0]
    player["stats"] = json.loads(player["stats"])

    return player

def get_players_by_team_guid(guid: str) -> list[dict]:
    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>
        PREFIX fifanp: <http://fifa24/nationality/pred/>
        PREFIX fifatp: <http://fifa24/team/pred/>
        PREFIX fifapop: <http://fifa24/position/pred/>
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?playerid ?name ?nationality ?position ?ovr ?gender ?image (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
        WHERE {{
            ?playerid fifaplp:gender ?genderid .
            ?genderid fifagp:label ?gender .
            ?playerid fifaplp:position ?positionid .
            ?positionid fifapop:shortLabel ?position .
            ?playerid fifaplp:nationality ?nationalityid .
            ?nationalityid fifanp:label ?nationality .
            ?playerid fifaplp:team ?teamid .
            FILTER(?teamid = <{guid}>)
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            ?playerid fifaplp:avatarUrl ?image .
            ?playerid fifaplp:stat ?stat .
        }}
        GROUP BY ?playerid ?name ?nationality ?position ?ovr ?gender ?image
        """
    
    result = select(query)

    for player in result:
        player["stats"] = json.loads(player["stats"])

    return result

def get_players_base_info_by_name(name: str) -> dict:
    query = f"""
        PREFIX fifaplp: <http://fifa24/player/pred/>

        SELECT ?playerid ?name ?ovr ?image
        WHERE {{
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            FILTER REGEX(?name, "{name}", "i")
            ?playerid fifaplp:avatarUrl ?image .
        }}
        """
    
    return select(query)
