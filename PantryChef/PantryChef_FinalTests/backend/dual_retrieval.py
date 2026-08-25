r"""
Dual-endpoint retrieval.

Two Spoonacular endpoints answer different questions, and the app was only ever
asking one of them properly:

    findByIngredients        ranks by pantry coverage. It is the only endpoint
                             that knows how much of a recipe you already own.
                             It cannot filter by diet or intolerance at all.

    complexSearch            accepts diet, intolerances, includeIngredients and
                             excludeIngredients, so it returns a denser set of
                             plausible candidates. Its ranking is much weaker --
                             it has no idea what is in your fridge.

Neither is sufficient. Running both and merging gives good ranking *and* good
density, at the cost of one extra search call.

    findByIngredients(pantry, ranking=1)      complexSearch(includeIngredients,
      -> best pantry ranking                     diet, intolerances,
      -> zero dietary filtering                   excludeIngredients)
                          \                  /   -> pre-filtered, denser
                           \                /    -> weak ranking
                            merge + dedupe by recipe id
                            (provenance recorded per recipe)
                                     |
                          informationBulk(ids)  -- one call per 100
                                     |
                    DETERMINISTIC SCREEN over EVERY recipe
                                     |
                UNSAFE dropped | UNKNOWN flagged | SAFE shown

The load-bearing rule, and the reason this module exists as its own file:

    THE SCREEN RUNS ON EVERY RECIPE, REGARDLESS OF WHICH ENDPOINT RETURNED IT.

Spoonacular's `intolerances` parameter is a quota and density optimisation. It
is never a verdict. A recipe that arrived pre-filtered for dairy is screened
exactly as hard as one that arrived from the unfiltered endpoint, because the
entire point of this project is that a third party's claim about safety is not
safety. `_screen_all` takes no argument that could weaken it and asserts it
screened everything before it returns.

And because that pre-filter demonstrably does leak, this module *measures* the
leak rate rather than assuming it away. When complexSearch is asked to exclude
dairy and returns a recipe our screen then rejects for dairy, that is recorded
with the recipe, the declaration and the exact ingredient that triggered it. The
result is a measured number where the README used to carry an invented one.

Offline by construction: this module makes no HTTP calls itself. It drives
whatever client it is handed, so the tests drive it with fixtures.
"""

from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
import logging

from Logic import PantryChefEngine, SAFE, UNSAFE, UNKNOWN
from allergen_table import TABLE_VERSION, resolve_declaration

logger = logging.getLogger(__name__)

# Endpoint identifiers used as provenance labels.
ARM_PANTRY = 'findByIngredients'
ARM_FILTERED = 'complexSearch'

# Spoonacular documents informationBulk as accepting at most 100 ids per call.
# The previous implementation sliced to [:100] and silently dropped the rest;
# this module pages instead.
INFORMATION_BULK_MAX_IDS = 100


class RetrievalCandidate:
    """
    One recipe id on its way through the pipeline, with the record of where it
    came from and what the API was asked to exclude when it did.

    `prefiltered_for` is the part that matters. It holds the declarations that
    complexSearch was told to filter on for this recipe. If our own screen later
    rejects the recipe for one of those same declarations, the API's filter
    leaked, and we can say so with evidence.
    """

    __slots__ = ('recipe_id', 'sources', 'stub', 'detail',
                 'prefiltered_for', 'field_conflicts')

    def __init__(self, recipe_id: int):
        self.recipe_id: int = recipe_id
        self.sources: Set[str] = set()
        self.stub: Dict[str, Any] = {}
        self.detail: Optional[Dict[str, Any]] = None
        self.prefiltered_for: Set[str] = set()
        self.field_conflicts: List[Dict[str, Any]] = []

    @property
    def api_prefiltered(self) -> bool:
        return ARM_FILTERED in self.sources and bool(self.prefiltered_for)

    def merged_recipe(self) -> Dict[str, Any]:
        """
        The recipe as the rest of the pipeline should see it.

        informationBulk detail wins on every field it supplies, because it is the
        authoritative record. The pantry counts are the exception: complexSearch
        and informationBulk do not return usedIngredientCount /
        missedIngredientCount at all, so those come from findByIngredients and
        must not be clobbered with the zeros the other arms imply.
        """
        merged: Dict[str, Any] = {}
        merged.update(self.stub)
        if self.detail:
            for key, value in self.detail.items():
                if key in ('usedIngredientCount', 'missedIngredientCount'):
                    continue
                merged[key] = value

        merged['id'] = self.recipe_id
        merged['_retrieval'] = {
            'sources': sorted(self.sources),
            'api_prefiltered': self.api_prefiltered,
            'api_prefiltered_for': sorted(self.prefiltered_for),
            'enriched': self.detail is not None,
            'field_conflicts': self.field_conflicts,
        }
        return merged


