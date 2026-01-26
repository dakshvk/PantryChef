from PantryChef.PC_Phase_2.Phase_2_Interface import Phase1Recipe, UserIntent, Phase2Recommendation
from typing import List

class ReasoningEngine:
    def __init__(self):
        self.intent_weights = {
            'tired': {
                'time': 0.8,
                'effort': 0.7,
                'skill': 0.3,
                'shopping': 0.8
            },

            'casual': {
                'time': 0.5,
                'effort': 0.5,
                'skill': 0.5,
                'shopping': 0.5

            },

            'energetic': {
                'time': 0.3,
                'effort': 0.4,
                'skill': 0.7,
                'shopping': 0.4

            }
        }

    def process_recommendations(
            self,
            phase1_recipes: List[Phase1Recipe],
            user_intent: UserIntent) -> List[Phase2Recommendation]:
        recommendations = [] # holds final phase 2 recommendations
        weights = self.intent_weights.get(
            user_intent.mood,
            self.intent_weights['casual'] #if user does not specify mood default to casual
        )
        #all phase 2 does is iterate over phase 1 output

        for recipe in phase1_recipes:

            if recipe.time_estimate and user_intent.max_time:
                time_score = max(0.1,
                                  1 - (recipe.time_estimate / user_intent.max_time)
                )
            else:
                time_score = 0.5
        #measures how well the recipe fits the user's available time
        #shorter recipes score higher

            difficulty_map = {'easy': 30, 'medium': 60, 'hard': 90}
            required_skill = difficulty_map.get(recipe.difficulty, 50)

            if user_intent.skill_level >= required_skill:
                skill_score = 1.0
            else:
                skill_score = max(
                    0.2,
                    1-(required_skill - user_intent.skill_level)/100
                )    # ensures we don't push difficult recipes to user with a low - casual diff, ranking
            if (recipe.used_count + recipe.missed_count) > 0:
                shopping_score = 1 - (
                    recipe.missed_count / (recipe.used_count + recipe.missed_count)
            )
            else:
                shopping_score = 0.5
            # rewards recipes that use what the user already had

            final_internal_score = (
                (recipe.smart_score/ 100) * 0.4 +
                time_score * weights['time'] * 0.25  +
                skill_score * weights['skill'] * 0.2 +
                shopping_score * weights['shopping'] *0.15
            )
            # Backend recommendation use
# people-friendly reasoning
            reasons = []

            if recipe.missed_count <= 1:
                reasons.append('requires very little shopping')
            elif recipe.missed_count <= 3:
                reasons.append('only needs a few extra ingredients')

            if recipe.time_estimate and recipe.time_estimate <= user_intent.max_time * 0.7:
                reasons.append('quick to prepare')
            if recipe.difficulty == 'easy':
                reasons.append('easy to cook up')

            if reasons:
                reasoning_text = 'Good match because it' + ','.join(reasons)
            else:
                reasoning_text = 'Matches your preferences pretty well'
                # computer logic -> positive people language

                # Confidence reflects how sure system is
                # NOT RELATED TO CORRECTNESS
                #confidence estimation (starts from neutral confidence baseline)
            confidence = 70
            if recipe.missed_count <= 1:
                confidence += 10
            if recipe.difficulty == 'easy':
                confidence += 5
            if recipe.time_estimate and recipe.time_estimate <= user_intent.max_time:
                confidence += 5

            confidence = min(confidence, 95)

            _internal_debug = {
                    "internal_score": round(final_internal_score * 100, 1),
                    "time_score": round(time_score, 2),
                    "skill_score": round(skill_score, 2),
                    "shopping_score": round(shopping_score, 2),
                    "weights_used": weights,
                    "reasoning": reasoning_text
                }

                # FINAL RECOMMENDATION
            recommendations.append(
                    Phase2Recommendation(
                        recipe=recipe,
                        match_confidence=confidence,
                ))

        recommendations.sort(key=lambda r: r.match_confidence, reverse=True)
        return recommendations


