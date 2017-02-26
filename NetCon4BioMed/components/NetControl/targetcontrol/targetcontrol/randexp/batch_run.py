from __future__ import division
from __future__ import with_statement

import sqlite3
from random import choice, randint, seed
from os import path
import os
import ast

import sys
import getopt
import time

from graph import random_graph_ER, save_graph, load_graph, random_targets, save_targets, load_targets
from heuristics import get_heuristics, hstr
from control import target_control, full_control
from utils import generate_id



# constants related to paths and extensions
GRAPHS_LOCATION = 'graphs'
TARGETS_LOCATION = 'targets'
CONFIGS_LOCATION = 'configs'
GRAPHS_EXT = 'txt'
TARGETS_EXT = 'txt'
HEU_CONFIG_EXT = 'heu'
IN_CONFIG_EXT = 'in'



# creates the database for the results
def create_db(filename) :
    # create the file
    open(filename, 'w').close()
    # open the file as a database and populate it
    with sqlite3.connect(filename) as connection :
        c = connection.cursor()
        c.execute('''CREATE TABLE 
            graphs(
                id TEXT PRIMARY KEY NOT NULL, 
                method TEXT NOT NULL, 
                nodes INT NOT NULL, 
                edges INT NOT NULL, 
                full_driver INT NOT NULL,
                full_driven INT NOT NULL)
                ''')
        c.execute('''CREATE TABLE 
            targets(
                id TEXT PRIMARY KEY NOT NULL, 
                method TEXT NOT NULL, 
                nodes INT NOT NULL, 
                target INT NOT NULL)
                ''')
        c.execute('''CREATE TABLE 
            runs(
                id TEXT PRIMARY KEY NOT NULL,
                graph_id TEXT NOT NULL REFERENCES graphs(id),
                targets_id TEXT NOT NULL REFERENCES targets(id),
                cut_to_driven INT,
                cut_non_branching INT,
                repeat INT,
                heuristics TEXT NOT NULL,
                seed INT NOT NULL,
                driven INT NOT NULL,
                ptime REAL NOT NULL,
                wtime REAL NOT NULL)
                ''')

# generate graphs with given parameters
#@profile
def generate_graphs(db_filename, count = 1, method = 'ER', nodes = 50, edges = 100) :
    with sqlite3.connect(db_filename) as connection :
        c = connection.cursor()
        # count existing graphs with the given parameters
        existing = c.execute(
            '''SELECT count(*) FROM graphs 
               WHERE method = ? AND nodes = ? AND edges = ?''',
            (method, nodes, edges)).fetchone()[0]
        missing = count - existing if existing < count else 0
        # graphs are stored in the GRAPHS_LOCATION folder,
        # located in the folder containing the database
        save_location = path.join(path.dirname(db_filename), GRAPHS_LOCATION)
        for _ in range(missing) :
            print '@',
            # generate graph and compute full control info
            if method == 'ER' :
                V, E = random_graph_ER(n = nodes, m = edges)
            else :
                raise NotImplementedError('Graphs generating method not implemented: {}'.format(method))
            (full_driver, full_driven) = full_control(V, E)
            # save graph
            while True :
                try :
                    graph_id = generate_id()
                    g_filename = path.join(save_location, graph_id + path.extsep + GRAPHS_EXT)
                    save_graph(V, E, g_filename, header = 'number')
                    c.execute('INSERT INTO graphs VALUES (?, ?, ?, ?, ?, ?)', 
                        (graph_id, method, nodes, edges, full_driver, full_driven))
                    break
                except IOError :
                    # if graphs location directory is missing, create it
                    if not path.exists(save_location) :
                        os.mkdir(save_location)
                    else :
                        raise
                except sqlite3.IntegrityError as e :
                    # if the generated id already exists in the database
                    # then try again
                    if e.message == 'UNIQUE constraint failed: graphs.id' :
                        pass
                    else :
                        raise

# generate targets
def generate_targets(db_filename, count = 1, method = 'random', nodes = 50, target = 10) :
    with sqlite3.connect(db_filename) as connection :
        c = connection.cursor()
        # count existing targets with the given parameters
        existing = c.execute(
            '''SELECT count(*) FROM targets 
               WHERE method = ? AND nodes = ? AND target = ?''', 
            (method, nodes, target)).fetchone()[0]
        missing = count - existing if existing < count else 0
        # targets are stored in the TARGETS_LOCATION folder,
        # located in the folder containing the database
        save_location = path.join(path.dirname(db_filename), TARGETS_LOCATION)
        for _ in range(missing) :
            print '+',
            # generate targets
            if method == 'random' :
                targets = random_targets(n = nodes, t = target)
            else :
                raise NotImplementedError('Targets generating method not implemented: {}'.format(method))
            # save targets
            while True :
                try :
                    targets_id = generate_id()
                    t_filename = path.join(save_location, targets_id + path.extsep + TARGETS_EXT)
                    save_targets(targets, t_filename, sep = ' ')
                    c.execute('INSERT INTO targets VALUES (?, ?, ?, ?)', (targets_id, method, nodes, target))
                    break
                except IOError :
                    # if graphs location directory is missing, create it
                    if not path.exists(save_location) :
                        os.mkdir(save_location)
                    else :
                        raise
                except sqlite3.IntegrityError as e :
                    # if the generated id already exists in the database
                    # then try again
                    if e.message == 'UNIQUE constraint failed: targets.id' :
                        pass
                    else :
                        raise

