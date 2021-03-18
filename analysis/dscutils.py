import numpy as np
import pandas as pd
import operator
import re

def select_column_with_condition(df, column, conditions):
    dfselect = select_rows(df, conditions)
    return dfselect


def select_dfrows(df, conditions):
    '''
    df: Pandas DataFrame
    Conditions: List of strings, each item is a condition to check
        Format of string items 
           $(colname) operator value
        to check 
           df[colname] operator value 
        The operator could be the ones listed in logic_dict (see parse_condition)
    Automatically append conditions with 'AND' operator.
    '''
    dfcond = None
    for condition in conditions:
        colname, logic_operator, valuestring = parse_condition(condition)
        
        if df[colname].dtype != 'O': # if not object type in the Dataframe
            value = np.array([valuestring]).astype(df[colname].dtype)[0]
        else:
            if valuestring.startswith("'") and valuestring.endswith("'"):
                value = re.match('^\'(.*)\'', valuestring).group(1)
            else:
                value = valuestring.strip()
            
        if dfcond is None:
            dfcond = logic_operator(df[colname], value)
        else:
            dfcond = dfcond & logic_operator(df[colname], value)
    return df.loc[dfcond]


def parse_condition(cstring):
    '''
    Format of cstring:
        $(colname) operator value
    Returns colname, operator, value
    colname and value are strings
    '''
    logic_dict = {'==': operator.eq,
                  '!=': operator.ne,
                  '<':  operator.lt,
                  '<=': operator.le,
                  '>':  operator.gt,
                  '>=': operator.ge,
                }
    logic_strings = list(logic_dict.keys())
    
    '''
    Some error messages
    '''
    logic_err = "Malformed expression {:s}. Must contain one and only one logic operator."
    colname_err = "Malformed column {:s}. Column name must be specified as $(column_name)."
    
    
    def parse_colname(cleft, errmsg):
        assert cleft.startswith('$(') and cleft.endswith(')'), errmsg.format(cleft)
        return re.match('^\$\((.*)\)', cleft).group(1)
    
    def parse_value(cright):
        return cright
    
    lstrings = [x for x in logic_strings if x in cstring]
    assert len(lstrings) == 1, logic_err.format(cstring)
    
    csplit  = [x.strip() for x in cstring.strip().split(lstrings[0])]
    colname = parse_colname(csplit[0], colname_err)
    value   = parse_value(csplit[1])
        
    return colname, logic_dict[lstrings[0]], value
