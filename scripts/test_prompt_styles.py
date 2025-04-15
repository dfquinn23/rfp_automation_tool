from generate_drafts import generate_draft_answer

question = "What is your investment philosophy?"
top_answers = [
    "We believe in long-term fundamental investing with a disciplined risk management process.",
    "Our approach combines macroeconomic analysis with bottom-up stock selection.",
    "We aim to deliver consistent performance through diversified exposure to high-conviction ideas."
]

draft_a = generate_draft_answer(question, top_answers, model="llama3")

prompt_b_instruction = (
    "Write a 2-3 sentence answer using clear, formal business language "
    "appropriate for an institutional due diligence process."
)
draft_b = generate_draft_answer(question, top_answers, model="llama3")

prompt_c_instruction = (
    "Use the first example answer as a foundation. Improve or expand it using insight from the others, "
    "and generate a concise, professional response."
)
draft_c = generate_draft_answer(question, top_answers, model="llama3")

print("\n🅰️ Prompt A (Baseline):\n", draft_a)
print("\n🅱️ Prompt B (Structured tone):\n", draft_b)
print("\nc Prompt C (Emphasize top match):\n", draft_c)
