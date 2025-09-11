from datetime import datetime, timezone
import sys
import logging

logger = logging.getLogger("TwitchDrops")


def Calculate_Balanced_Priority(campaign, user_priority: int, priority_list_length: int) -> float:
    """
    Calculate weighted priority score: Balanced blend of user priority and time urgency.

    This algorithm sits in the middle of the spectrum between pure priority and pure time.
    It always considers both factors, making it more time-sensitive than Smart but more
    priority-respectful than Ending Soonest.

    Algorithm: 60% user priority + 40% time urgency

    Args:
        campaign: The campaign to calculate priority for
        user_priority: User-defined priority value (lower = more important)
        priority_list_length: Total length of the user's priority list

    Returns:
        Weighted priority score (higher = more important)
    """
    current_time = datetime.now(timezone.utc)
    time_remaining_hours = (campaign.ends_at - current_time).total_seconds() / 3600

    if time_remaining_hours <= 0:
        print(f"      BALANCED: Campaign expired, returning -sys.maxsize")
        return -sys.maxsize  # Expired campaigns get lowest priority

    # Calculate time urgency score (0-100 scale)
    # Use a reasonable time window - campaigns ending within 72 hours are considered urgent
    max_urgency_window = 72  # hours
    time_urgency_score = max(0, 100 * (1 - (time_remaining_hours / max_urgency_window)))
    time_urgency_score = min(100, time_urgency_score)  # Cap at 100

    # Priority component (0-100 scale)
    # Invert user priority so lower numbers = higher priority scores
    inverted_priority = priority_list_length - user_priority + 1
    priority_score = (inverted_priority / priority_list_length) * 100

    # Weighted blend: 60% priority + 40% time urgency
    priority_weight = 0.60
    time_weight = 0.40

    blended_score = (priority_weight * priority_score) + (time_weight * time_urgency_score)

    # Scale final score to maintain reasonable range relative to user priorities
    final_score = (blended_score / 100) * inverted_priority + (blended_score * 0.1)

    return final_score

def Calculate_Adaptive_Priority(campaign, user_priority: int, priority_list_length: int) -> int:
    """
    Calculate smart priority score that ensures higher priority games complete before lower ones.

    Args:
        campaign: The campaign to calculate priority for
        user_priority: User-defined priority value (lower = more important)
        priority_list_length: Total length of the user's priority list

    Returns:
        Smart priority score (higher = more important)
    """
    current_time = datetime.now(timezone.utc)
    time_remaining_hours = (campaign.ends_at - current_time).total_seconds() / 3600

    if time_remaining_hours <= 0:
        print(f"      ADAPTIVE: Campaign expired, returning -sys.maxsize")
        return -sys.maxsize  # Expired campaigns get lowest priority

    # Calculate time pressure
    minutes_needed = campaign.remaining_minutes
    hours_needed = minutes_needed / 60

    # Calculate completion risk (0-1, where 1 = very risky)
    # Risk factor: how tight is the time window?
    buffer_factor = 1.2  # 20% buffer
    time_risk = max(0, 1 - (time_remaining_hours / (hours_needed * buffer_factor))) if hours_needed > 0 else 0

    # Invert user priority so lower numbers = higher priority scores
    inverted_priority = priority_list_length - user_priority + 1

    # Calculate priority boost for high-priority games at risk
    # Higher priority games (lower user_priority) get bigger boost when at risk
    priority_boost = inverted_priority * time_risk * 10  # Scale factor
    final_score = inverted_priority + priority_boost

    return final_score