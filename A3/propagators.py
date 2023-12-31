############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 3 Starter Code
## v1.0
##
############################################################


def prop_FC(csp, last_assigned_var=None):
    """
    This is a propagator to perform forward checking. 

    First, collect all the relevant constraints.
    If the last assigned variable is None, then no variable has been assigned 
    and we are performing propagation before search starts.
    In this case, we will check all the constraints.
    Otherwise, we will only check constraints involving the last assigned variable.

    Among all the relevant constraints, focus on the constraints with one unassigned variable. 
    Consider every value in the unassigned variable's domain, if the value violates 
    any constraint, prune the value. 

    :param csp: The CSP problem
    :type csp: CSP
        
    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: The boolean indicates whether forward checking is successful.
        The boolean is False if at least one domain becomes empty after forward checking.
        The boolean is True otherwise.
        Also returns a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]
    """
    pruned = []

    if not last_assigned_var:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(last_assigned_var)

    for c in constraints:
        if c.get_num_unassigned_vars() == 1:
            unassigned = c.get_unassigned_vars()[0]
            for value in unassigned.cur_domain():
                # Temporarily assign a value
                unassigned.assign(value)
                if not c.check([var.get_assigned_value() for var in c.get_scope()]):
                    # Prune the value
                    unassigned.prune_value(value)
                    pruned.append((unassigned, value))
                    if unassigned.cur_domain_size() == 0:
                        # Undo assignment
                        unassigned.unassign()
                        return False, pruned
                # Undo assignment
                unassigned.unassign()
    return True, pruned


def prop_AC3(csp, last_assigned_var=None):
    """
    This is a propagator to perform the AC-3 algorithm.

    Keep track of all the constraints in a queue (list). 
    If the last_assigned_var is not None, then we only need to 
    consider constraints that involve the last assigned variable.

    For each constraint, consider every variable in the constraint and 
    every value in the variable's domain.
    For each variable and value pair, prune it if it is not part of 
    a satisfying assignment for the constraint. 
    Finally, if we have pruned any value for a variable,
    add other constraints involving the variable back into the queue.

    :param csp: The CSP problem
    :type csp: CSP
        
    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: a boolean indicating if the current assignment satisifes 
        all the constraints and a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]
    """
    pruned = []

    if not last_assigned_var:
        constraints = csp.get_all_cons()
    else:
        constraints = csp.get_cons_with_var(last_assigned_var)

    while len(constraints) != 0:
        c = constraints.pop(0)
        scope = c.get_scope()
        for var in scope:
            revised = False
            for val in var.cur_domain():
                works = False
                if (var, val) in c.sup_tuples:
                    for sup in c.sup_tuples[(var, val)]:
                        sup_works = True
                        for i, v in enumerate(sup):
                            if v not in scope[i].cur_domain():
                                sup_works = False
                        if sup_works:
                            works = True
                if not works:
                    var.prune_value(val)
                    pruned.append((var, val))
                    revised = True
                    if var.cur_domain_size() == 0:
                        return False, pruned
            if revised:
                for new_c in csp.get_cons_with_var(var):
                    if new_c != c and new_c not in constraints:
                        constraints.append(new_c)
    return True, pruned


def ord_mrv(csp):
    """
    Implement the Minimum Remaining Values (MRV) heuristic.
    Choose the next variable to assign based on MRV.

    If there is a tie, we will choose the first variable. 

    :param csp: A CSP problem
    :type csp: CSP

    :returns: the next variable to assign based on MRV

    """
    unassigned_vars = csp.get_all_unasgn_vars()
    least = None
    for var in unassigned_vars:
        if least is None:
            least = var
        else:
            if var.cur_domain_size() < least.cur_domain_size():
                least = var
    return least


###############################################################################
# Do not modify the prop_BT function below
###############################################################################


def prop_BT(csp, last_assigned_var=None):
    """
    This is a basic propagator for plain backtracking search.

    Check if the current assignment satisfies all the constraints.
    Note that we only need to check all the fully instantiated constraints 
    that contain the last assigned variable.
    
    :param csp: The CSP problem
    :type csp: CSP

    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: a boolean indicating if the current assignment satisifes all the constraints 
        and a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]

    """

    # If we haven't assigned any variable yet, return true.
    if not last_assigned_var:
        return True, []

    # Check all the constraints that contain the last assigned variable.
    for c in csp.get_cons_with_var(last_assigned_var):

        # All the variables in the constraint have been assigned.
        if c.get_num_unassigned_vars() == 0:

            # get the variables
            vars = c.get_scope()

            # get the list of values
            vals = []
            for var in vars:  #
                vals.append(var.get_assigned_value())

            # check if the constraint is satisfied
            if not c.check(vals):
                return False, []

    return True, []
