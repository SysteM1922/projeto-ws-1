import json
from .utils import select

def get_nationalities() -> list[dict]:
    query = """
        PREFIX fifanp: <http://fifa24/nationality/pred/>

        SELECT ?nationality ?label ?image
        WHERE {
            ?nationality fifanp:label ?label .
            ?nationality fifanp:imageUrl ?image .
        }
        ORDER BY ?label
        """
    
    result = select(query)

    for nationality in result:
        nationality["id"] = result["nationality"].split("/")[-1]

    return result

def get_genders() -> list[dict]:
    query = """
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?gender ?label
        WHERE {
            ?gender fifagp:label ?label .
        }
        ORDER BY ?label
        """
    
    result = select(query)

    for gender in result:
        gender["id"] = gender["gender"].split("/")[-1]

    return result

def get_positions() -> list[dict]:

    ret = {"defenders": {"GK": None,
                         "CB": None,
                         "RB": None,
                         "RWB": None,
                         "LB": None,
                         "LWB": None},
           "midfielders": {"CDM": None,
                           "CM": None,
                           "CAM": None,
                           "RM": None,
                           "LM": None,},
           "attackers": {"LW": None,
                         "RW": None,
                         "CF": None,
                         "ST": None}
                         }
    
    query = """
        PREFIX fifapop: <http://fifa24/position/pred/>

        SELECT ?positionid ?label
        WHERE {
            ?positionid fifapop:shortLabel ?label .
        }
        """
    
    result = select(query)

    for section in ret:
        for position in ret[section]:
            for pos in result:
                if pos["label"] == position:
                    ret[section][position] = pos["positionid"].split("/")[-1]

    return ret

def get_players_by_prop(start: int = 0, limit: int = 30, ascending: bool = None, props: dict = None) -> list[dict]:
    if ascending is None:
        order = "DESC(?ovr) ?name"
    else:
        if props["prop"] == "ovr":
            order = f'{"ASC" if ascending else "DESC"}(?ovr) ?name'
        elif props["prop"] == "name":
            order = f'{"ASC" if ascending else "DESC"}(?name) DESC(?ovr)'
        else:
            order = f'{"ASC" if ascending else "DESC"}(?{props["prop"]}) DESC(?ovr) ?name'

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
                ?nationalityid fifanp:imageUrl ?flag .
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

        SELECT ?playerid ?name ?flag ?team ?position ?ovr ?gender ?image ?skills ?weakfoot ?attwr ?defwr (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
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
            ?nationalityid fifanp:imageUrl ?flag .
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
        GROUP BY ?playerid ?name ?flag ?team ?position ?ovr ?gender ?image ?skills ?weakfoot ?attwr ?defwr
        ORDER BY {order}
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
        PREFIX fifatg: <http://fifa24/team/guid/>
        PREFIX fifatp: <http://fifa24/team/pred/>
        PREFIX fifapop: <http://fifa24/position/pred/>
        PREFIX fifagp: <http://fifa24/gender/pred/>

        SELECT ?playerid ?name ?nationality ?position ?ovr ?image ?skills ?weakfoot ?attwr ?defwr (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
        WHERE {{
            ?playerid fifaplp:position ?positionid .
            ?positionid fifapop:shortLabel ?position .
            ?playerid fifaplp:nationality ?nationalityid .
            ?nationalityid fifanp:imageUrl ?nationality .
            ?playerid fifaplp:team ?teamid .
            FILTER(?teamid = fifatg:{guid})
            ?playerid fifaplp:overallRating ?ovr .
            ?playerid fifaplp:firstName ?fName .
            ?playerid fifaplp:lastName ?lName .
            OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
            BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
            ?playerid fifaplp:skillMoves ?skills .
            ?playerid fifaplp:weakFootAbility ?weakfoot .
            ?playerid fifaplp:attackingWorkRate ?attwr .
            ?playerid fifaplp:defensiveWorkRate ?defwr .
            ?playerid fifaplp:avatarUrl ?image .
            ?playerid fifaplp:stat ?stat .
        }}
        GROUP BY ?playerid ?name ?nationality ?position ?ovr ?image ?skills ?weakfoot ?attwr ?defwr
        ORDER BY DESC(?ovr) ?name
        """
    
    result = select(query)

    for player in result:
        player["id"] = player["playerid"].split("/")[-1]
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
