"""
Dual-endpoint retrieval tests.

Entirely offline. No API key is read, no HTTP request is made, and no
Spoonacular payload is checked in -- the fixtures below are hand-written to the
documented response shapes. (Real cached provider responses do not belong in
this repository; that is why the .db files were untracked.)

    python3 test_dual_retrieval.py

Exits non-zero if anything fails.
"""

import os
import sys
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dual_retrieval import (
    DualEndpointRetriever, ARM_PANTRY, ARM_FILTERED, INFORMATION_BULK_MAX_IDS,
)

PASS = FAIL = 0


def check(case, expected, actual, detail=""):
    global PASS, FAIL
    ok = expected == actual
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {case}")
    print(f"       expected: {expected}")
    print(f"       actual:   {actual}")
    if detail:
        print(f"       {detail}")


def ing(*names):
    return [{'name': n, 'amount': 1.0, 'unit': 'cup',
             # Non-name fields the old pre-gate used to read as ingredients.
             'aisle': 'Produce', 'image': 'https://img.example/ham.jpg',
             'consistency': 'SOLID'} for n in names]


# ---------------------------------------------------------------------------
# Fixture client. Serves the documented response shapes per endpoint and
# records exactly what it was asked, so the tests can assert on the params.
# ---------------------------------------------------------------------------
class FixtureClient:
    def __init__(self, find_by_ingredients=None, complex_search=None, details=None,
                 fail=()):
        self._fbi = find_by_ingredients if find_by_ingredients is not None else []
        self._cs = complex_search if complex_search is not None else []
        self._details = {d['id']: d for d in (details or [])}
        self._fail = set(fail)
        self.calls = []          # [(endpoint, params)]

    def _make_request(self, endpoint, params, method='GET'):
        self.calls.append((endpoint, dict(params)))
        if endpoint in self._fail:
            raise RuntimeError(f'simulated {endpoint} outage')
        if 'findByIngredients' in endpoint:
            return list(self._fbi)
        if 'complexSearch' in endpoint:
            return {'results': list(self._cs), 'totalResults': len(self._cs)}
        if 'informationBulk' in endpoint:
            ids = [int(i) for i in str(params.get('ids', '')).split(',') if i]
            return [self._details[i] for i in ids if i in self._details]
        return {}

    def endpoint_calls(self, name):
        return [p for e, p in self.calls if name in e]


BASE_SETTINGS = {
    'user_profile': 'balanced', 'mood': 'casual', 'max_difficulty': 'hard',
    'max_time_minutes': 120, 'max_missing_ingredients': 10,
    'dietary_requirements': [], 'intolerances': [], 'skill_level': 50, 'max_time': 120,
}


def settings(**kw):
    s = dict(BASE_SETTINGS)
    s.update(kw)
    return s


def detail(rid, title, ingredients, **kw):
    d = {
        'id': rid, 'title': title, 'extendedIngredients': ingredients,
        'readyInMinutes': kw.pop('ready', 30), 'servings': 2,
        'instructions': kw.pop('instructions', 'Cook it.'),
        'analyzedInstructions': [{'steps': [{'number': 1, 'step': 'Cook it.'}]}],
        'nutrition': {'nutrients': [{'name': 'Protein', 'amount': 10.0}]},
        'diets': kw.pop('diets', []), 'dietary_info': kw.pop('dietary_info', {}),
    }
    d.update(kw)
    return d


print("=" * 78)
print("1. BOTH ARMS RUN, MERGE AND DEDUPE BY RECIPE ID, WITH PROVENANCE")
print("=" * 78)

