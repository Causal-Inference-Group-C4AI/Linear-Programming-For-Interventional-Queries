from flask import Flask, render_template, request, redirect, url_for
from causal_solver.OptimizationInterface import OptimizationInterface

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nodeString = request.form.get("nodes")
        edgeString = request.form.get("edges")

        return redirect(url_for("display_graph", nodes=nodeString, edges=edgeString))

    return render_template("index.html")

@app.route("/display_graph")
def display_graph():
    nodesStr = request.args.get("nodes")
    edgesStr = request.args.get("edges")

    qLow, qUpper = OptimizationInterface.optimizationProblem(fromInterface=True, nodesStr=nodesStr, edgesStr=edgesStr)

    return render_template("display_graph.html", lowerBound=qLow, upperBound=qUpper)

if __name__ == "__main__":
    app.run(debug=True)
