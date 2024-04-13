import json
from utils import select, ask
from unidecode import unidecode

def get_random_player() -> dict:
    query = """
    PREFIX fifaplp: <http://fifa24/player/pred/>
    PREFIX fifanp: <http://fifa24/nationality/pred/>
    PREFIX fifatp: <http://fifa24/team/pred/>
    PREFIX fifapop: <http://fifa24/position/pred/>

    SELECT ?playerid ?name ?nationality ?team ?position ?ovr ?image (CONCAT("{{",GROUP_CONCAT(?stat; separator=", "), "}}") AS ?stats)
    WHERE {
        ?playerid fifaplp:overallRating ?ovr .
        FILTER(?ovr > 74)
        ?playerid fifaplp:position ?positionid .
        ?positionid fifapop:shortLabel ?position .
        ?playerid fifaplp:nationality ?nationalityid .
        ?nationalityid fifanp:label ?nationality .
        ?playerid fifaplp:team ?teamid .
        ?teamid fifatp:imageUrl ?team .
        ?playerid fifaplp:firstName ?fName .
        ?playerid fifaplp:lastName ?lName .
        OPTIONAL {{ ?playerid fifaplp:commonName ?cName . }}
        BIND(COALESCE(?cName, CONCAT(?fName, " ", ?lName)) AS ?name)
        ?playerid fifaplp:shieldUrl ?image .
        ?playerid fifaplp:stat ?stat .
    }
    GROUP BY ?playerid ?name ?nationality ?team ?position ?ovr ?image

    """

def guess_stat(player_guid: str, stat: str, value: str) -> bool:
    
    if value.isdigit():
        obj = f"\"{value}\"^^xsd:int"
    else:
        if stat == "stat":
            obj = f"\"{value}\""

    if stat == "stat":
        args = f"<{player_guid}> fifaplp:{stat} {obj} ."
    elif stat == "ovr":
        args = f"<{player_guid}> fifaplp:overallRating {obj} ."
    elif stat == "name":
        return guess_name(player_guid, value)
    else:
        return False

    query = f"""
    PREFIX fifaplp: <http://fifa24/player/pred/>

    ASK {{
        {args}
    }}
    """

    return ask(query)

def guess_name(player_guid: str, name: str) -> bool:
    query = f"""
    PREFIX fifaplp: <http://fifa24/player/pred/>

    SELECt ?fName ?lName ?cName
    WHERE {{
        <{player_guid}> fifaplp:firstName ?fName .
        <{player_guid}> fifaplp:lastName ?lName .
        OPTIONAL {{ <{player_guid}> fifaplp:commonName ?cName . }}
    }}
    """

    result = select(query)[0]

    cName = None
    if "cName" in result:
        cName = unidecode(result["cName"])

    fName = unidecode(result["fName"])
    lName = unidecode(result["lName"])

    return name == fName or name == lName or (bool(cName) and name == cName)