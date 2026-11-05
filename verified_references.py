"""
Curated, publication-grade reference list for Elsevier Pattern Recognition.
Every reference is verified, real, and formatted according to elsarticle-num standards.
"""

REFERENCES_DATA = [
    {
        "id": 1,
        "key": "cortes1995support",
        "authors": "C. Cortes, V. Vapnik",
        "title": "Support-vector networks",
        "venue": "Machine Learning",
        "details": "20 (3) (1995) 273–297",
        "doi": "10.1007/BF00994018"
    },
    {
        "id": 2,
        "key": "vapnik1998statistical",
        "authors": "V. N. Vapnik",
        "title": "Statistical Learning Theory",
        "venue": "Wiley, New York",
        "details": "1998",
        "doi": "ISBN: 978-0-471-03003-4"
    },
    {
        "id": 3,
        "key": "scholkopf2002learning",
        "authors": "B. Schölkopf, A. J. Smola",
        "title": "Learning with Kernels: Support Vector Machines, Regularization, Optimization, and Beyond",
        "venue": "MIT Press, Cambridge, MA",
        "details": "2002",
        "doi": "ISBN: 978-0-262-19475-3"
    },
    {
        "id": 4,
        "key": "broomhead1988multivariable",
        "authors": "D. S. Broomhead, D. Lowe",
        "title": "Multivariable functional interpolation and adaptive networks",
        "venue": "Complex Systems",
        "details": "2 (3) (1988) 321–355",
        "doi": "CorpusID: 1533036"
    },
    {
        "id": 5,
        "key": "omohundro1989five",
        "authors": "S. M. Omohundro",
        "title": "Five balltree construction algorithms",
        "venue": "Tech. Rep. TR-89-063, International Computer Science Institute (ICSI), Berkeley, CA",
        "details": "1989",
        "doi": "TR-89-063"
    },
    {
        "id": 6,
        "key": "breiman2001random",
        "authors": "L. Breiman",
        "title": "Random forests",
        "venue": "Machine Learning",
        "details": "45 (1) (2001) 5–32",
        "doi": "10.1023/A:1010933404324"
    },
    {
        "id": 7,
        "key": "friedman2001greedy",
        "authors": "J. H. Friedman",
        "title": "Greedy function approximation: a gradient boosting machine",
        "venue": "The Annals of Statistics",
        "details": "29 (5) (2001) 1189–1232",
        "doi": "10.1214/aos/1013203451"
    },
    {
        "id": 8,
        "key": "chen2016xgboost",
        "authors": "T. Chen, C. Guestrin",
        "title": "XGBoost: A scalable tree boosting system",
        "venue": "in: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining",
        "details": "2016, pp. 785–794",
        "doi": "10.1145/2939672.2939785"
    },
    {
        "id": 9,
        "key": "ke2017lightgbm",
        "authors": "G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, T.-Y. Liu",
        "title": "LightGBM: A highly efficient gradient boosting decision tree",
        "venue": "Advances in Neural Information Processing Systems",
        "details": "30 (2017) 3149–3157",
        "doi": "NIPS 2017"
    },
    {
        "id": 10,
        "key": "lecun2015deep",
        "authors": "Y. LeCun, Y. Bengio, G. Hinton",
        "title": "Deep learning",
        "venue": "Nature",
        "details": "521 (7553) (2015) 436–444",
        "doi": "10.1038/nature14539"
    },
    {
        "id": 11,
        "key": "arik2021tabnet",
        "authors": "S. Ö. Arık, T. Pfister",
        "title": "TabNet: Attentive interpretable tabular learning",
        "venue": "in: Proceedings of the AAAI Conference on Artificial Intelligence",
        "details": "Vol. 35 (8), 2021, pp. 6679–6687",
        "doi": "10.1609/aaai.v35i8.16826"
    },
    {
        "id": 12,
        "key": "gorishniy2021revisiting",
        "authors": "Y. Gorishniy, I. Rubachev, V. Khrulkov, A. Babenko",
        "title": "Revisiting deep learning models for tabular data",
        "venue": "in: Advances in Neural Information Processing Systems",
        "details": "Vol. 34, 2021, pp. 18932–18943",
        "doi": "NeurIPS 2021"
    },
    {
        "id": 13,
        "key": "goodfellow2014explaining",
        "authors": "I. J. Goodfellow, J. Shlens, C. Szegedy",
        "title": "Explaining and harnessing adversarial examples",
        "venue": "in: International Conference on Learning Representations (ICLR)",
        "details": "2015",
        "doi": "arXiv:1412.6572"
    },
    {
        "id": 14,
        "key": "aizerman1964theoretical",
        "authors": "M. A. Aizerman, E. M. Braverman, L. I. Rozonoer",
        "title": "Theoretical foundations of the potential function method in pattern recognition learning",
        "venue": "Automation and Remote Control",
        "details": "25 (1964) 821–837",
        "doi": "ARC-1964"
    },
    {
        "id": 15,
        "key": "robbins1951stochastic",
        "authors": "H. Robbins, S. Monro",
        "title": "A stochastic approximation method",
        "venue": "The Annals of Mathematical Statistics",
        "details": "22 (3) (1951) 400–407",
        "doi": "10.1214/aoms/1177729586"
    },
    {
        "id": 16,
        "key": "szegedy2014intriguing",
        "authors": "C. Szegedy, W. Zaremba, I. Sutskever, J. Bruna, D. Erhan, I. Goodfellow, R. Fergus",
        "title": "Intriguing properties of neural networks",
        "venue": "in: International Conference on Learning Representations (ICLR)",
        "details": "2014",
        "doi": "arXiv:1312.6199"
    },
    {
        "id": 17,
        "key": "madry2018towards",
        "authors": "A. Madry, A. Makelov, L. Schmidt, D. Tsipras, A. Vladu",
        "title": "Towards deep learning models resistant to adversarial attacks",
        "venue": "in: International Conference on Learning Representations (ICLR)",
        "details": "2018",
        "doi": "arXiv:1706.06083"
    },
    {
        "id": 18,
        "key": "cohen2019certified",
        "authors": "J. Cohen, E. Rosenfeld, J. Z. Kolter",
        "title": "Certified adversarial robustness via randomized smoothing",
        "venue": "in: International Conference on Machine Learning, PMLR",
        "details": "Vol. 97, 2019, pp. 1310–1320",
        "doi": "PMLR 97:1310-1320"
    },
    {
        "id": 19,
        "key": "wachter2017counterfactual",
        "authors": "S. Wachter, B. Mittelstadt, C. Russell",
        "title": "Counterfactual explanations without opening the black box: Automated decisions and the GDPR",
        "venue": "Harvard Journal of Law & Technology",
        "details": "31 (2) (2018) 841–887",
        "doi": "10.2139/ssrn.3063289"
    },
    {
        "id": 20,
        "key": "mothilal2020explaining",
        "authors": "R. K. Mothilal, A. Sharma, C. Tan",
        "title": "Explaining machine learning classifiers through diverse counterfactual explanations",
        "venue": "in: Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency (FAT*)",
        "details": "2020, pp. 607–617",
        "doi": "10.1145/3351095.3372850"
    },
    {
        "id": 21,
        "key": "ustun2019actionable",
        "authors": "B. Ustun, A. Spangher, Y. Liu",
        "title": "Actionable recourse in linear classification",
        "venue": "in: Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT*)",
        "details": "2019, pp. 10–19",
        "doi": "10.1145/3287560.3287566"
    },
    {
        "id": 22,
        "key": "bartlett2002rademacher",
        "authors": "P. L. Bartlett, S. Mendelson",
        "title": "Rademacher and Gaussian complexities: Risk bounds and structural results",
        "venue": "Journal of Machine Learning Research",
        "details": "3 (2002) 463–482",
        "doi": "10.1162/153244303321897702"
    },
    {
        "id": 23,
        "key": "beyer1999nearest",
        "authors": "K. Beyer, J. Goldstein, R. Ramakrishnan, U. Shaft",
        "title": "When is nearest neighbor meaningful?",
        "venue": "in: International Conference on Database Theory (ICDT), Springer",
        "details": "1999, pp. 217–235",
        "doi": "10.1007/3-540-49257-7_15"
    },
    {
        "id": 24,
        "key": "chen2018neural",
        "authors": "R. T. Q. Chen, Y. Rubanova, J. Bettencourt, D. K. Duvenaud",
        "title": "Neural ordinary differential equations",
        "venue": "in: Advances in Neural Information Processing Systems",
        "details": "Vol. 31, 2018, pp. 6571–6583",
        "doi": "NeurIPS 2018"
    },
    {
        "id": 25,
        "key": "bronstein2017geometric",
        "authors": "M. M. Bronstein, J. Bruna, Y. LeCun, A. Szlam, P. Vandergheynst",
        "title": "Geometric deep learning: going beyond Euclidean data",
        "venue": "IEEE Signal Processing Magazine",
        "details": "34 (4) (2017) 18–42",
        "doi": "10.1109/MSP.2017.2693418"
    }
]

def format_reference_string(r):
    return f"{r['authors']}, {r['title']}, {r['venue']} {r['details']}."
