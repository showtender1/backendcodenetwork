from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Game state
state = {
    "turn": 1,  # 1 for North Korea, 2 for USA
    "north_korea": {
        "health": 10,
        "special_items": {
            "KN25": 0,  # Basic missile used count
            "Hwasong18": 0,  # Limited to 1
            "P18_radar": 0  # Limited to 3
        },
        "submarine": True
    },
    "usa": {
        "health": 10,
        "special_items": {
            "MinutemanIII": 0,  # Basic missile used count
            "B83": False,  # Used flag
            "AGM45": False,  # Used flag
            "Tomahawk": 0  # Limited to 3
        },
        "radar": 0  # Limited to 2
    },
    "log": [],  # Logs actions and results for debugging
}

# Determine winner based on conditions
def determine_winner():
    if state["north_korea"]["health"] <= 0:
        if state["usa"]["health"] == 10:
            return "/UW1"  # No damage taken
        elif state["log"][-1]["action"] == "tomahawk":
            return "/UW2"  # Tomahawk reflection
        elif state["log"][-1]["action"] == "B83":
            return "/UW4"  # Nuclear strike
        else:
            return "/UW3"  # General victory
    if state["usa"]["health"] <= 0:
        if state["north_korea"]["health"] == 10:
            return "/NW1"  # No damage taken
        elif state["log"][-1]["action"] == "Hwasong18":
            return "/NW2"  # Nuclear strike
        elif state["log"][-1]["action"] == "KN25":
            return "/NW3"  # KN25 finish
    if state["turn"] > 20:
        if state["north_korea"]["health"] > state["usa"]["health"]:
            return "/NW1"  # Higher health
        return "/UW3"  # Higher health
    return None

# Routes for game pages
@app.route("/")
def team_select():
    return render_template("TeamSelect.html")

@app.route("/NK_DESC")
def nk_desc():
    return render_template("NK_DESC.html")

@app.route("/US_DESC")
def us_desc():
    return render_template("US_DESC.html")

@app.route("/NKATTACK")
def nk_attack():
    return render_template("NKATTACK.html")

@app.route("/USATK")
def us_attack():
    return render_template("USATK.html")

@app.route("/NKDEFEND")
def nk_defend():
    return render_template("NKDEFEND.html")

@app.route("/USDEF")
def us_defend():
    return render_template("USDEF.html")

@app.route("/NK_Load")
def nk_load():
    return render_template("NK_Load.html")

@app.route("/US_Load")
def us_load():
    return render_template("US_Load.html")

# Victory routes
@app.route("/UW1")
def uw1():
    return render_template("UW1.html")

@app.route("/UW2")
def uw2():
    return render_template("UW2.html")

@app.route("/UW3")
def uw3():
    return render_template("UW3.html")

@app.route("/UW4")
def uw4():
    return render_template("UW4.html")

@app.route("/NW1")
def nw1():
    return render_template("NW1.html")

@app.route("/NW2")
def nw2():
    return render_template("NW2.html")

@app.route("/NW3")
def nw3():
    return render_template("NW3.html")

# Action endpoint for game logic
@app.route("/action", methods=["POST"])
def action():
    data = request.json
    player = data.get("player")
    action_type = data.get("action")
    target = data.get("target")  # Optional target for attacks

    if player not in ["north_korea", "usa"]:
        return jsonify({"error": "Invalid player."}), 400

    # Check turn
    if (state["turn"] % 2 == 1 and player != "north_korea") or \
       (state["turn"] % 2 == 0 and player != "usa"):
        return jsonify({"error": "Not your turn."}), 400

    # Process action
    if action_type == "attack":
        if player == "north_korea":
            state["usa"]["health"] -= 1
        elif player == "usa":
            state["north_korea"]["health"] -= 1

    elif action_type in ["Hwasong18", "B83"]:
        if player == "north_korea" and action_type == "Hwasong18" and state["north_korea"]["special_items"]["Hwasong18"] == 0:
            state["usa"]["health"] -= 2
            state["north_korea"]["special_items"]["Hwasong18"] = 1
        elif player == "usa" and action_type == "B83" and not state["usa"]["special_items"]["B83"]:
            state["north_korea"]["health"] = 0
            state["usa"]["special_items"]["B83"] = True

    elif action_type == "KN25":
        state["usa"]["health"] -= 1
        state["north_korea"]["special_items"]["KN25"] += 1

    # Log the action
    state["log"].append({"player": player, "action": action_type, "target": target})
    state["turn"] += 1

    # Check for victory
    winner = determine_winner()
    if winner:
        return jsonify({"redirect": winner})

    return jsonify({"status": "Action processed", "state": state})

@app.route("/reset", methods=["POST"])
def reset():
    global state
    state = {
        "turn": 1,
        "north_korea": {
            "health": 10,
            "special_items": {"KN25": 0, "Hwasong18": 0, "P18_radar": 0},
            "submarine": True
        },
        "usa": {
            "health": 10,
            "special_items": {"MinutemanIII": 0, "B83": False, "AGM45": False, "Tomahawk": 0},
            "radar": 0
        },
        "log": [],
    }
    return jsonify({"status": "Game reset", "state": state})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
