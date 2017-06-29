import graphviz as gv


def apply(log, input_file, output_file):

    tl = set()  # all task list
    df = []  # direct following tasks
    cs = []  # causalities tasks
    ncs = []  # non-causality tasks
    par = []  # parallel tasks
    xl = []   # (A,B) belong to Xw if there is a causal relation from each member of A to each member of B
              # and the membership never accur next to one another
    yl = []   # is derived from X by taking only the largest elements withrespect to set inclusion
    ti = []   #initial tasks
    to = []   #terminal tasks

    tl, df, cs, ncs, par = build_ordering_relations(log)
    xl, yl, ti, to, sub, prexl = make_sets(log, tl, cs, ncs)

    print "all tasks:", tl
    print "direct followers:", df
    print "causalities:", cs
    print "no_causalities:", ncs
    print "parallels:", par
    print "x list:", xl
    print "y list:", yl
    print "initial tasks:", ti
    print "terminal tasks:", to
    print "subsets:", sub
    print "pre x list", prexl

    build_petrinet(tl, yl, ti, to, output_file)


def build_ordering_relations(log):
    tl = set([item for sub in log for item in sub])
    df = get_direct_followers(log)
    cs = get_causalities(tl, df)
    ncs = get_no_causalities(tl, df)
    par = get_parallels(tl, df)

    return tl, df, cs, ncs, par


def make_sets(log, tl, cs, ncs):
    xl = make_xl_set(tl, cs, ncs)
    yl = make_yl_set(xl)
    ti = make_ti_set(log)
    to = make_to_set(log)
    sub = make_subset(tl)
    prexl = make_prexl_set(tl, ncs)

    return xl, yl, ti, to, sub, prexl



#find out the direct following relationship between tasks

def get_direct_followers(log):
    df = []
    for trace in log:
        for index, event in enumerate(trace):
            print index, event
            if index != len(trace)-1:
                if (event, trace[index+1]) not in df:
                    df.append((event, trace[index+1]))
    return df


#if direct following relationship exists, and it is not A->B and B->A, then generate causality
def get_causalities(all_tasks, direct_followers):
    cs = []  # causalities
    for event in all_tasks:
        for event2 in all_tasks:
            if (event, event2) not in cs:
                if (event, event2) in direct_followers and \
                   (event2, event) not in direct_followers:
                    cs.append((event, event2))
    return cs

#if direct following relationship not exists between two events, then no causality exist
def get_no_causalities(all_tasks, direct_followers):
    ncs = []  # no causalities
    for event in all_tasks:
        for event2 in all_tasks:
            if (event, event2) not in ncs:
                if (event, event2) not in direct_followers and \
                   (event2, event) not in direct_followers:
                    ncs.append((event, event2))
    return ncs


#if direct following relationship exists between two events and is A->B and B->A, then parallel
def get_parallels(all_tasks, direct_followers):
    par = []  # parallel tasks
    for event in all_tasks:
        for event2 in all_tasks:
            if (event, event2) not in par:
                if (event, event2) in direct_followers and \
                   (event2, event) in direct_followers:
                    par.append((event, event2))
    return par


#check whether causalty exists between events inside A, if true, then no causalty
def check_set(A, ncs):
    for event in A:
        for event2 in A:
            if (event, event2) not in ncs:
                return False
    return True


#check whether causalty exists between events in A and B, if true, then causalty
def check_outsets(A, B, cs):
    for event in A:
        for event2 in B:
            if (event, event2) not in cs:
                return False
    return True

#generate xl set, here they first generate a subset and then use causalities/no_causalities to generate xl
def make_xl_set(all_tasks, causalities, no_causalities):
    import itertools
    xl = set()
    subsets = set()
    for i in range(1, len(all_tasks)):       #generate subset
        for s in itertools.combinations(all_tasks, i):
            subsets.add(s)
    for a in subsets:                        #if two events has causality, then add into xl
        reta = check_set(a, no_causalities)
        for b in subsets:
            retb = check_set(b, no_causalities)
            if reta and retb and \
               check_outsets(a, b, causalities):
                xl.add((a, b))
    return xl

#the first new function to check what is in the subset when generating xl
def make_subset(all_tasks):
    import itertools
    subsets = set()
    for i in range(1, len(all_tasks)):       #generate subset
        for s in itertools.combinations(all_tasks, i):
            subsets.add(s)

    return subsets
#the second new function to check how the function of causalities/no_causalities used when generating xl
def make_prexl_set(all_tasks, no_causalities):
    import itertools
    xl = set()
    subsets = set()
    for i in range(1, len(all_tasks)):       #generate subset
        for s in itertools.combinations(all_tasks, i):
            subsets.add(s)
    for a in subsets:                        #if two events has causality, then add into xl
        reta = check_set(a, no_causalities)
        for b in subsets:
            retb = check_set(b, no_causalities)
            if reta and retb :
               xl.add((a, b))
    return xl

#generate yl
def make_yl_set(xl):
    import copy
    #yl is the subset of xl
    yl = copy.deepcopy(xl)
    for a in xl:
        A = a[0]
        B = a[1]
        for b in xl:

            if set(A).issubset(b[0]) and set(B).issubset(b[1]):
                if a != b:
                    yl.discard(a)    # if A is subset of b[0], B is subset of b[1]
                                     # if a is not b, then discard a
    return yl   # remaining element in yl will contain all the largest event set of xl


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


#building petrinet
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
