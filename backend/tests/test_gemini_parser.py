from app.ai.gemini_parser import GeminiIntentParser
from app.schemas.intent import IntentType


def test_intent_parsing_heuristics():
    parser = GeminiIntentParser()

    # Register worker
    p1 = parser.parse("Add maid Sunita Salary 9000 Sunday off")
    assert p1.intent == IntentType.REGISTER_WORKER
    assert p1.worker_name == "Sunita"
    assert p1.monthly_salary == 9000.0
    assert p1.weekly_off == "Sunday"

    # Remove worker
    p2 = parser.parse("Remove Sunita")
    assert p2.intent == IntentType.REMOVE_WORKER
    assert p2.worker_name == "Sunita"

    # Update worker salary
    p3 = parser.parse("Sunita salary is now 9500")
    assert p3.intent == IntentType.UPDATE_WORKER
    assert p3.worker_name == "Sunita"
    assert p3.monthly_salary == 9500.0

    # Absent
    p4 = parser.parse("Sunita absent today")
    assert p4.intent == IntentType.ABSENT
    assert p4.worker_name == "Sunita"

    # Half Day
    p5 = parser.parse("Sunita half day")
    assert p5.intent == IntentType.HALF_DAY
    assert p5.worker_name == "Sunita"

    # Advance
    p6 = parser.parse("Sunita took 500 advance")
    assert p6.intent == IntentType.ADVANCE
    assert p6.worker_name == "Sunita"
    assert p6.amount == 500.0

    # Bonus
    p7 = parser.parse("Bonus 1000 for Sunita")
    assert p7.intent == IntentType.BONUS
    assert p7.worker_name == "Sunita"
    assert p7.amount == 1000.0

    # Generate Payment
    p8 = parser.parse("Generate payment for Sunita")
    assert p8.intent == IntentType.GENERATE_PAYMENT
    assert p8.worker_name == "Sunita"

    # Help
    p9 = parser.parse("Hi")
    assert p9.intent == IntentType.HELP
