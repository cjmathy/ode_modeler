import numpy as np
from scipy.integrate import odeint
import sympy


def run(species, parameters, ttot, n_iter, **kwargs):
    '''
    Description:
        This method prepares the system and calls the odeint method, which
        performs the ode integration over the specified time course. The
        odeint method requires the definition of an ode_ststem method,
        which computes the derivative of the function at a given timepoint.
    Inputs:
        species - a dictionary mapping strings to Species objects.
        parameters - a dictionary mapping strings to floats.
        ttot - an integer setting the total length of simulation.
        n_int - an integer setting the total number of integrations steps
            during simulation.
    Returns:
        concentrations - a numpy array with dimensions n_species x n_timepoints
        t - the numpy array with dimensions 1 x n_timepoints (useful for
            plotting concentration vs. time)
    '''

    # TODO: sanitize input of ODE (parse, then confirm that it only contains strings in species)


    # Prepare initial concentration and time vectors for odeint
    c0 = initialize_concentrations(species)
    t = np.linspace(0, ttot, n_iter)

    # Solve system of ODEs. Cell i,j of concentrations contains the
    # concentration value of Species j at timepoint i.
    concentrations = odeint(ode_system,
                            c0,
                            t,
                            args=(species, parameters),
                            full_output = 1)
    return concentrations, t


def initialize_concentrations(species):
    '''
    Description:
        This method takes in a dictionary of species objects and creates a
        numpy array containing the initial concentrations of each species.
        The array is ordered according to the indexes unique to each Species
        object, which correspond to the ordering of the csv file.
    Input:
        species - a dictionary of Species objects.
    Returns:
        c0 - a numpy array of floats, shape (n_sp,), where n_sp is the number
            of species in the system.
    '''
    c0 = np.empty(len(species))
    for s in species:
        c0[species[s].index] = species[s].conc0
    return c0


def ode_system(y, t, species, parameters):
    '''
    Description:
        This method prepares a system of first order ODEs for odeint. It
        computes the derivative of y (the vector of molecular species) at t.
        First, a variable is created for each Species and set to the current
        value found in y. Then, a variable is created for each parameter, and
        set to its corresponding value. Finally, the derivate expressions for
        each species are evaluated according to these variables, and stored in
        the list dydt.
    Inputs:
        y - a numpy ndarray of floats (representing concentrations).
        t - a numpy ndarray of floats (representing timepoints). t is not
            explicitly called in ode_system, but is required by odeint.
        species - a dictionary mapping strings to Species objects.
        parameters - a dictionary mapping strings to Parameter objects.
    Returns:
        dydt - a list of floats representing rates of change in concentration.
    '''
    var_dict = {}
    
    for s in species:
        tmp = sympy.var(s)
        var_dict[tmp] = y[int(species[s].index)]
        
    for p in parameters:
        tmp = sympy.var(p)
        var_dict[tmp] = parameters[p]
        
    dydt = [None]*len(species)
    
    for s in species:
        dydt[int(species[s].index)] = sympy.sympify(species[s].ode).evalf(subs = var_dict)
    return dydt
