"""
Contains static mappings for buildings, floors, and classrooms.
"""

# Maps building keys to their floors and the classrooms on each floor.
# Format: { "BuildingKey": { floor_number: [ (classroom_id, building_id), ... ] } }
BUILDING_FLOOR_MAP = {
    "A": {
        1: [
            ("5f775da9bb0c1600171ae370", "5f6cb2c183c80e0018f4d46"),  # A-1-1
            ("5f778ceabab2280018354c66", "5f6cb2c183c80e0018f4d46"),  # A-1-2
            ("5f77a3c28e23b1001b1b8dd1", "5f6cb2c183c80e0018f4d46"),  # A-1-3
            ("5f77ac63caaa8600182d1aa3", "5f6cb2c183c80e0018f4d46"),  # A-1-4
            ("5f7ede92090abe00160f2b63", "5f6cb2c183c80e0018f4d46"),  # A-1-5
            ("5f7eebfa090abe00160f3069", "5f6cb2c183c80e0018f4d46"),  # A-1-6
            ("6038e6b089cb050017681bc6", "5f6cb2c183c80e0018f4d46"),  # A-1-7
            ("6038e6f495192a0018abbe35", "5f6cb2c183c80e0018f4d46")   # A-1-8
        ],
        0: [
            ("6144b30f4478e70018ec408f", "5f6cb2c183c80e0018f4d46"),  # A-S-1
            ("6144b36b4478e70018ec4091", "5f6cb2c183c80e0018f4d46"),  # A-S-2
            ("6144b4404478e70018ec409d", "5f6cb2c183c80e0018f4d46"),  # A-S-3
            ("6144b4a006477900174b0ce3", "5f6cb2c183c80e0018f4d46"),  # A-S-6
            ("6144b4c14478e70018ec40d5", "5f6cb2c183c80e0018f4d46"),  # A-S-7
            ("6144b4da06477900174b0cf2", "5f6cb2c183c80e0018f4d46")   # A-S-8
        ],
        -1: [
            ("6144b558dec1980017698b99", "5f6cb2c183c80e0018f4d46"),  # A-T-1
            ("6144b5bbdec1980017698b9d", "5f6cb2c183c80e0018f4d46"),  # A-T-2
            ("6144b5f7dec1980017698ba9", "5f6cb2c183c80e0018f4d46"),  # A-T-3
            ("6144b62e06477900174b0cfd", "5f6cb2c183c80e0018f4d46"),  # A-T-4
            ("6144b6dedec1980017698bae", "5f6cb2c183c80e0018f4d46"),  # A-T-5
            ("6144b73f4478e70018ec4130", "5f6cb2c183c80e0018f4d46"),  # A-T-6
            ("6144b6bb4478e70018ec412c", "5f6cb2c183c80e0018f4d46"),  # A-T-7
            ("6144b77e4478e70018ec4133", "5f6cb2c183c80e0018f4d46"),  # A-T-8
            ("6144b7af06477900174b0d23", "5f6cb2c183c80e0018f4d46"),  # A-T-9
            ("6144b65ea673ee001710c74f", "5f6cb2c183c80e0018f4d46"),  # A-T-10
            ("6144b7d7a673ee001710c7bf", "5f6cb2c183c80e0018f4d46")   # A-T-11
        ],
    },

    "B": {
        1: [
            ("6145bffa0058d500181757ed", "5f6cb2c183c80e0018f4d476"),  # B-1-1
            ("6145c03aa58ea000182c799d", "5f6cb2c183c80e0018f4d476"),  # B-1-2
            ("6145c071d73db400176fccb5", "5f6cb2c183c80e0018f4d476"),  # B-1-3
            ("6145c0aa0058d500181757ee", "5f6cb2c183c80e0018f4d476"),  # B-1-4
            ("6145bf9a82d1800017fc0d8f", "5f6cb2c183c80e0018f4d476")   # B-1-10
        ],
        0: [
            ("6038e57140af57001887058c", "5f6cb2c183c80e0018f4d476")   # B-T-1
        ],
        2: [
            ("61533537d62c88001775dc80", "5f6cb2c183c80e0018f4d476"),  # B-2-1
            ("615335f628892300173bd6af", "5f6cb2c183c80e0018f4d476"),  # B-2-7
            ("615333ae28892300173bd5fd", "5f6cb2c183c80e0018f4d476"),  # B-2-18/19
            ("6153366628892300173bd6b0", "5f6cb2c183c80e0018f4d476"),  # B-2-11
            ("6153341c28892300173bd600", "5f6cb2c183c80e0018f4d476")   # B-2-21
        ],
        3: [
            ("6145c15e82d1800017fc0dc6", "5f6cb2c183c80e0018f4d476"),  # B-3-1
            ("6145c189d73db400176fccb8", "5f6cb2c183c80e0018f4d476"),  # B-3-2
            ("650dc6182a9e75003a003c6e", "5f6cb2c183c80e0018f4d476"),  # B-3-24
            ("615336cc28892300173bd6eb", "5f6cb2c183c80e0018f4d476"),  # LAB B-3-03
            ("61533732eaaf860017d57745", "5f6cb2c183c80e0018f4d476"),  # LAB B-3-12
            ("6153378731cd9200175bf597", "5f6cb2c183c80e0018f4d476"),  # LAB B-3-14
            ("61533860eaaf860017d57765", "5f6cb2c183c80e0018f4d476"),  # LAB B-3-17
            ("615338e428892300173bd75a", "5f6cb2c183c80e0018f4d476")   # LAB B-3-18/20
        ]
    },

    "SBA": {
        0: [
            ("5f6cb2c683c80e0018f4d5f5", "5f6cb2c183c80e0018f4d474"),  # SBA-T-1
            ("5f6cb2c683c80e0018f4d5ef", "5f6cb2c183c80e0018f4d474"),  # SBA-T-2A-B
            ("636e489dfcabcf0f2fdac9e0", "5f6cb2c183c80e0018f4d474"),  # SBA-T-2A
            ("6145ba0d0058d5001817571d", "5f6cb2c183c80e0018f4d474"),  # SBA-T-2B
            ("5f6cb2c683c80e0018f4d5f3", "5f6cb2c183c80e0018f4d474"),  # SBA-T-3
            ("5f6cb2c683c80e0018f4d5f1", "5f6cb2c183c80e0018f4d474")   # SBA-T-4
        ],
        1: [
            ("5f6cb2c783c80e0018f4d5fd", "5f6cb2c183c80e0018f4d474"),  # SBA-1-1
            ("5f6cb2c783c80e0018f4d5fb", "5f6cb2c183c80e0018f4d474"),  # SBA-1-2
            ("5f6cb2c683c80e0018f4d5f9", "5f6cb2c183c80e0018f4d474"),  # SBA-1-3
            ("5f6cb2c683c80e0018f4d5f7", "5f6cb2c183c80e0018f4d474"),  # SBA-1-4
            ("5f846f301859670017207611", "5f6cb2c183c80e0018f4d474")   # Aula Consorzio CISFA 1° P
        ],
        2: [
            ("5f6cb2c583c80e0018f4d582", "5f6cb2c183c80e0018f4d474"),  # SBA-2-1
            ("5f6cb2c583c80e0018f4d580", "5f6cb2c183c80e0018f4d474"),  # SBA-2-2
            ("5f6cb2c583c80e0018f4d57c", "5f6cb2c183c80e0018f4d474"),  # SBA-2-3
            ("5f6cb2c583c80e0018f4d57e", "5f6cb2c183c80e0018f4d474")   # SBA-2-4
        ]
    }
}

