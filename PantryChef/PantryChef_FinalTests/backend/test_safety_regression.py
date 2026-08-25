"""
Safety and scoring regression suite.

Every case here is a defect that was found by executing the shipping code and
observing what it actually returned. They are kept as permanent tests so the
same failure cannot come back quietly.

Runs entirely against local fixtures. It calls no network service: no
Spoonacular, no Gemini, no API key. That is a property worth protecting -- a
safety verdict that needs a paid third party to be correct is not a safety
verdict.

    python3 test_safety_regression.py

Exits non-zero if anything fails.
"""
import sys, os, importlib.util

BACKEND = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
sys.path.insert(0, BACKEND)
spec = importlib.util.spec_from_file_location("Logic", os.path.join(BACKEND, "Logic.py"))
Logic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Logic)
Engine = Logic.PantryChefEngine

BASE = {
    'user_profile': 'balanced', 'mood': 'casual', 'max_difficulty': 'hard',
    'max_time_minutes': 120, 'max_missing_ingredients': 10,
    'dietary_requirements': [], 'intolerances': [], 'skill_level': 50,
    'max_time': 120,
}


def settings(**kw):
    s = dict(BASE)
    s.update(kw)
    return s


def ing(*names):
    return [{'name': n, 'amount': 1.0, 'unit': 'cup'} for n in names]


def recipe(title, ingredients, **kw):
    r = {
        'id': abs(hash(title)) % 100000, 'title': title,
        'extendedIngredients': ingredients,
        'usedIngredientCount': kw.pop('used', 1),
        'missedIngredientCount': kw.pop('missed', 1),
        'readyInMinutes': kw.pop('ready', 30), 'servings': kw.pop('servings', 2),
        'instructions': kw.pop('instructions', 'Cook it.'),
        'analyzedInstructions': [{'steps': []}],
        'nutrition': {'nutrients': [{'name': 'Protein', 'amount': 10.0}]},
        'diets': kw.pop('diets', []), 'dietary_info': kw.pop('dietary_info', {}),
    }
    r.update(kw)
    return r


def verdict(rec, **s):
    """Run the safety gate and report the verdict in a version-agnostic way."""
    e = Engine(settings(**s))
    out = e._apply_safety_check(rec)
    state = out.get('safety_state')
    if state is None:  # pre-fix code has no three-state verdict
        state = 'SAFE(passed=True)' if out.get('passed', True) else 'UNSAFE(passed=False)'
    return state, out


def shows(rec, **s):
    """Does the recipe survive the full pipeline and reach the user?"""
    e = Engine(settings(**s))
    return len(e.process_results([rec])) > 0


PASS = FAIL = 0
def check(case, expected, actual, detail=""):
    global PASS, FAIL
    ok = expected == actual
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {case}")
    print(f"       expected: {expected}")
    print(f"       actual:   {actual}")
    if detail:
        print(f"       {detail}")


print("=" * 78)
print("SAFETY GATE")
print("=" * 78)

# D-1  free-text allergen declared safe
st, out = verdict(recipe('Shrimp Scampi', ing('shrimp', 'garlic')), intolerances=['shellfish'])
check("D-1  shellfish declared on Shrimp Scampi", "UNSAFE", st.split('(')[0],
      f"reason={out.get('safety_reason') or out.get('reason')!r} score={out.get('safety_score')}")

st, out = verdict(recipe('Pad Thai', ing('rice noodles', 'peanuts', 'egg')), intolerances=['peanuts'])
check("D-1b peanuts declared on peanut Pad Thai", "UNSAFE", st.split('(')[0],
      f"reason={out.get('safety_reason') or out.get('reason')!r}")

st, out = verdict(recipe('Edamame Salad', ing('soybeans', 'sesame oil')), intolerances=['soy'])
check("D-1c soy declared on soybean salad", "UNSAFE", st.split('(')[0])

st, out = verdict(recipe('Tahini Dressing', ing('tahini', 'lemon juice')), intolerances=['sesame'])
check("D-1d sesame declared on tahini dressing", "UNSAFE", st.split('(')[0])

# R-11 allergen the table cannot screen for
st, out = verdict(recipe('Mystery Stew', ing('carrot', 'potato')), intolerances=['tartrazine'])
check("R-11 allergen not in table -> cannot screen", "UNKNOWN", st.split('(')[0],
      f"reason={out.get('safety_reason') or out.get('reason')!r}")

# D-2  empty ingredient list certified safe
st, out = verdict(recipe('Mystery Stub', []), intolerances=['dairy', 'nuts'])
check("D-2  empty extendedIngredients", "UNKNOWN", st.split('(')[0],
      f"reason={out.get('safety_reason') or out.get('reason')!r} score={out.get('safety_score')}")

