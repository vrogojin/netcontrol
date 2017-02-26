# aggregates all the data we have
from __future__ import division
import sqlite3
import pickle

db_names = [
    "tests1000/d2/results.db", "tests1000/d3/results.db", "tests1000/d4/results.db", "tests1000/d5/results.db", "tests1000/d6/results.db", "tests1000/d7/results.db",
    "tests100/d2/results.db", "tests100/d3/results.db", "tests100/d4/results.db", "tests100/d5/results.db", "tests100/d6/results.db", 
    "DATA/tests/d2/results.db", "DATA/tests/d3/results.db", "DATA/tests/d4/results.db", "DATA/tests/d5/results.db", #"DATA/tests/d6/results.db",     
    ]
names = ["graph_id", "nodes", "edges", "full_driver", "full_driven", "targets_id", "targets", "heuristics", 
    "min_driven", "avg_driven", "max_driven", "min_time", "avg_time", "max_time"]

print "reading raw data...",
raw_data = {}
for db_name in db_names:
    with sqlite3.connect(db_name) as connection:
        c = connection.cursor()
        raw_data[db_name] = c.execute(
            """SELECT runs.graph_id AS graph_id, 
                      graphs.nodes AS nodes,
                      graphs.edges AS edges,
                      graphs.full_driver AS full_driver,
                      graphs.full_driven AS full_driven,
                      runs.targets_id AS targets_id,
                      targets.target AS targets,
                      runs.cut_to_driven || runs.cut_non_branching || runs.repeat || runs.heuristics AS heuristics,
                      min(runs.driven) AS min_driven,
                      avg(runs.driven) AS avg_driven,
                      max(runs.driven) AS max_driven,
                      min(runs.ptime) AS min_time,
                      avg(runs.ptime) AS avg_time,
                      max(runs.ptime) AS max_time
               FROM runs
               LEFT JOIN graphs ON graphs.id = runs.graph_id
               LEFT JOIN targets ON targets.id = runs.targets_id
               WHERE runs.repeat = 1
               GROUP BY graph_id, targets_id, full_driver, full_driven, targets, heuristics
            """).fetchall()
print "OK"

print "collecting heuristics...",
hnames = set()
hindex = names.index("heuristics")
for db_name in db_names:
    for raw in raw_data[db_name]:
        hnames.add(raw[hindex])
hnames = list(hnames)
print "OK"
print hnames

print "transforming data 1 ...",
data = {}
gindex = names.index("graph_id")
tindex = names.index("targets_id")
for db_name in db_names:
    for raw in raw_data[db_name]:
        key = (db_name, raw[names.index("graph_id")], raw[names.index("targets_id")])
        if key not in data:
            data[key] = {name: raw[names.index(name)] for name in ["nodes", "edges", "targets", "full_driver", "full_driven"]}
            for hname in hnames:
                data[key].update({hname: None})
        data[key].update({raw[names.index("heuristics")]: raw[names.index("min_driven")]})
for key in data:
    data[key].update({"degree": (data[key]["edges"] / data[key]["nodes"]) })
    data[key].update({"min_driven": min(data[key][hname] for hname in hnames if data[key][hname] is not None)})
    for hname in hnames:
        if data[key][hname] is not None:
            data[key][hname] /= data[key]["min_driven"]
    data[key].update({"scaled_min_driven": data[key]["min_driven"] / data[key]["full_driven"]})
    data[key].update({"scaled_full_driver": data[key]["full_driver"] / data[key]["nodes"]})
    data[key].update({"scaled_full_driven": data[key]["full_driven"] / data[key]["nodes"]})
    data[key].update({"scaled_targets": data[key]["targets"] / data[key]["nodes"]})
    data[key].update({"driven_per_targets": data[key]["min_driven"] / data[key]["targets"]})
data = data.values()
pickle.dump(data, open("sdata.txt", "w"))
print "OK"

print "transforming data 1 ...",
data = {}
gindex = names.index("graph_id")
tindex = names.index("targets_id")
for db_name in db_names:
    for raw in raw_data[db_name]:
        key = (db_name, raw[names.index("graph_id")], raw[names.index("targets_id")])
        if key not in data:
            data[key] = {name: raw[names.index(name)] for name in ["nodes", "edges", "targets", "full_driver", "full_driven", "heuristics", "min_driven", "avg_driven"]}
for key in data:
    data[key].update({"degree": (data[key]["edges"] / data[key]["nodes"]) })
    data[key].update({"scaled_min_driven": data[key]["min_driven"] / data[key]["full_driven"]})
    data[key].update({"scaled_full_driver": data[key]["full_driver"] / data[key]["nodes"]})
    data[key].update({"scaled_full_driven": data[key]["full_driven"] / data[key]["nodes"]})
    data[key].update({"scaled_targets": data[key]["targets"] / data[key]["nodes"]})
data = data.values()
pickle.dump(data, open("jdata.txt", "w"))
print "OK"

pickle.dump(hnames, open("hnames.txt", "w"))

