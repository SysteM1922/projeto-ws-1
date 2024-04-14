from utils import select, update, ask

def get_squads_by_user_id(user_id: str) -> list[dict]:
    query = f"""
    PREFIX fifasqp: <http://fifa24/squad/pred/>

    SELECT ?squadId ?name ?formation
    WHERE {{
        ?squad fifasqp:userId "{user_id}"^^xsd:string .
        ?squad fifasqp:name ?name .
        ?squad fifasqp:formation ?formation .
    }}
    ORDER BY ?name
    """

    return select(query)

def get_squad_by_guid(guid: str) -> dict:
    query = f"""
    PREFIX fifasqp: <http://fifa24/squad/pred/>
    PREFIX fifaspp: <http://fifa24/squad_player/pred/>

    SELECT ?name ?formation ?playerId ?playerShield ?playerPos ?squadPlayerId
    WHERE {{
        <{guid}> fifasqp:name ?name .
        <{guid}> fifasqp:formation ?formation .
        <{guid}> fifaspp:player ?squadPlayerId .
        ?squadPlayerId fifaspp:player ?playerId .
        ?squadPlayerId fifaspp:position ?playerPos .
        ?playerId fifaplp:shieldUrl ?playerShield .
    }}
    """

    result = select(query)

    if not result:
        return None
    
    squad = {
        "id": guid,
        "name": result[0]["name"],
        "formation": result[0]["formation"],
        "players": []
    }

    for player in result:
        squad["players"].append({
            "id": player["playerId"],
            "squadPlayerId": player["squadPlayerId"],
            "shield": player["playerShield"],
            "pos": player["playerPos"]
        })

    return sorted(squad["players"], key=lambda x: x["pos"])

def create_squad(user_id: str, squad: dict) -> dict:

    status = ask(f"ASK {{ <http://fifa24/squad/guid/1> ?p ?o }}")

    if status:
        return False

    squad_players = ""
    for player in squad["players"]:
        squad_players += f"fifasqg:{squad["id"]} fifasqp:player fifaspg:{squad["id"]+player["pos"]} .\n"
        squad_players += f"fifaspg:{squad["id"]+player["pos"]} fifaspp:player {player["id"]} .\n"
        squad_players += f"fifaspg:{squad["id"]+player["pos"]} fifaspp:position \"{player["pos"]}\"^^xsd:int .\n"

    query = f"""
    PREFIX fifasqg: <http://fifa24/squad/guid/>
    PREFIX fifasqp: <http://fifa24/squad/pred/>
    PREFIX fifaspg: <http://fifa24/squad_player/guid/>
    PREFIX fifaspp: <http://fifa24/squad_player/pred/>

    INSERT DATA {{
    	fifasqg:{squad["id"]} fifasqp:name "{squad["name"]}"^^xsd:string .
        fifasqg:{squad["id"]} fifasqp:formation "{squad["formation"]}"^^xsd:string .
        fifasqg:{squad["id"]} fifasqp:userId "{user_id}"^^xsd:string .
        {squad_players}
    }}
    """

    update(query)

    return ask(f"ASK {{ <http://fifa24/squad/guid/1> ?p ?o }}")

def update_squad(guid: str, squad: dict) -> dict:
    
    delete = ""
    insert = ""

    new_players = []
    old_players = []

    old_squad = get_squad_by_guid(guid)

    if not old_squad:
        return False
    
    for old_player, new_player in zip(old_squad["players"], squad["players"]):
        if old_player["id"] != new_player["id"]:
            old_players.append(old_player)
            new_players.append(new_player)

            delete += f"""
            {guid} fifasqp:player {old_player["squadPlayerId"]} .
            {old_player["squadPlayerId"]} ?p{old_player["pos"]} ?o{old_player["pos"]} .
            """
            if new_player["id"]:
                insert += f"""
                {guid} fifasqp:player fifaspg:{guid+new_player["pos"]} .
                {old_player["squadPlayerId"]} fifaspp:player {new_player["id"]} .
                {old_player["squadPlayerId"]} fifaspp:position "{new_player["pos"]}"^^xsd:int .
                """

    query = f"""
    PREFIX fifasqp: <http://fifa24/squad/pred/>
    PREFIX fifaspg: <http://fifa24/squad_player/guid/>
    PREFIX fifaspp: <http://fifa24/squad_player/pred/>

    DELETE {{
        {delete}
    }}
    WHERE {{
        {delete}
    }}
    INSERT DATA{{
        {insert}
    }}
    """

    update(query)

    query = ""

    for player in new_players:
        if not ask(f"ASK {{ <{player["squadPlayerId"]}> fifaspp:player <{player["id"]}> }}"):
            return False
        
    for player in old_players:
        if ask(f"ASK {{ <{player["squadPlayerId"]}> fifaspp:player <{player["id"]}> }}"):
            return False
        
    return True    

def delete_squad(guid: str) -> dict:
    query = f"""
    PREFIX fifasqp: <http://fifa24/squad/pred/>

    DELETE {{
        {guid} ?p1 ?o1 .
        ?squadPlayerId ?p2 ?o2 .
    }}
    WHERE {{
        {guid} ?p1 ?o1 .
        {guid} fifasqp:player ?squadPlayerId .
        ?squadPlayerId ?p2 ?o2 .
    }}
    """

    update(query)

    return not ask(f"ASK {{ <http://fifa24/squad/guid/1> ?p ?o }}")