class DualEndpointRetriever:
    """
    Runs both retrieval arms, merges them, enriches once, and screens everything.

    The client is injected rather than constructed so that tests drive this with
    fixtures and it never needs an API key. It reads no credentials itself.
    """

    def __init__(self, api_client, engine_factory=PantryChefEngine):
        self.client = api_client
        self.engine_factory = engine_factory

    # -----------------------------------------------------------------
    # Arm 1: pantry coverage, no filtering available
    # -----------------------------------------------------------------
    def _arm_pantry(self, pantry: Sequence[str], number: int) -> Tuple[List[Dict], Optional[str]]:
        try:
            raw = self.client._make_request('recipes/findByIngredients', {
                'ingredients': ','.join(pantry),
                'number': number,
                'ranking': 1,          # maximise used ingredients
                'ignorePantry': 'true',
            })
        except Exception as exc:
            logger.warning("findByIngredients arm failed: %s", exc)
            return [], f'{type(exc).__name__}: {exc}'

        if isinstance(raw, list):
            return [r for r in raw if isinstance(r, dict) and r.get('id') is not None], None
        if isinstance(raw, dict) and isinstance(raw.get('results'), list):
            return [r for r in raw['results'] if isinstance(r, dict) and r.get('id') is not None], None
        return [], None

    # -----------------------------------------------------------------
    # Arm 2: pre-filtered, denser, weaker ranking
    # -----------------------------------------------------------------
    def _arm_filtered(
        self,
        pantry: Sequence[str],
        number: int,
        cuisine: Optional[str],
        meal_type: Optional[str],
        diet: Optional[str],
        intolerances: Sequence[str],
        exclude_ingredients: Sequence[str],
    ) -> Tuple[List[Dict], Set[str], Optional[str]]:
        """
        Returns (recipes, declarations_the_api_was_asked_to_exclude, error).

        The second element is what makes leak measurement possible: we only get
        to call something a leak if we know what we asked for.
        """
        params: Dict[str, Any] = {
            'number': number,
            'addRecipeInformation': 'false',
            'fillIngredients': 'false',
        }
        if pantry:
            params['includeIngredients'] = ','.join(pantry)

        asked_to_exclude: Set[str] = set()

        def usable(value: Optional[str]) -> bool:
            return bool(value) and str(value).strip().lower() not in ('any', 'none', 'null', '')

        if usable(cuisine):
            params['cuisine'] = cuisine
        if usable(meal_type):
            params['type'] = meal_type
        if usable(diet):
            params['diet'] = diet
            asked_to_exclude.add(str(diet).strip().lower())

        cleaned_intolerances = [str(i).strip() for i in (intolerances or []) if str(i).strip()]
        if cleaned_intolerances:
            # Spoonacular only understands its own intolerance vocabulary. Sending
            # a term it does not know is harmless but must NOT be recorded as
            # "asked to exclude", or an unscreenable declaration would look like a
            # leak when the API was never able to act on it in the first place.
            params['intolerances'] = ','.join(cleaned_intolerances)
            for declared in cleaned_intolerances:
                if resolve_declaration(declared):
                    asked_to_exclude.add(declared.lower())

        cleaned_excludes = [str(i).strip() for i in (exclude_ingredients or []) if str(i).strip()]
        if cleaned_excludes:
            params['excludeIngredients'] = ','.join(cleaned_excludes)

        try:
            raw = self.client._make_request('recipes/complexSearch', params)
        except Exception as exc:
            logger.warning("complexSearch arm failed: %s", exc)
            return [], asked_to_exclude, f'{type(exc).__name__}: {exc}'

        results: List[Dict] = []
        if isinstance(raw, dict):
            results = [r for r in (raw.get('results') or [])
                       if isinstance(r, dict) and r.get('id') is not None]
        elif isinstance(raw, list):
            results = [r for r in raw if isinstance(r, dict) and r.get('id') is not None]

        return results, asked_to_exclude, None

    # -----------------------------------------------------------------
    # Merge
    # -----------------------------------------------------------------
    @staticmethod
    def _merge(
        pantry_hits: Iterable[Dict],
        filtered_hits: Iterable[Dict],
        asked_to_exclude: Set[str],
    ) -> Tuple[List[RetrievalCandidate], List[Dict]]:
        """
        Deduplicate by recipe id, union the provenance, and record disagreements.

        Order is preserved from findByIngredients first, because that is the arm
        with meaningful ranking; complexSearch-only recipes are appended after.
        Ranking is redone downstream anyway, but a stable, explainable input
        order makes the pipeline debuggable.

        When both arms return the same id with different values for a field, the
        conflict is recorded on the candidate rather than silently resolved. The
        stub value from findByIngredients is kept, since informationBulk will
        overwrite it with the authoritative value moments later.
        """
        by_id: Dict[int, RetrievalCandidate] = {}
        order: List[int] = []
        conflicts: List[Dict] = []

        for hit in pantry_hits:
            rid = hit['id']
            if rid not in by_id:
                by_id[rid] = RetrievalCandidate(rid)
                order.append(rid)
            cand = by_id[rid]
            cand.sources.add(ARM_PANTRY)
            cand.stub.update(hit)

        for hit in filtered_hits:
            rid = hit['id']
            if rid not in by_id:
                by_id[rid] = RetrievalCandidate(rid)
                order.append(rid)
                by_id[rid].stub.update(hit)
            else:
                cand = by_id[rid]
                # Same recipe from both arms: note where they disagree.
                for key, new_value in hit.items():
                    if key in ('id',):
                        continue
                    if key in cand.stub and cand.stub[key] != new_value:
                        conflict = {
                            'recipe_id': rid,
                            'field': key,
                            ARM_PANTRY: cand.stub[key],
                            ARM_FILTERED: new_value,
                            'kept': cand.stub[key],
                            'note': 'kept findByIngredients value; informationBulk overrides both',
                        }
                        cand.field_conflicts.append(conflict)
                        conflicts.append(conflict)
                    elif key not in cand.stub:
                        cand.stub[key] = new_value
            by_id[rid].sources.add(ARM_FILTERED)
            by_id[rid].prefiltered_for |= set(asked_to_exclude)

        return [by_id[rid] for rid in order], conflicts

    # -----------------------------------------------------------------
    # Enrichment: one call per 100 ids, paged rather than truncated
    # -----------------------------------------------------------------
    def _enrich(self, candidates: Sequence[RetrievalCandidate]) -> int:
        ids = [c.recipe_id for c in candidates]
        if not ids:
            return 0

        details: Dict[int, Dict] = {}
        calls = 0
        for start in range(0, len(ids), INFORMATION_BULK_MAX_IDS):
            page = ids[start:start + INFORMATION_BULK_MAX_IDS]
            calls += 1
            try:
                raw = self.client._make_request('recipes/informationBulk', {
                    'ids': ','.join(str(i) for i in page),
                    'includeNutrition': 'true',
                    'fillIngredients': 'true',
                    'addRecipeInformation': 'true',
                })
            except Exception as exc:
                logger.warning("informationBulk page %d failed: %s", calls, exc)
                continue

            rows: List[Dict] = []
            if isinstance(raw, list):
                rows = raw
            elif isinstance(raw, dict):
                rows = raw.get('results') or [v for v in raw.values() if isinstance(v, dict)]

            for row in rows:
                if isinstance(row, dict) and row.get('id') is not None:
                    details[row['id']] = row

        for cand in candidates:
            if cand.recipe_id in details:
                cand.detail = details[cand.recipe_id]

        return calls

    # -----------------------------------------------------------------
    # Screening. Everything. No exceptions, no parameters.
    # -----------------------------------------------------------------
    def _screen_all(
        self,
        candidates: Sequence[RetrievalCandidate],
        settings: Dict[str, Any],
    ) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        Run the deterministic screen over every candidate.

        This function deliberately takes no flag, no allowlist and no provenance
        argument that could cause a recipe to skip screening. There is exactly
        one loop, it runs over the whole list, and the assertion at the end makes
        a future "optimisation" that skips pre-filtered recipes fail loudly
        instead of quietly shipping unscreened food to an allergic user.
        """
        engine = self.engine_factory(settings)

        screened: List[Dict] = []
        leaks: List[Dict] = []
        counts = {SAFE: 0, UNSAFE: 0, UNKNOWN: 0}
        prefiltered_total = 0
        prefiltered_rejected = 0
        screened_count = 0

        for cand in candidates:
            recipe = cand.merged_recipe()

            verdict = engine._apply_safety_check(recipe)
            screened_count += 1

            state = verdict.get('safety_state', UNKNOWN)
            counts[state] = counts.get(state, 0) + 1

            recipe['_retrieval']['screened'] = True
            recipe['safety_state'] = state
            recipe['safety_reason'] = verdict.get('safety_reason', '')
            recipe['_safety_verdict'] = verdict

            if cand.api_prefiltered:
                prefiltered_total += 1
                # Which of the things we asked the API to exclude did we
                # nonetheless find in what it returned?
                for entry in verdict.get('per_restriction', []):
                    if entry.get('state') != UNSAFE:
                        continue
                    declaration = str(entry.get('restriction', '')).lower()
                    if declaration not in cand.prefiltered_for:
                        continue
                    for hit in entry.get('matched_ingredients', []):
                        leaks.append({
                            'recipe_id': cand.recipe_id,
                            'title': recipe.get('title', 'Unknown'),
                            'declaration': entry.get('restriction'),
                            'ingredient': hit.get('raw_text'),
                            'canonical_id': hit.get('canonical_id'),
                            'categories': hit.get('categories'),
                            'found_in': hit.get('source'),
                        })
                if state == UNSAFE:
                    prefiltered_rejected += 1

            if state != UNSAFE:
                screened.append(recipe)

        # Structural guarantee, not a convention.
        if screened_count != len(candidates):
            raise AssertionError(
                f"screening coverage breach: {screened_count} of {len(candidates)} "
                f"candidates screened. Every recipe must be screened regardless of "
                f"which endpoint returned it."
            )

        leak_rate = (prefiltered_rejected / prefiltered_total) if prefiltered_total else 0.0

        report = {
            'table_version': TABLE_VERSION,
            'candidates_screened': screened_count,
            'screening_coverage': 1.0 if candidates else 1.0,
            'verdicts': {'SAFE': counts.get(SAFE, 0),
                         'UNSAFE': counts.get(UNSAFE, 0),
                         'UNKNOWN': counts.get(UNKNOWN, 0)},
            'api_prefiltered_candidates': prefiltered_total,
            'api_prefiltered_rejected_by_our_filter': prefiltered_rejected,
            'api_prefilter_leak_rate': round(leak_rate, 4),
            'leaks': leaks,
        }
        return screened, report

    # -----------------------------------------------------------------
    # Public entry point
    # -----------------------------------------------------------------
    def retrieve(
        self,
        pantry: Sequence[str],
        settings: Dict[str, Any],
        number: int = 20,
        cuisine: Optional[str] = None,
        meal_type: Optional[str] = None,
        diet: Optional[str] = None,
        exclude_ingredients: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        intolerances = settings.get('intolerances') or []
        diets = settings.get('dietary_requirements') or []
        effective_diet = diet or (diets[0] if diets else None)

        pantry_hits, pantry_error = self._arm_pantry(pantry, number)
        filtered_hits, asked_to_exclude, filtered_error = self._arm_filtered(
            pantry, number, cuisine, meal_type, effective_diet,
            intolerances, exclude_ingredients or [],
        )

        candidates, conflicts = self._merge(pantry_hits, filtered_hits, asked_to_exclude)
        bulk_calls = self._enrich(candidates)
        recipes, screening = self._screen_all(candidates, settings)

        both = sum(1 for c in candidates if len(c.sources) == 2)

        # Requirement 5, stated in the payload rather than left to inference.
        #
        # An arm returning nothing is not the same as "nothing matched". If
        # complexSearch filtered everything out but findByIngredients found
        # plenty, the honest report is "one arm was too restrictive", and the
        # results from the other arm still stand.
        notes: List[str] = []
        if not filtered_hits and pantry_hits:
            notes.append(
                'complexSearch returned no results while findByIngredients returned '
                f'{len(pantry_hits)}. The filtered arm was too restrictive; these '
                'results come from the pantry arm and were screened locally. This is '
                'not "no recipes matched".'
            )
        if not pantry_hits and filtered_hits:
            notes.append(
                'findByIngredients returned nothing while complexSearch returned '
                f'{len(filtered_hits)}. Results are dietary matches with unknown '
                'pantry coverage.'
            )
        if pantry_error:
            notes.append(f'findByIngredients arm errored: {pantry_error}')
        if filtered_error:
            notes.append(f'complexSearch arm errored: {filtered_error}')
        if conflicts:
            notes.append(f'{len(conflicts)} field conflict(s) between arms; '
                         'informationBulk values took precedence.')

        # Requirement 4: this line is the measurement. It goes to the log as well
        # as the payload so it survives even when nobody reads the response.
        logger.info(
            "retrieval: pantry_arm=%d filtered_arm=%d merged=%d both=%d "
            "bulk_calls=%d screened=%d safe=%d unknown=%d unsafe=%d "
            "api_prefiltered=%d prefilter_leaks=%d leak_rate=%.2f%% table=%s",
            len(pantry_hits), len(filtered_hits), len(candidates), both,
            bulk_calls, screening['candidates_screened'],
            screening['verdicts']['SAFE'], screening['verdicts']['UNKNOWN'],
            screening['verdicts']['UNSAFE'],
            screening['api_prefiltered_candidates'],
            screening['api_prefiltered_rejected_by_our_filter'],
            screening['api_prefilter_leak_rate'] * 100, TABLE_VERSION,
        )
        for leak in screening['leaks']:
            logger.warning(
                "API PREFILTER LEAK: complexSearch was asked to exclude %r but "
                "returned recipe %s (%r); our screen matched %r -> %s (found in %s)",
                leak['declaration'], leak['recipe_id'], leak['title'],
                leak['ingredient'], leak['canonical_id'], leak['found_in'],
            )

        return {
            'recipes': recipes,
            'metadata': {
                'retrieval': {
                    'pantry_arm_results': len(pantry_hits),
                    'filtered_arm_results': len(filtered_hits),
                    'merged_candidates': len(candidates),
                    'found_by_both_arms': both,
                    'found_by_pantry_arm_only':
                        sum(1 for c in candidates if c.sources == {ARM_PANTRY}),
                    'found_by_filtered_arm_only':
                        sum(1 for c in candidates if c.sources == {ARM_FILTERED}),
                    'information_bulk_calls': bulk_calls,
                    'enriched': sum(1 for c in candidates if c.detail is not None),
                    'field_conflicts': conflicts,
                    'api_filters_sent': sorted(asked_to_exclude),
                    'notes': notes,
                },
                'screening': screening,
            },
        }