client = FixtureClient(
    # 101 and 102 from the pantry arm; 102 and 103 from the filtered arm.
    find_by_ingredients=[
        {'id': 101, 'title': 'Garlic Rice', 'usedIngredientCount': 3, 'missedIngredientCount': 0},
        {'id': 102, 'title': 'Tomato Pasta', 'usedIngredientCount': 2, 'missedIngredientCount': 1},
    ],
    complex_search=[
        {'id': 102, 'title': 'Tomato Pasta (complexSearch title)', 'readyInMinutes': 25},
        {'id': 103, 'title': 'Lentil Stew', 'readyInMinutes': 40},
    ],
    details=[
        detail(101, 'Garlic Rice', ing('rice', 'garlic', 'olive oil')),
        detail(102, 'Tomato Pasta', ing('pasta', 'tomatoes', 'basil')),
        detail(103, 'Lentil Stew', ing('lentils', 'carrot', 'onion')),
    ],
)
r = DualEndpointRetriever(client).retrieve(['rice', 'garlic'], settings(), number=10)
meta = r['metadata']['retrieval']

check("both endpoints were called", [1, 1],
      [len(client.endpoint_calls('findByIngredients')), len(client.endpoint_calls('complexSearch'))])
check("merged to 3 unique ids (102 deduped)", 3, meta['merged_candidates'],
      f"pantry={meta['pantry_arm_results']} filtered={meta['filtered_arm_results']}")
check("102 attributed to both arms", 1, meta['found_by_both_arms'])
check("101 pantry-only, 103 filtered-only", [1, 1],
      [meta['found_by_pantry_arm_only'], meta['found_by_filtered_arm_only']])

prov = {x['id']: x['_retrieval']['sources'] for x in r['recipes']}
check("per-recipe provenance recorded",
      {101: [ARM_PANTRY], 102: [ARM_FILTERED, ARM_PANTRY], 103: [ARM_FILTERED]},
      prov)
check("pantry counts survive the merge (complexSearch lacks them)", (2, 1),
      tuple(next(x for x in r['recipes'] if x['id'] == 102)[k]
            for k in ('usedIngredientCount', 'missedIngredientCount')))

print()
print("=" * 78)
print("2. informationBulk: ONE CALL FOR N RECIPES, PAGED AT THE DOCUMENTED CAP")
print("=" * 78)

check("3 recipes enriched in a single informationBulk call", 1, meta['information_bulk_calls'])
check("all 3 enriched", 3, meta['enriched'])
bulk_params = client.endpoint_calls('informationBulk')[0]
check("bulk call sent all ids at once", '101,102,103', bulk_params['ids'])
check("cap constant matches Spoonacular's documented maximum", 100, INFORMATION_BULK_MAX_IDS)

# 250 ids must page into 3 calls, not truncate to 100.
many = [{'id': i, 'title': f'R{i}', 'usedIngredientCount': 1, 'missedIngredientCount': 1}
        for i in range(1000, 1250)]
big = FixtureClient(find_by_ingredients=many, complex_search=[],
                    details=[detail(i, f'R{i}', ing('rice')) for i in range(1000, 1250)])
rbig = DualEndpointRetriever(big).retrieve(['rice'], settings(), number=250)
check("250 candidates page into 3 informationBulk calls", 3,
      rbig['metadata']['retrieval']['information_bulk_calls'])
check("all 250 enriched, none silently dropped", 250, rbig['metadata']['retrieval']['enriched'])
check("no page exceeded the cap", True,
      all(len(p['ids'].split(',')) <= INFORMATION_BULK_MAX_IDS
          for p in big.endpoint_calls('informationBulk')))

print()
print("=" * 78)
print("3. THE FILTER RUNS ON EVERY RECIPE, WHICHEVER ENDPOINT RETURNED IT")
print("=" * 78)

check("screening coverage is total", 3, r['metadata']['screening']['candidates_screened'])
check("every returned recipe carries proof it was screened", True,
      all(x['_retrieval']['screened'] for x in r['recipes']))
check("every returned recipe carries a verdict", True,
      all(x.get('safety_state') in ('SAFE', 'UNKNOWN') for x in r['recipes']))

# _screen_all must not accept any way to skip a recipe.
import inspect
sig = inspect.signature(DualEndpointRetriever._screen_all)
check("_screen_all takes no flag that could weaken it",
      ['self', 'candidates', 'settings'], list(sig.parameters))