st, out = verdict({'id': 1, 'title': 'No Ingredients Field'}, intolerances=['dairy'])
check("D-2b ingredients field absent entirely", "UNKNOWN", st.split('(')[0])

# D-3  substring matching
eggp = recipe('Roasted Eggplant', ing('eggplant', 'olive oil'))
st, _ = verdict(eggp, intolerances=['eggs'])
check("D-3  eggplant is not egg", "SAFE", st.split('(')[0])
check("D-3a2 ... and the recipe is not hidden", True, shows(eggp, intolerances=['eggs']))

donut = recipe('Glazed Donuts', ing('donuts', 'sugar'))
st, _ = verdict(donut, intolerances=['nuts'])
check("D-3b donuts are not nuts", "SAFE", st.split('(')[0])
check("D-3b2 ... and the recipe is not hidden", True, shows(donut, intolerances=['nuts']))

st, out = verdict(recipe('Walnut Oil Salad', ing('walnut oil', 'lettuce')), intolerances=['nuts'])
check("D-3c walnut oil (singular) is a tree nut", "UNSAFE", st.split('(')[0],
      f"reason={out.get('safety_reason') or out.get('reason')!r}")

st, _ = verdict(recipe('Satay Skewers', ing('peanut butter', 'chicken')), intolerances=['dairy'])
check("D-3d peanut butter is not dairy", "SAFE", st.split('(')[0])

st, _ = verdict(recipe('Satay Skewers', ing('peanut butter', 'chicken')), intolerances=['peanuts'])
check("D-3e peanut butter is a peanut", "UNSAFE", st.split('(')[0])

bns = recipe('Butternut Squash Soup', ing('butternut squash', 'vegetable stock'))
st, _ = verdict(bns, intolerances=['dairy'])
check("D-3f butternut squash is not butter", "SAFE", st.split('(')[0])
check("D-3f2 ... and the recipe is not hidden", True, shows(bns, intolerances=['dairy']))

st, _ = verdict(recipe('Flourless Chocolate Cake', ing('dark chocolate', 'eggs', 'sugar')),
                intolerances=['gluten'])
check("D-3g flourless cake has no flour", "SAFE", st.split('(')[0])

st, _ = verdict(recipe('Graham Cracker Crust', ing('graham crackers', 'butter')),
                dietary_requirements=['vegetarian'])
check("D-3h graham is not ham", "SAFE", st.split('(')[0])

# D-4  SAFE_WORDS fail-open
st, out = verdict(recipe('Vegan-Style Mac and Cheese', ing('butter', 'cheddar cheese', 'macaroni')),
                  intolerances=['dairy'])
check("D-4  'Vegan' in title over real butter+cheddar", "UNSAFE", st.split('(')[0],
      f"reason={out.get('safety_reason') or out.get('reason')!r} score={out.get('safety_score')}")

st, out = verdict(recipe('Warm Salad', ing('goat cheese', 'beets')), intolerances=['dairy'])
check("D-4b goat cheese is dairy ('oat' in 'goat')", "UNSAFE", st.split('(')[0],
      f"score={out.get('safety_score')}")

st, out = verdict(recipe('Buttered Toast', ing('butter', 'almond extract', 'bread')),
                  dietary_requirements=['vegan'])
check("D-4c almond extract does not clear butter", "UNSAFE", st.split('(')[0],
      f"score={out.get('safety_score')}")

st, out = verdict(recipe('Gluten-Free Bread', ing('wheat flour', 'yeast', 'water')),
                  intolerances=['gluten'])
check("D-4d 'Gluten-Free' title over wheat flour", "UNSAFE", st.split('(')[0])

# D-5  early return hides later allergens
st, out = verdict(recipe('Cashew Milk Curry', ing('milk', 'cashew', 'curry powder')),
                  intolerances=['dairy', 'nuts'])
found = out.get('found_intolerances', out.get('matched_allergens', []))
check("D-5  multi-allergen: both reported", 2, len(found),
      f"found_intolerances={found}")

st, _ = verdict(recipe('Nut Cream Sauce', ing('almond', 'butter')), intolerances=['dairy', 'nuts'])
check("D-5b soft-deferred dairy must not skip the nut check", "UNSAFE", st.split('(')[0])

# D-6  if/elif dietary chain
st, out = verdict(recipe('Omelette', ing('milk', 'egg')),
                  dietary_requirements=['vegetarian', 'vegan'])
check("D-6  vegetarian+vegan screens vegan too", "UNSAFE", st.split('(')[0],
      f"reason={out.get('safety_reason') or out.get('reason')!r}")

