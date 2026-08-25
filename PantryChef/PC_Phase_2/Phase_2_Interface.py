from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Phase1Recipe:
    id: int
    title: str
    #backend only
    smart_score: float

    used_count: int
    missed_count: int
    difficulty: str
    time_estimate: int
    cuisine: str

@dataclass
class UserIntent:
    priority: str
    max_time: int
    max_difficulty: str

    mood: Optional[str] = None
    skill_level: int = 50

@dataclass
class Phase2Recommendation:
    recipe: Phase1Recipe
    match_confidence: float