# generate run configurations
# - db_filename = input database file
# - gmethod = graph generation method
# - tmethod = targets generation method
# - tfractions = target fractions to generate for each graph nodes number
# - scenarios = list of dictionaries, with the following keys:
#   - gnodes = list of node numbers
#   - gdegrees = list of average degrees (translate to edge numbers)
#   - gcount = number of graphs to generate (for each (nodes, edges) pair
#   - goffset = number of graphs to skip (for each (nodes, edges) pair
#   - tcount = number of target sets to generate (for each fraction)
#   - toffset = number of target sets to skip (for each fraction)
#@profile
def generate_run_config(db_filename, 
                        gmethod = 'ER', tmethod = 'random', 
                        tfractions = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                        scenarios = [{
                            'gnodes' : [50], 'gdegrees' : [2, 3],
                            'gcount' : 2, 'ggroup' : 1, 'goffset' : 0,
                            'tcount' : 1, 'tgroup' : 1, 'toffset' : 0
                        }]
                        ) :
    with sqlite3.connect(db_filename) as connection :
        c = connection.cursor()
        ret = []
        for s in scenarios :
            subret = []
            for n in s['gnodes'] :
                # get target ids
                targets_ids = []
                for f in tfractions :
                    t = int(round(n * f))
                    # make sure targets exist, then get their ids
                    generate_targets(db_filename, count = s['tcount'] * s['tgroup'] + s['toffset'], method = tmethod, nodes = n, target = t)
                    ids = [row[0] for row in c.execute(
                        'SELECT id FROM targets WHERE method = ? AND nodes = ? AND target = ? LIMIT ? OFFSET ?', 
                        (tmethod, n, t, s['tcount'] * s['tgroup'], s['toffset'])).fetchall()]
                    targets_ids.extend(ids)
                # get graph ids
                graph_ids = []
                for d in s['gdegrees'] :
                    m = int(round(n * d))
                    # make sure the graphs exist, then get their ids
                    generate_graphs(db_filename, count = s['gcount'] * s['ggroup'] + s['goffset'], method = gmethod, nodes = n, edges = m)
                    ids = [(row[0], row[1]) for row in c.execute(
                        'SELECT id, full_driven FROM graphs WHERE method = ? AND nodes = ? AND edges = ? LIMIT ? OFFSET ?', 
                        (gmethod, n, m, s['gcount'] * s['ggroup'], s['goffset'])).fetchall()]
                    graph_ids.extend(ids)
                # save for return
                subret.append((graph_ids, targets_ids))
            ret.append(subret)
        return ret

# read input configuration from file
def read_run_config(db_filename, in_filename) :
    data = generate_run_config(db_filename, **ast.literal_eval(open(in_filename, 'r').read()))
    ret = []
    for group in data :
        ret_group = []
        for (gs, ts) in group :
            ret_group.append(([g[0] for g in gs], ts))
        ret.append(ret_group)
    return ret

# read heuristics configuration file
def read_heuristics_config(h_filename) :
    with open(h_filename, 'r') as hfile :
        lines = [line.split() for line in hfile.readlines()]
        params = [{
            'cut_to_driven' : line[0] == 'T',
            'cut_non_branching' : line[1] == 'T',
            'repeat' : int(line[2]),
            'heuristics' : get_heuristics(line[3]),
            'name' : line[0] + line[1] + line[2] + line[3],
        } for line in lines]
        return params

# generate runs
#@profile
def generate_runs(db_filename, heu_filename, in_filename, stop_by_file = False) :
    # read heuristics configuration file
    params = read_heuristics_config(heu_filename)
    # read graphs configuration file
    inputs = read_run_config(db_filename, in_filename)
    # run tests
    try :
        connection = sqlite3.connect(db_filename)
        c = connection.cursor()
        # get count of existing runs for each (graph, targets, heuristics) tuple
        run_setup = {}
        for p in params :
            for i in range(len(inputs)) :
                for gs, ts in inputs[i] :
                    counts = c.execute(
                        '''SELECT graph_id, targets_id, count(*) FROM runs 
                           WHERE graph_id IN ({}) AND targets_id IN ({}) AND heuristics = ? AND
                                 cut_to_driven = ? AND cut_non_branching = ? AND repeat = ?
                           GROUP BY graph_id, targets_id'''.format("'" + "','".join(gs) + "'", "'" + "','".join(ts) + "'"), 
                        (hstr(p['heuristics']),
                                    1 if p['cut_to_driven'] else 0,
                                    1 if p['cut_non_branching'] else 0,
                                    p['repeat']
                                    )).fetchall()
                    get_count = {}
                    for (g, t, val) in counts :
                        get_count[(g, t)] = val
                    for g in gs :
                        for t in ts :
                            count = get_count[(g, t)] if (g, t) in get_count else 0
                            if count not in run_setup :
                                run_setup[count] = []
                            if (p, g, t) not in run_setup[count] :
                                run_setup[count].append((p, g, t))
        # setup graph and targets locations
        graphs_location = path.join(path.dirname(db_filename), GRAPHS_LOCATION)
        targets_location = path.join(path.dirname(db_filename), TARGETS_LOCATION)
        # run the testing loop
        stop_file = path.join(path.dirname(db_filename), "STOP")
        condition = (lambda: True) if not stop_by_file else (lambda : not path.isfile(stop_file))
        print
        while condition() :
            k = min(run_setup.keys())
            K = max(run_setup.keys())
            print '{} ({}) : '.format(k, K - k) + '0 / {} entries'.format(len(run_setup[k])).ljust(25),
            if k + 1 not in run_setup :
                run_setup[k + 1] = []
            for rsi in range(len(run_setup[k])) :
                if not condition():
                    break
                (p, g, t) = run_setup[k][rsi]
                # run test
                rseed = randint(0, 1000000)
