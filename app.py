from flask import Flask, render_template, request, redirect, url_for, session
from simulator.engine import scenarios, simulate

app = Flask(__name__)
app.secret_key = "supersecurekey"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        scenario = request.form["scenario"]
        session["scenario"] = scenario
        return redirect(url_for("configure_counts"))
    return render_template("index.html", scenarios=scenarios)


@app.route("/configure", methods=["GET", "POST"])
def configure_counts():
    if "scenario" not in session:
        return redirect(url_for("index"))  # changed here

    if request.method == "POST":
        try:
            session["weapon_count"] = int(request.form["weapon_count"])
            session["target_count"] = int(request.form["target_count"])
            session["max_rounds"] = int(request.form["max_rounds"])
        except (KeyError, ValueError, TypeError):
            return "Invalid input", 400
        return redirect(url_for("select_units"))

    scenario = session["scenario"]
    return render_template("configure.html", scenario=scenario)


@app.route("/select_units", methods=["GET", "POST"])
def select_units():
    scenario = session.get("scenario")
    weapon_count = session.get("weapon_count")
    target_count = session.get("target_count")
    max_rounds = session.get("max_rounds", 500)  

    # Ensure counts are integers
    try:
        weapon_count = int(weapon_count)
        target_count = int(target_count)
    except (TypeError, ValueError):
        return redirect(url_for("configure_counts"))

    if not scenario:
        return redirect(url_for("index"))  # changed here

    available_weapons = scenarios[scenario]["available_weapons"]
    available_targets = scenarios[scenario]["available_targets"]

    if request.method == "POST":
        selected_weapons = request.form.getlist("weapons")
        selected_targets = request.form.getlist("targets")

        if len(selected_weapons) != weapon_count or len(selected_targets) != target_count:
            return "Please select the correct number of weapons and targets.", 400

        result_text, result_lines = simulate(scenario, selected_weapons, selected_targets, max_rounds)
        return render_template("result.html", result=result_text, lines=result_lines, scenario=scenario)


    return render_template(
        "select_units.html",
        weapon_count=weapon_count,
        target_count=target_count,
        available_weapons=available_weapons,
        available_targets=available_targets
    )


if __name__ == "__main__":
    app.run(debug=True)