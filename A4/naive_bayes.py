############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 4 Starter Code
## v1.2
## - removed the example in ve since it is misleading.
## - updated the docstring in min_fill_ordering. The tie-breaking rule should
##   choose the variable that comes first in the provided list of factors.
############################################################

from bnetbase import Variable, Factor, BN
import csv


def normalize(factor):
    '''
    Normalize the factor such that its values sum to 1.
    Do not modify the input factor.

    :param factor: a Factor object. 
    :return: a new Factor object resulting from normalizing factor.
    '''

    total = sum(factor.values)
    normalized_factor = Factor(factor.name, factor.get_scope())
    normalized_factor.values = [val / total for val in factor.values]

    return normalized_factor


def restrict(factor, variable, value):
    '''
    Restrict a factor by assigning value to variable.
    Do not modify the input factor.

    :param factor: a Factor object.
    :param variable: the variable to restrict.
    :param value: the value to restrict the variable to
    :return: a new Factor object resulting from restricting variable to value.
             This new factor no longer has variable in it.
    '''

    new_scope = [v for v in factor.get_scope() if v != variable]
    new_factor = Factor(factor.name + " restricted", new_scope)
    new_values = []

    for i in range(len(factor.values)):
        assignment = []
        temp = i
        for v in reversed(factor.get_scope()):
            assignment.insert(0, v.dom[temp % v.domain_size()])
            temp = temp // v.domain_size()

        # Check if the assignment matches the restricted variable's value
        if assignment[factor.get_scope().index(variable)] == value:
            # Compute the index for the new factor
            new_index = 0
            for v in new_scope:
                new_index = new_index * v.domain_size() + v.value_index(assignment[factor.get_scope().index(v)])

            # Add the value to the new factor's values
            new_values.append(factor.values[i])

    new_factor.values = new_values

    return new_factor


def sum_out(factor, variable):
    '''
    Sum out a variable variable from factor factor.
    Do not modify the input factor.

    :param factor: a Factor object.
    :param variable: the variable to sum out.
    :return: a new Factor object resulting from summing out variable from the factor.
             This new factor no longer has variable in it.
    '''

    new_scope = [v for v in factor.get_scope() if v != variable]
    summed_out_factor = Factor(factor.name + " summed out" + variable.name, new_scope)

    # Calculate the size of the new factor's value table
    new_factor_size = 1
    for v in new_scope:
        new_factor_size *= v.domain_size()
    new_values = [0] * new_factor_size

    for idx, val in enumerate(factor.values):
        assignment = [None] * len(factor.get_scope())
        temp = idx
        for i, v in enumerate(reversed(factor.get_scope())):
            assignment[len(factor.get_scope()) - 1 - i] = v.dom[temp % v.domain_size()]
            temp //= v.domain_size()

        new_index = 0
        multiplier = 1
        for v in new_scope:
            new_index += multiplier * v.dom.index(assignment[factor.get_scope().index(v)])
            multiplier *= v.domain_size()

        new_values[new_index] += val

    summed_out_factor.values = new_values

    return summed_out_factor


def multiply(factor_list):
    '''
    Multiply a list of factors together.
    Do not modify any of the input factors. 

    :param factor_list: a list of Factor objects.
    :return: a new Factor object resulting from multiplying all the factors in factor_list.
    '''
    new_scope_vars = set()
    for factor in factor_list:
        new_scope_vars.update(factor.get_scope())
    new_scope = list(new_scope_vars)

    new_factor_name = "product of" + " ".join([f.name for f in factor_list])
    product_factor = Factor(new_factor_name, new_scope)

    # Calculate the size of the new factor's value table
    new_factor_size = 1
    for v in new_scope:
        new_factor_size *= v.domain_size()

    # Initialize the value table for the new factor
    product_factor.values = [1] * new_factor_size

    # Step 3: Calculate the values for the new factor
    for idx in range(new_factor_size):
        # Determine the assignment for this index
        assignment = [None] * len(new_scope)
        temp = idx
        for i, v in enumerate(reversed(new_scope)):
            assignment[len(new_scope) - 1 - i] = v.dom[temp % v.domain_size()]
            temp //= v.domain_size()

        # Multiply corresponding values from the input factors
        for factor in factor_list:
            # Generate index for the current factor
            current_index = 0
            multiplier = 1
            for var in factor.get_scope():
                value_index = var.dom.index(assignment[new_scope.index(var)])
                current_index += multiplier * value_index
                multiplier *= var.domain_size()

            # Multiply the value
            product_factor.values[idx] *= factor.values[current_index]

    return product_factor


