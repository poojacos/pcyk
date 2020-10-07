# pcyk
Implementation of Probabilistic CYK algorithm

Example: 
  Input Sentence: "The reason was not high interest rates or labor costs"
  Output:
  
    Probability:  8.654317452774051e-29
    [      'S',
           [      'NP',
                  [      'DT',
                         'The'],
                  [      'NN',
                         'reason']],
           [      'VP',
                  [      'VBD',
                         'was'],
                  [      'NP',
                         [      'NP-CC',
                                [      'NP',
                                       [      'ADJP-NN',
                                              [      'ADJP',
                                                     [      'RB',
                                                            'not'],
                                                     [      'JJ',
                                                            'high']],
                                              [      'NN',
                                                     'interest']],
                                       [      'NNS',
                                              'rates']],
                                [      'CC',
                                       'or']],
                         [      'NP',
                                [      'NN',
                                       'labor'],
                                [      'NNS',
                                       'costs']]]]]
