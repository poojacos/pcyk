import nltk
from pprint import pprint
import numpy as np
import pandas as pd


def genGrammar(ruleFile):
    """
    The function binarizes a grammar in non-CNF and outputs the set of grammer/lexical rules in CNF along with the associated probabilities for PCKY parsing.

    Args:
        ruleFile (file): file containing grammar rules

    Returns:
        [type]: binarized grammar
    """
    rules = []
    mastr = []
    with open(ruleFile) as f :
        for line in f:
            rule = line.strip().split('\t')
            rules.append([rule[1], rule[2:], float(rule[0])])
            mastr.append([rule[1], rule[2:]])
            
    cnf = []           
    while len(rules) > 0 :
        [lhs, rhs, p] = rules.pop()
        if len(rhs) <= 2: cnf.append([lhs, rhs, p])
        else :
            rest = rhs[:len(rhs)-1]
            first = '-'.join(rest)
            if [first, rest] not in mastr :
                rules.append([first, rest, 1])
                mastr.append([first, rest])
            cnf.append([lhs, [first, rhs[-1]], p])

    mysteryVariable = {}
    for [lhs, rhs, p] in cnf :
        if lhs not in mysteryVariable :
            mysteryVariable[lhs] = p
        else :
            mysteryVariable[lhs] += p

    cleanRules = []
    for r in cnf:
        cleanRules.append((r[0], r[1], r[2]/mysteryVariable[r[0]]))
    
    return cleanRules


def init_parse_triangle(number_of_words,non_terminals, fill_value=np.float64(0.0)):
    """
    This function initializes a dictionary for parsing

    Args:
        number_of_words (int): number of words in the sentence
        non_terminals (list): a list of terminals in the grammar rules
        fill_value (float, optional): Initializing value for list elements. Defaults to np.float64(0.0).

    Returns:
        dict: An dictionary with key as non terminal and value as a matrix of size (number_of_words+1)*(number_of_words+1)
    """
    nt_dict = {}
    for non_term in non_terminals:
      nt_dict[non_term] = [[fill_value for j in range(number_of_words+1)] for k in range(number_of_words+1)] # imp: initialize for each!
    return nt_dict

def get_nonterminals(rules):
    """
    Returns all non terminals that appear in the rules
    """
    d = {}
    for r in rules:
        d[r[0]] = 1
        # binary rule
        if len(r[1])==2:
            d[r[1][0]] = 1
            d[r[1][1]] = 1
    return d.keys()

def find_prob(lhs, rhs, rules):
  """
  This function returns the probability of the rule given it's lhs and rhs
  """
  for rule in rules:
    if len(rule[1])==1 and rule[0]==lhs and rhs==rule[1][0]:
      return rule[2]
  return 0

def create_tree(B, left, right, non_terminal, sent):
    """
    This is a recursive function that creates a nested list structure for parse tree

    Args:
        B (dict): Stores backppointers
        left (int): starting index of a consituent
        right ([type]): ending index of a consituent
        non_terminal (str): tag associated with the constituent
        sent (list): list of words in the sentence

    Returns:
        list: Nested list representation of a parse tree

    Example:
        For input sentence: "Her creditor makes a barrier"
        Return value of create_tree: ['S', ['NP', ['PRP$', 'Her'], ['NN', 'creditor']], ['VP', ['VBZ', 'makes'], ['NP', ['DT', 'a'], ['NN', 'barrier']]]]
    """
    if left<0 or left>=right:
        return None
        
    if left == right-1:
        return [non_terminal, sent[left]]

    split, left_tag, right_tag = B[non_terminal][left][right]
    left_ans = create_tree(B, left, split, left_tag, sent) 
    right_ans = create_tree(B, split, right, right_tag, sent)
    return [non_terminal, left_ans, right_ans]
  

def PCYK(sent, rules):
    """
    Given a probabilistic context-free grammar and lexicon and an input string this function implements the algorithm 
    for Probabilistic CYK.

    Args:
        sent (list): list of words in the sentence
        rules (list): list of lexical and grammar rules of the form (left-hand-side, right-hand-side, probability)

    Returns:
        tuple: If the sentece is in the language, returns a tuple containing the highest probability parse tree along with its probability
                Otherwise, return None
    """
    n = len(sent)
    non_terminals = get_nonterminals(rules)
    T = init_parse_triangle(n, non_terminals)
    Bk = init_parse_triangle(n, non_terminals)
    pr = np.float64(0.0)

    for i in range(1,n+1): # i values are from 0 to n
      for nt in non_terminals:
        pr1 = find_prob(nt, sent[i-1], rules) 
        T[nt][i-1][i] = pr1
        
      for j in range(i-2,-1,-1): # j values are from 0 to i-2
        # split point
        for k in range(j+1, i): # k values are from j+1 to i-1
          for rule in rules:
            # binary rule
            if len(rule[1]) == 2:
              A, B, C = rule[0], rule[1][0], rule[1][1]
              pr = np.float64(np.float64(T[B][j][k]) * np.float64(T[C][k][i]) * np.float64(rule[2]))
              if pr > T[A][j][i]:
                T[A][j][i] = pr
                Bk[A][j][i] = [k,B,C]
    
    if T['S'][0][n]>0:
      # create a  nested list using back pointers
      tree = create_tree(Bk, 0, n, 'S', sent)
      return (tree, T['S'][0][n])

    return None

def get_rules():
    """
    Lexical rule example:('WRB', ['how'], 1.0)
    Grammar rule example: ('VP', ['VP', 'NP'], 0.0010309278350515464)

    Returns:
        list: A list of lexical and grammar rules
    """
    lexicon_rules = genGrammar('./pcyk_data/lexicon.txt')
    grammar_rules = genGrammar('./pcyk_data/grammar.txt')
    rules = lexicon_rules + grammar_rules
    return rules

def compute_parse_tree(sent, rules):
    parsingResult = PCYK(sent, rules)

    if parsingResult != None:
        parseTree, prob = parsingResult
        print("Highest probability parse tree: ", parseTree)
        print("Probability: ", prob)
    else:
        print("Sorry! This sentence is NOT in the language.")
    
    pprint(PCYK(sent, rules)[0], indent=7, width=5)
    

if __name__=="__main__":
    rules = get_rules()

    # Examples to try out
    sent1 = "The reason was not high interest rates or labor costs".split()
    sent2 = "Her creditor makes a barrier".split()
    sent3 = "I guess this is not going to work".split()

    compute_parse_tree(sent1, rules)
    