# Maps classroom IDs to their human-readable names for display purposes.
CLASSROOM_ID_TO_NAME = {
    # Edificio A, piano 1
    "5f775da9bb0c1600171ae370": "A-1-1",
    "5f778ceabab2280018354c66": "A-1-2",
    "5f77a3c28e23b1001b1b8dd1": "A-1-3",
    "5f77ac63caaa8600182d1aa3": "A-1-4",
    "5f7ede92090abe00160f2b63": "A-1-5",
    "5f7eebfa090abe00160f3069": "A-1-6",
    "6038e6b089cb050017681bc6": "A-1-7",
    "6038e6f495192a0018abbe35": "A-1-8",

    # Edificio A, piano seminterrato (0)
    "6144b30f4478e70018ec408f": "A-S-1",
    "6144b36b4478e70018ec4091": "A-S-2",
    "6144b4404478e70018ec409d": "A-S-3",
    "6144b4a006477900174b0ce3": "A-S-6",
    "6144b4c14478e70018ec40d5": "A-S-7",
    "6144b4da06477900174b0cf2": "A-S-8",

    # Edificio A, piano terra (-1)
    "6144b558dec1980017698b99":  "A-T-1",
    "6144b5bbdec1980017698b9d":  "A-T-2",
    "6144b5f7dec1980017698ba9":  "A-T-3",
    "6144b62e06477900174b0cfd":  "A-T-4",
    "6144b6dedec1980017698bae":  "A-T-5",
    "6144b73f4478e70018ec4130":  "A-T-6",
    "6144b6bb4478e70018ec412c":  "A-T-7",
    "6144b77e4478e70018ec4133":  "A-T-8",
    "6144b7af06477900174b0d23":  "A-T-9",
    "6144b65ea673ee001710c74f":  "A-T-10",
    "6144b7d7a673ee001710c7bf":  "A-T-11",

    # Edificio B, piano 1
    "6145bffa0058d500181757ed": "B-1-1",
    "6145c03aa58ea000182c799d": "B-1-2",
    "6145c071d73db400176fccb5": "B-1-3",
    "6145c0aa0058d500181757ee": "B-1-4",
    "6145bf9a82d1800017fc0d8f": "B-1-10",

    # Edificio B, piano terra (0)
    "6038e57140af57001887058c": "B-T-1",

    # Edificio B, piano 2
    "61533537d62c88001775dc80": "B-2-1",
    "615335f628892300173bd6af": "B-2-7",
    "615333ae28892300173bd5fd": "B-2-18/19",
    "6153366628892300173bd6b0": "B-2-11",
    "6153341c28892300173bd600": "B-2-21",

    # Edificio B, piano 3
    "6145c15e82d1800017fc0dc6": "B-3-1",
    "6145c189d73db400176fccb8": "B-3-2",
    "650dc6182a9e75003a003c6e": "B-3-24",
    "615336cc28892300173bd6eb": "LAB B-3-03",
    "61533732eaaf860017d57745": "LAB B-3-12",
    "6153378731cd9200175bf597": "LAB B-3-14",
    "61533860eaaf860017d57765": "LAB B-3-17",
    "615338e428892300173bd75a": "LAB B-3-18/20",

    # Edificio SBA, piano terra (0)
    "5f6cb2c683c80e0018f4d5f5": "SBA-T-1",
    "5f6cb2c683c80e0018f4d5ef": "SBA-T-2A-B",
    "636e489dfcabcf0f2fdac9e0": "SBA-T-2A",
    "6145ba0d0058d5001817571d": "SBA-T-2B",
    "5f6cb2c683c80e0018f4d5f3": "SBA-T-3",
    "5f6cb2c683c80e0018f4d5f1": "SBA-T-4",

    # Edificio SBA, piano 1
    "5f6cb2c783c80e0018f4d5fd": "SBA-1-1",
    "5f6cb2c783c80e0018f4d5fb": "SBA-1-2",
    "5f6cb2c683c80e0018f4d5f9": "SBA-1-3",
    "5f6cb2c683c80e0018f4d5f7": "SBA-1-4",
    "5f846f301859670017207611": "Aula Consorzio CISFA 1° P",

    # Edificio SBA, piano 2
    "5f6cb2c583c80e0018f4d582": "SBA-2-1",
    "5f6cb2c583c80e0018f4d580": "SBA-2-2",
    "5f6cb2c583c80e0018f4d57c": "SBA-2-3",
    "5f6cb2c583c80e0018f4d57e": "SBA-2-4",
}