#                V, E = load_graph('graphs/' + g + '.txt', header = 'number', convert = int)
#                targets = load_targets('targets/' + t + '.txt', sep = ' ', convert = int)
                V, E = load_graph(path.join(graphs_location, g + path.extsep + GRAPHS_EXT), header = 'number', convert = int)
                targets = load_targets(path.join(targets_location, t + path.extsep + TARGETS_EXT), sep = ' ', convert = int)
                seed(rseed)
                pstart = time.clock()
                wstart = time.time()
                res = target_control(V, E, targets, **p)
                ptime = time.clock() - pstart
                wtime = time.time() - wstart
                driven = len(res['driven'])
                # save targets
                while True :
                    try :
                        run_id = generate_id()
                        c.execute(
                            '''INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (run_id, g, t,
                            1 if p['cut_to_driven'] else 0,
                            1 if p['cut_non_branching'] else 0,
                            p['repeat'],
                            hstr(p['heuristics']),
                            rseed,
                            driven, ptime, wtime))
                        run_setup[k + 1].append((p, g, t))
                        connection.commit()
                        print '\b' * 26 + '{} / {} entries'.format(rsi + 1, len(run_setup[k])).ljust(25),
                        break
                    except sqlite3.IntegrityError as e :
                        # if the generated id already exists in the database
                        # then try again
                        if e.message == 'UNIQUE constraint failed: runs.id' :
                            pass
                        else :
                            raise
            del run_setup[k]
            connection.commit()
            print
        if stop_by_file:
            os.remove(stop_file)
        print "Batch run stopped."
    except KeyboardInterrupt :
        connection.commit()
        connection.close()



#=======
# run this as a script
#=====================

if __name__ == "__main__" :
    run_str = "run.py (-c | --create | -a | --append) [-f | --force] (-d | --database=)<db_filename> (-i | --input=)<input_configfile> (-h | --heuristics=)<heuristics_configfile>"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cafh:i:d:", ["heuristics=", "input=", "database=", "create", "append", "force", "stop-by-file"])
    except getopt.GetoptError:
        # default behavior is append to existing db
        print run_str
        sys.exit(0)
    db_filename = None
    h_filename = None
    in_filename = None
    mode = None
    force = False
    stop_by_file = False
    for opt, arg in opts:
        if opt in ("-c", "--create"):
            if mode is None:
                mode = "create"
            else:
                print "multiple options found, use exactly one of '-c', '-a', '--create', '--append'"
                sys.exit(0)
        elif opt in ("-a", "--append"):
            if mode is None:
                mode = "append"
            else:
                print "multiple options found, use exactly one of '-c', '-a', '--create', '--append'"
                sys.exit(0)
        elif opt in ("-f", "--force"):
            force = True
        elif opt in ("-i", "--input"):
            in_filename = arg
        elif opt in ("-d", "--database"):
            db_filename = arg
        elif opt in ("-h", "--heuristics"):
            h_filename = arg
        elif opt == "--stop-by-file":
            stop_by_file = True
        else:
            print "unrecognized option: {}".format(opt)
    if db_filename is None:
        print "use '-d <filename>' or '--database=<filename>' to indicate the database file"
        sys.exit(0)
    if in_filename is None:
        print "use '-i <filename>' or '--input=<filename>' to indicate the input configuration file"
        sys.exit(0)
    if h_filename is None:
        print "use '-h <filename>' or '--heuristics=<filename>' to indicate the heuristics file"
        sys.exit(0)
    if mode is None:
        print "indicate how  you want to use the database: '-c' for create, '-a' for append"
        sys.exit(0)
    exists = path.isfile(db_filename)
    if mode == "create":
        if exists and not force:
            print "database file already exists, use '-f' or '--force' to overwrite"
            sys.exit(0)
        create_db(db_filename)
    elif mode == "append":
        if not exists:
            if not force:
                print "database file not found, use '-f' or '--force' to create"
                sys.exit(0)
            create_db(db_filename)
    else:
        print "mode not implemented: {}".format(mode)
        sys.exit(0)
    generate_runs(db_filename, h_filename, in_filename, stop_by_file = stop_by_file)