def min_fill_ordering(factor_list, variable_query):
    '''
    This function implements The Min Fill Heuristic. We will use this heuristic to determine the order 
    to eliminate the hidden variables. The Min Fill Heuristic says to eliminate next the variable that 
    creates the factor of the smallest size. If there is a tie, choose the variable that comes first 
    in the provided order of factors in factor_list.

    The returned list is determined iteratively.
    First, determine the size of the resulting factor when eliminating each variable from the factor_list.
    The size of the resulting factor is the number of variables in the factor.
    Then the first variable in the returned list should be the variable that results in the factor 
    of the smallest size. If there is a tie, choose the variable that comes first in the provided order of 
    factors in factor_list. 
    Then repeat the process above to determine the second, third, ... variable in the returned list.

    Here is an example.
    Consider our complete Holmes network. Suppose that we are given a list of factors for the variables 
    in this order: P(E), P(B), P(A|B, E), P(G|A), and P(W|A). Assume that our query variable is Earthquake. 
    Among the other variables, which one should we eliminate first based on the Min Fill Heuristic? 

    - Eliminating B creates a factor of 2 variables (A and E).
    - Eliminating A creates a factor of 4 variables (E, B, G and W).
    - Eliminating G creates a factor of 1 variable (A).
    - Eliminating W creates a factor of 1 variable (A).

    In this case, G and W tie for the best variable to be eliminated first since eliminating each variable 
    creates a factor of 1 variable only. Based on our tie-breaking rule, we should choose G since it comes 
    before W in the list of factors provided.
    '''

    # Start with all variables except the query variable
    remaining_vars = set()
    for factor in factor_list:
        for var in factor.get_scope():
            if var != variable_query:
                remaining_vars.add(var)

    elimination_order = []

    while remaining_vars:
        min_size = float('inf')
        best_var = None

        for var in remaining_vars:
            # Simulate eliminating the variable and calculate the size of the resulting factor
            involved_factors = [f for f in factor_list if var in f.get_scope()]
            new_scope = set()
            for f in involved_factors:
                new_scope.update(f.get_scope())
            new_scope.discard(var)  # Remove the variable being eliminated
            new_factor_size = 1
            for v in new_scope:
                new_factor_size *= v.domain_size()

            # Check if this is the smallest factor so far
            if new_factor_size < min_size:
                min_size = new_factor_size
                best_var = var

        # Add the best variable to the elimination order and remove it from remaining variables
        elimination_order.append(best_var)
        remaining_vars.remove(best_var)

    return elimination_order


def ve(bayes_net, var_query, varlist_evidence): 
    '''
    Execute the variable elimination algorithm on the Bayesian network bayes_net
    to compute a distribution over the values of var_query given the 
    evidence provided by varlist_evidence. 

    :param bayes_net: a BN object.
    :param var_query: the query variable. we want to compute a distribution
                     over the values of the query variable.
    :param varlist_evidence: the evidence variables. Each evidence variable has 
                         its evidence set to a value from its domain 
                         using set_evidence.
    :return: a Factor object representing a distribution over the values
             of var_query. that is a list of numbers, one for every value
             in var_query's domain. These numbers sum to 1. The i-th number
             is the probability that var_query is equal to its i-th value given 
             the settings of the evidence variables.

    '''
    factors = bayes_net.factors()
    for var in varlist_evidence:
        for i in range(len(factors)):
            if var in factors[i].get_scope():
                factors[i] = restrict(factors[i], var, var.get_evidence())

    elimination_order = min_fill_ordering(factors, var_query)
    for var in elimination_order:
        involved_factors = [factor for factor in factors if var in factor.get_scope()]
        for f in involved_factors:
            factors.remove(f)
        product_factor = multiply(involved_factors)
        summed_out_factor = sum_out(product_factor, var)
        factors.append(summed_out_factor)

    final_factor = multiply(factors)

    normalized_factor = normalize(final_factor)

    return normalized_factor


## The order of these domains is consistent with the order of the columns in the data set.
salary_variable_domains = {
"Work": ['Not Working', 'Government', 'Private', 'Self-emp'],
"Education": ['<Gr12', 'HS-Graduate', 'Associate', 'Professional', 'Bachelors', 'Masters', 'Doctorate'],
"Occupation": ['Admin', 'Military', 'Manual Labour', 'Office Labour', 'Service', 'Professional'],
"MaritalStatus": ['Not-Married', 'Married', 'Separated', 'Widowed'],
"Relationship": ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'],
"Race": ['White', 'Black', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other'],
"Gender": ['Male', 'Female'],
"Country": ['North-America', 'South-America', 'Europe', 'Asia', 'Middle-East', 'Carribean'],
"Salary": ['<50K', '>=50K']
}

salary_variable=Variable("Salary", ['<50K', '>=50K'])

def naive_bayes_model(data_file, variable_domains=salary_variable_domains, class_var=salary_variable):
    '''
    NaiveBayesModel returns a BN that is a Naive Bayes model that represents 
    the joint distribution of value assignments to variables in the given dataset.

    Remember a Naive Bayes model assumes P(X1, X2,.... XN, Class) can be represented as 
    P(X1|Class) * P(X2|Class) * .... * P(XN|Class) * P(Class).

    When you generated your Bayes Net, assume that the values in the SALARY column of 
    the dataset are the CLASS that we want to predict.

    Please name the factors as follows. If you don't follow these naming conventions, you will fail our tests.
    - The name of the Salary factor should be called "Salary" without the quotation marks.
    - The name of any other factor should be called "VariableName,Salary" without the quotation marks. 
      For example, the factor for Education should be called "Education,Salary".

    @return a BN that is a Naive Bayes model and which represents the given data set.
    '''
    ### READ IN THE DATA
    input_data = []
    with open(data_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)

    ### YOUR CODE HERE ###


def explore(bayes_net, question):
    '''    
    Return a probability given a Naive Bayes Model and a question number 1-6. 
    
    The questions are below: 
    1. What percentage of the women in the test data set does our model predict having a salary >= $50K? 
    2. What percentage of the men in the test data set does our model predict having a salary >= $50K? 
    3. What percentage of the women in the test data set satisfies the condition: P(S=">=$50K"|Evidence) is strictly greater than P(S=">=$50K"|Evidence,Gender)?
    4. What percentage of the men in the test data set satisfies the condition: P(S=">=$50K"|Evidence) is strictly greater than P(S=">=$50K"|Evidence,Gender)?
    5. What percentage of the women in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K?
    6. What percentage of the men in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K?

    @return a percentage (between 0 and 100)
    ''' 
    ### YOUR CODE HERE ###