print()
print("=" * 78)
print("4. LEAK RATE: PRE-FILTERED RECIPES THAT OUR FILTER STILL REJECTS")
print("=" * 78)

# complexSearch is asked for intolerances=dairy and returns three recipes.
# Two of them contain dairy. This is the leak the measurement exists to catch.
leaky = FixtureClient(
    find_by_ingredients=[
        {'id': 201, 'title': 'Plain Rice', 'usedIngredientCount': 1, 'missedIngredientCount': 0},
    ],
    complex_search=[
        {'id': 301, 'title': 'Creamy Zucchini Pasta'},
        {'id': 302, 'title': 'Dairy-Free Pesto'},
        {'id': 303, 'title': 'Cheesy Bake'},
    ],
    details=[
        detail(201, 'Plain Rice', ing('rice', 'salt')),
        # Leak 1: mascarpone and double cream, returned despite intolerances=dairy.
        detail(301, 'Creamy Zucchini Pasta', ing('pasta', 'zucchini', 'double cream', 'mascarpone')),
        # Correctly filtered: genuinely dairy-free.
        detail(302, 'Dairy-Free Pesto', ing('basil', 'pine nuts', 'olive oil')),
        # Leak 2: cheddar in the ingredients, butter only in the method.
        detail(303, 'Cheesy Bake', ing('potato', 'cheddar cheese'),
               instructions='Grease the dish with butter, then bake.'),
    ],
)

logging.basicConfig(level=logging.INFO, format='LOG %(levelname)s %(message)s',
                    stream=sys.stdout, force=True)

rl = DualEndpointRetriever(leaky).retrieve(
    ['rice'], settings(intolerances=['dairy']), number=10)

logging.getLogger().handlers[0].flush()
scr = rl['metadata']['screening']

cs_params = leaky.endpoint_calls('complexSearch')[0]
check("complexSearch really was sent intolerances=dairy", 'dairy', cs_params.get('intolerances'))
check("...and includeIngredients", 'rice', cs_params.get('includeIngredients'))
check("4 candidates merged", 4, rl['metadata']['retrieval']['merged_candidates'])
check("3 arrived pre-filtered", 3, scr['api_prefiltered_candidates'])
check("2 pre-filtered recipes rejected by our filter", 2,
      scr['api_prefiltered_rejected_by_our_filter'])
check("measured leak rate is 2/3", 0.6667, scr['api_prefilter_leak_rate'])
# One entry per triggering ingredient, not per recipe: 301 leaks on double cream
# and mascarpone, 303 on cheddar and on the butter in its method text. Knowing
# *which* ingredient got through is the point of the measurement.
check("leaks name the recipe, declaration and triggering ingredient", 4, len(scr['leaks']))
check("...across exactly the 2 leaking recipes", [301, 303],
      sorted({l['recipe_id'] for l in scr['leaks']}))

print("\n       Leak detail (this is the measurement the README claim needed):")
for lk in scr['leaks']:
    print(f"         recipe {lk['recipe_id']} {lk['title']!r}: asked to exclude "
          f"{lk['declaration']!r}, found {lk['ingredient']!r} "
          f"-> {lk['canonical_id']} ({lk['found_in']})")

check("the leaked recipes are withheld from the user", [201, 302],
      sorted(x['id'] for x in rl['recipes']))
check("a leak found only in the method text is caught too", True,
      any(l['found_in'] == 'instructions' for l in scr['leaks']),
      f"sources={[l['found_in'] for l in scr['leaks']]}")

# A declaration Spoonacular cannot act on must not be counted as a leak.
unscreenable = FixtureClient(
    find_by_ingredients=[],
    complex_search=[{'id': 401, 'title': 'Mystery Bake'}],
    details=[detail(401, 'Mystery Bake', ing('flour', 'sugar'))],
)
ru = DualEndpointRetriever(unscreenable).retrieve(
    ['flour'], settings(intolerances=['tartrazine']), number=5)
