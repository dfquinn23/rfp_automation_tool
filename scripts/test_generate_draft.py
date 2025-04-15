from generate_drafts import generate_draft_answer

question = "What is your investment philosophy?"
top_answers = [
    "We believe in long-term fundamental investing with a disciplined risk management process.",
    "Our approach combines macroeconomic analysis with bottom-up stock selection.",
    "We aim to deliver consistent performance through diversified exposure to high-conviction ideas."
]

draft = generate_draft_answer(question, top_answers)
print("\n📝 Draft Answer:\n", draft)
