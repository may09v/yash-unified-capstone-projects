def needs_refinement_status(state):
 
    # If already refined once → DO NOT refine again
    if state["refinement_count"] >= 1:
        return False
 
    v = state["verifier_output_data"]
    failed = (v["avg_confidence"] < 0.7) or (len(v["missing_topics"]) > 0)
 
    if failed:
        state["refinement_count"] += 1
        return True
 
    return False