import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.simulation import Keyword, Simulation, SimulationKeyword
from app.repositories.simulation_repository import extract_keywords

def build_insights(db: Session, simulation: Simulation):
    links = db.scalars(select(SimulationKeyword).where(SimulationKeyword.simulation_id == simulation.id)).all()
    if not links:
        for value in extract_keywords(simulation.product_name, simulation.product_description, simulation.target_audience, simulation.ad_copy):
            keyword = db.scalar(select(Keyword).where(Keyword.value == value))
            if not keyword:
                keyword = Keyword(value=value); db.add(keyword); db.flush()
            db.add(SimulationKeyword(simulation_id=simulation.id, keyword_id=keyword.id))
        db.commit()
        links = db.scalars(select(SimulationKeyword).where(SimulationKeyword.simulation_id == simulation.id)).all()
    keywords = [db.get(Keyword, link.keyword_id) for link in links]
    rows = []
    for keyword in keywords:
        positive = negative = neutral = 0
        scores = []
        persona_matches = []
        report_text = json.dumps(simulation.summary_report.data if simulation.summary_report else {}, ensure_ascii=False).lower()
        discussion_text = json.dumps(simulation.discussion.data if simulation.discussion else {}, ensure_ascii=False).lower()
        terms = [keyword.value, *(keyword.synonyms or [])]
        for persona in simulation.personas:
            response = persona.response.data if persona.response else {}
            text = json.dumps({"profile": persona.profile, "response": response}, ensure_ascii=False).lower()
            if not any(term.lower() in text for term in terms):
                continue
            persona_matches.append(persona.name)
            scores.append(response.get("purchase_intent_score"))
            positive += sum(1 for item in response.get("positive_points", []) if any(term.lower() in str(item).lower() for term in terms))
            negative += sum(1 for item in response.get("concerns", []) if any(term.lower() in str(item).lower() for term in terms))
            if positive == 0 and negative == 0: neutral += 1
        total_mentions = positive + negative
        rows.append({"keyword": keyword.value, "category": keyword.category, "is_priority": keyword.is_priority, "positive_mentions": positive, "negative_mentions": negative, "neutral_mentions": neutral, "matched_personas": len(scores), "matched_persona_names": persona_matches, "summary_mentions": sum(term.lower() in report_text for term in terms), "discussion_mentions": sum(term.lower() in discussion_text for term in terms), "average_purchase_intent": round(sum(scores) / len(scores), 2) if scores else None, "sentiment_ratio": round((positive-negative) / total_mentions, 2) if total_mentions else 0})
    return sorted(rows, key=lambda item: (item["matched_personas"], item["positive_mentions"]), reverse=True)