st, _ = verdict(recipe('Beef Chilli', ing('ground beef', 'beans')), dietary_requirements=['vegan'])
check("D-6b vegan alone still catches meat", "UNSAFE", st.split('(')[0])

# D-13 instructions never scanned
st, _ = verdict(recipe('Pan-Seared Tofu', ing('tofu', 'soy sauce'),
                       instructions='Grease the pan with butter, then sear.'),
                intolerances=['dairy'])
check("D-13 butter in the method only", "UNSAFE", st.split('(')[0])

# D-7  ingredient image/aisle fields scanned as text
ham_img = [{'name': 'tomato', 'aisle': 'Meat', 'image': 'https://img.example/ham.jpg',
            'consistency': 'SOLID', 'amount': 2.0, 'unit': 'whole'}]
st, _ = verdict(recipe('Tomato Salad', ham_img), dietary_requirements=['vegetarian'])
check("D-7  ham.jpg image path is not an ingredient", "SAFE", st.split('(')[0])

# R-9  unresolved ingredient
st, out = verdict(recipe('Odd Bake', ing('flour', 'xanthan gum', 'zzzq')), intolerances=['dairy'])
names = str(out.get('unresolved_ingredients', out.get('safety_reason', '')))
check("R-9  unresolved ingredient -> UNKNOWN", "UNKNOWN", st.split('(')[0],
      f"unresolved={out.get('unresolved_ingredients')}")

# R-12 API boolean flag must not override ingredient evidence
st, _ = verdict(recipe('Seitan Wrap', ing('seitan', 'wheat flour'),
                       dietary_info={'glutenFree': True}), intolerances=['gluten'])
check("R-12 glutenFree flag over wheat flour", "UNSAFE", st.split('(')[0])

# extra vocabulary coverage the audit called out
st, _ = verdict(recipe('Protein Bar', ing('whey protein', 'casein', 'oats')), intolerances=['dairy'])
check("D-8  whey and casein are dairy", "UNSAFE", st.split('(')[0])

st, _ = verdict(recipe('Malted Barley Loaf', ing('barley malt', 'rye flour')), intolerances=['gluten'])
check("D-8b barley and rye are gluten", "UNSAFE", st.split('(')[0])

st, _ = verdict(recipe('Hollandaise', ing('hollandaise sauce', 'asparagus')), intolerances=['eggs'])
check("D-8c hollandaise is egg", "UNSAFE", st.split('(')[0])

# R-16 monotonicity: adding a declaration never loosens the verdict
ORDER = {'SAFE': 0, 'UNKNOWN': 1, 'UNSAFE': 2}
mono_ok = True
probe = recipe('Mixed Plate', ing('milk', 'cashew', 'wheat flour', 'shrimp'))
for extra in (['dairy'], ['dairy', 'nuts'], ['dairy', 'nuts', 'gluten'],
              ['dairy', 'nuts', 'gluten', 'shellfish']):
    prev = None
    s1, _ = verdict(probe, intolerances=extra[:-1] or [])
    s2, _ = verdict(probe, intolerances=extra)
    a, b = ORDER.get(s1.split('(')[0], 0), ORDER.get(s2.split('(')[0], 0)
    if b < a:
        mono_ok = False
check("R-16 monotonic under added declarations", True, mono_ok)

print()
print("=" * 78)
print("SCORING AND RANKING")
print("=" * 78)

# D-14 profiles mathematically identical
r = recipe('Sparse Match', ing('a', 'b'), used=2, missed=6)
scores = {}
for p in ('minimal_shopper', 'pantry_cleaner', 'balanced'):
    e = Engine(settings(user_profile=p, max_missing_ingredients=4))
    scores[p] = e._calculate_smart_score(r)['smart_score']
check("D-14 three profiles give three different scores", 3, len(set(scores.values())),
      f"scores={scores}")
check("D-14b minimal_shopper scores used=2/missed=6 below pantry_cleaner", True,
      scores['minimal_shopper'] < scores['pantry_cleaner'], f"scores={scores}")

# D-15 sort key is a constant
A = recipe('A-poor', ing('x'), used=1, missed=9, ready=200)
B = recipe('B-great', ing('y'), used=9, missed=0, ready=10)
e = Engine(settings(max_missing_ingredients=3, max_time_minutes=60, max_time=60))
res = e.process_results([A, B])
order = [x['title'] for x in res]
check("D-15 better recipe ranks first", ['B-great', 'A-poor'], order,
      f"confidences={[(x['title'], x.get('confidence'), x.get('match_confidence')) for x in res]}")

keys = [x.get('_metadata', {}).get('internal_debug', {}).get('rank_score') for x in res]
check("D-15b sort key is not a constant", True, len(set(keys)) > 1, f"rank_score={keys}")

