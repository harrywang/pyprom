#!/usr/bin/python
# Module for Alpha Algorithm
# https://en.wikipedia.org/wiki/Alpha_algorithm
import graphviz as gv


def apply(log, input_file, output_file):

    tl = set()  # all task list
    df = []  # direct following tasks
    cs = []  # causalities tasks
    ncs = []  # non-causality tasks
    par = []  # parallel tasks
    xl = []
    yl = []
    ti = []
    to = []

    tl, df, cs, ncs, par = build_ordering_relations(log)
    xl, yl, ti, to = make_sets(log, tl, df, cs, ncs)

    print("all tasks:", tl)
    print("direct followers:", df)
    print("causalities:", cs)
    print("no_causalities:", ncs)
    print("parallels:", par)
    print("x list:", xl)
    print("y list:", yl)
    print("initial tasks:", ti)
    print("terminal tasks:", to)

    build_petrinet(tl, yl, ti, to, output_file)


def build_ordering_relations(log):
    tl = set([item for sub in log for item in sub])
    df = get_direct_followers(log)
    cs = get_causalities(tl, df)
    ncs = get_no_causalities(tl, df)
    par = get_parallels(tl, df)

    return tl, df, cs, ncs, par


def make_sets(log, tl, df, cs, ncs):
    xl = make_xl_set(tl, df, cs, ncs)
    yl = make_yl_set(xl)
    ti = make_ti_set(log)
    to = make_to_set(log)

    return xl, yl, ti, to


def get_direct_followers(log):
    df = []
    for trace in log:
        for index, event in enumerate(trace):
            print(index, event)
            if index != len(trace)-1:
                if (event, trace[index+1]) not in df:
                    df.append((event, trace[index+1]))
    return df


def get_causalities(all_tasks, direct_followers):
    cs = []  # causalities
    for event in all_tasks:
        for event2 in all_tasks:
            if (event, event2) not in cs:
                if (event, event2) in direct_followers and \
                   (event2, event) not in direct_followers:
                    cs.append((event, event2))
    return cs


def get_no_causalities(all_tasks, direct_followers):
    ncs = []  # no causalities
    for event in all_tasks:
        for event2 in all_tasks:
            if (event, event2) not in ncs:
                if (event, event2) not in direct_followers and \
                   (event2, event) not in direct_followers:
                    ncs.append((event, event2))
    return ncs


def get_parallels(all_tasks, direct_followers):
    par = []  # parallel tasks
    for event in all_tasks:
        for event2 in all_tasks:
            if (event, event2) not in par:
                if (event, event2) in direct_followers and \
                   (event2, event) in direct_followers:
                    par.append((event, event2))
    return par


def check_set(A, ncs):
    for event in A:
        for event2 in A:
            if (event, event2) not in ncs:
                return False
    return True


def check_outsets(A, B, cs):
    for event in A:
        for event2 in B:
            if (event, event2) not in cs:
                return False
    return True


def make_xl_set(all_tasks, direct_followers, causalities, no_causalities):
    import itertools
    xl = set()
    subsets = set()
    for i in range(1, len(all_tasks)):
        for s in itertools.combinations(all_tasks, i):
            subsets.add(s)
    for a in subsets:
        reta = check_set(a, no_causalities)
        for b in subsets:
            retb = check_set(b, no_causalities)
            if reta and retb and \
               check_outsets(a, b, causalities):
                xl.add((a, b))
    return xl


def make_yl_set(xl):
    import copy
    yl = copy.deepcopy(xl)
    for a in xl:
        A = a[0]
        B = a[1]
        for b in xl:

            if set(A).issubset(b[0]) and set(B).issubset(b[1]):
                if a != b:
                    yl.discard(a)
    return yl


# Ti is the set of all tasks which occur trace-initially
def make_ti_set(log):
    ti = set()
    [ti.add(event[0]) for event in log]
    return ti


# To is the set of all tasks which occur trace-terminally
def make_to_set(log):
    to = set()
    [to.add(event[-1]) for event in log]
    return to


def build_petrinet(tl, yl, ti, to, output_file):
    pn = gv.Digraph(format='png')
    pn.attr(rankdir='LR')  # left to righ layout - default is top down
    pn.node('start')
    pn.node('end')

    for elem in yl:
        for i in elem[0]:
            pn.edge(i, str(elem))
            pn.node(i, shape='box')
            pn.node(str(elem), shape='circle')
        for i in elem[1]:
            pn.edge(str(elem), i)
            pn.node(i, shape='box')
    for i in ti:
        pn.edge('start', i)
    for o in to:
        pn.edge(o, 'end')
    pn.render(output_file)