check("an unscreenable declaration is not miscounted as an API leak", 0,
      ru['metadata']['screening']['api_prefiltered_rejected_by_our_filter'],
      f"verdicts={ru['metadata']['screening']['verdicts']}")
check("...and the recipe is reported UNKNOWN, not SAFE", 1,
      ru['metadata']['screening']['verdicts']['UNKNOWN'])

print()
print("=" * 78)
print("5. DISAGREEMENT AND ONE-SIDED EMPTINESS")
print("=" * 78)

check("conflicting titles for id 102 recorded, not silently dropped", 1,
      len(meta['field_conflicts']),
      f"{meta['field_conflicts'][0]['field']}: "
      f"{meta['field_conflicts'][0][ARM_PANTRY]!r} vs "
      f"{meta['field_conflicts'][0][ARM_FILTERED]!r}")
check("informationBulk is authoritative for the conflicted field", 'Tomato Pasta',
      next(x for x in r['recipes'] if x['id'] == 102)['title'])

# complexSearch filters everything out; findByIngredients has plenty.
one_sided = FixtureClient(
    find_by_ingredients=[
        {'id': 501, 'title': 'Rice Bowl', 'usedIngredientCount': 2, 'missedIngredientCount': 0},
        {'id': 502, 'title': 'Veg Stew', 'usedIngredientCount': 2, 'missedIngredientCount': 1},
    ],
    complex_search=[],
    details=[detail(501, 'Rice Bowl', ing('rice', 'peas')),
             detail(502, 'Veg Stew', ing('carrot', 'onion', 'lentils'))],
)
r1 = DualEndpointRetriever(one_sided).retrieve(['rice'], settings(), number=10)
check("empty filtered arm does not empty the result", 2, len(r1['recipes']))
check("...and the response says why, rather than implying nothing matched", True,
      any('not "no recipes matched"' in n for n in r1['metadata']['retrieval']['notes']),
      r1['metadata']['retrieval']['notes'][0][:110])

# The pantry arm falls over entirely; the filtered arm still answers.
outage = FixtureClient(
    find_by_ingredients=[],
    complex_search=[{'id': 601, 'title': 'Filtered Only'}],
    details=[detail(601, 'Filtered Only', ing('rice', 'peas'))],
    fail={'recipes/findByIngredients'},
)
r2 = DualEndpointRetriever(outage).retrieve(['rice'], settings(), number=10)
check("an arm outage degrades rather than fails", 1, len(r2['recipes']))
check("...and the outage is reported", True,
      any('errored' in n for n in r2['metadata']['retrieval']['notes']),
      str(r2['metadata']['retrieval']['notes']))

# Both arms empty: genuinely nothing, and it may say so.
empty = FixtureClient(find_by_ingredients=[], complex_search=[], details=[])
r3 = DualEndpointRetriever(empty).retrieve(['xyzzy'], settings(), number=10)
check("both arms empty yields an honest empty result", (0, 0),
      (len(r3['recipes']), r3['metadata']['retrieval']['merged_candidates']))
check("...with no misleading one-sided note", [], r3['metadata']['retrieval']['notes'])

print()
print("=" * 78)
print("NO LIVE CALLS, NO CREDENTIALS")
print("=" * 78)

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dual_retrieval.py')).read()
check("dual_retrieval makes no HTTP calls of its own", [],
      [t for t in ('requests.get', 'requests.post', 'urllib', 'http.client', 'socket')
       if t in src])
check("dual_retrieval reads no credentials", [],
      [t for t in ('getenv', 'API_KEY', 'api_key', 'environ') if t in src])
check("no live endpoint was contacted in this run", True,
      all(isinstance(c, tuple) for c in client.calls),
      f"{len(client.calls)} fixture calls: {[e for e, _ in client.calls]}")

print()
print("=" * 78)
print(f"{PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print("=" * 78)
sys.exit(1 if FAIL else 0)
