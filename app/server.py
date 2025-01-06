from flask import Flask, render_template, request, redirect, url_for
from causal_solver.OptimizationInterface import OptimizationInterface
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nodeString = request.form.get("nodes")
        edgeString = request.form.get("edges")
        labelT = request.form.get("label1")
        valueT = request.form.get("value1")
        labelI = request.form.get("label2")
        valueI = request.form.get("value2")
        file = request.files.get("file")

        UPLOAD_FOLDER = 'uploads'
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        if file and file.filename:
            filepath: str = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            print(f"filepath: {filepath}")
        else:
            return "File not found or invalid", 400

        print(f"dbg early early: {labelI}")
        return redirect(url_for("display_graph", nodes=nodeString, edges=edgeString, filepath=filepath,
                                labelT=labelT,valueT=valueT,labelI=labelI,valueI=valueI))

    return render_template("index.html")

@app.route("/display_graph")
def display_graph():
    nodesStr = request.args.get("nodes")
    edgesStr = request.args.get("edges")
    filepath = request.args.get("filepath")
    labelTarget = request.args.get("labelT")
    valueTarget = request.args.get("valueT")
    labelIntervention = request.args.get("labelI")
    valueIntervention = request.args.get("valueI")

    qLow, qUpper = OptimizationInterface.optimizationProblem(fromInterface=True, nodesStr=nodesStr, edgesStr=edgesStr,
                                                             filepath=filepath,
                                                             labelTarget=labelTarget,
                                                             valueTarget=valueTarget,
                                                             labelIntervention=labelIntervention,
                                                             valueIntervention=valueIntervention)

    return render_template("display_graph.html", lowerBound=qLow, upperBound=qUpper)

if __name__ == "__main__":
    app.run(debug=True)