# D-16 tired double multiplier
e = Engine(settings(mood='tired', max_time=60, max_time_minutes=60))
rr = recipe('Quick Thing', ing('z'), used=3, missed=0, ready=10)
fr = e._apply_soft_filters_with_penalties(rr)
sd = e._calculate_smart_score(rr)
rd = e._apply_reasoning(rr, sd['smart_score'], fr)
internal = rd['internal_debug']['internal_score']
check("D-16 tired ranking score stays within 0-100", True, 0 <= internal <= 100,
      f"internal_score={internal}")

# D-17 effort weight is read
e = Engine(settings(mood='tired'))
rr = recipe('Long Method', ing('z'), used=2, missed=1, ready=30,
            analyzedInstructions=[{'steps': [{'number': i} for i in range(14)]}])
fr = e._apply_soft_filters_with_penalties(rr)
sd = e._calculate_smart_score(rr)
rd = e._apply_reasoning(rr, sd['smart_score'], fr)
check("D-17 effort axis is bound to something real", True,
      'effort_score' in rd.get('internal_debug', {}),
      f"internal_debug keys={sorted(rd.get('internal_debug', {}).keys())}")

# D-21 KeyError landmine
try:
    e = Engine({'user_profile': 'balanced', 'mood': 'casual'})
    e.process_results([recipe('Bare Settings', ing('rice'))])
    ok = True
    err = 'no exception'
except Exception as ex:
    ok = False
    err = f"{type(ex).__name__}: {ex}"
check("D-21 missing max_missing_ingredients does not raise", True, ok, err)

# D-2 end-to-end: an unknown-verdict stub must not reach the user as safe
e = Engine(settings(intolerances=['dairy']))
out = e.process_results([recipe('Mystery Stub', [], used=1, missed=2)])
if out:
    st = out[0].get('_metadata', {}).get('safety_check', {}).get('safety_state', 'SAFE')
else:
    st = 'DROPPED'
check("D-2c stub reaching the UI is not labelled SAFE", True, st != 'SAFE', f"state={st}")

print()
print("=" * 78)
print("TABLE INTEGRITY AND PRODUCT CLAIMS")
print("=" * 78)

import allergen_table as AT

# R-32  every alias must round-trip to its own entry, so the table cannot
#       silently contain unreachable vocabulary.
bad = []
for cid, aliases in AT.ALIASES_BY_ID.items():
    for alias in aliases:
        ids, misses = AT.resolve_text(alias)
        if ids != [cid]:
            bad.append((alias, cid, ids))
check("R-32 every alias resolves to its own canonical entry", [], bad[:5],
      f"{len(bad)} alias(es) shadowed" if bad else "")

# Every declaration the UI can produce must be screenable.
unscreenable = [d for d in ("dairy", "gluten", "eggs", "peanuts", "tree nuts",
                            "soy", "shellfish", "fish", "sesame", "mustard",
                            "celery", "lupin", "sulphites", "molluscs")
                if not AT.resolve_declaration(d)]
check("R-11b UI-suggested declarations are all screenable", [], unscreenable)

# R-21  the product must not claim more than it can do. A grep, because this
#       kind of copy comes back.
FORBIDDEN = ("100% adherence", "100% accurate", "allergen-safe", "allergen safe",
             "guaranteed safe", "guarantees safety")
ROOT = os.path.abspath(os.path.join(BACKEND, "..", "..", ".."))
offenders = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames
                   if d not in (".git", "node_modules", "__pycache__", ".venv", "dist")]
    for fn in filenames:
        if not fn.endswith((".py", ".md", ".jsx", ".js", ".html", ".json")):
            continue
        if fn == os.path.basename(__file__):
            continue
        path = os.path.join(dirpath, fn)
        try:
            text = open(path, encoding="utf-8", errors="ignore").read().lower()
        except OSError:
            continue
        for phrase in FORBIDDEN:
            if phrase in text:
                offenders.append(f"{os.path.relpath(path, ROOT)}: {phrase!r}")
check("R-21 no unsupportable safety claims in the tree", [], sorted(set(offenders))[:5],
      f"{len(offenders)} occurrence(s)" if offenders else "")

# R-19/R-20  the safety module is offline by construction.
srcs = open(os.path.join(BACKEND, "allergen_table.py")).read()
banned = [t for t in ("import requests", "genai", "google.generativeai",
                      "urllib.request", "http.client", "socket")
          if t in srcs]
check("R-20 allergen table imports nothing that can reach a network", [], banned)

print()
print("=" * 78)
print(f"{PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print("=" * 78)
sys.exit(1 if FAIL else 0)
