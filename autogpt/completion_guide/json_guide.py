json_guide = '''{
    "thoughts": {
        "text": "'''


def insert_completion_guide_to_last_message(current_context: object) -> object:
    opening_prompt = current_context[-1]["content"]
    guide_with_prompt = f'{opening_prompt}{json_guide}'
    current_context[-1] = {"role": "system", "content": guide_with_prompt}
    return current_context


def insert_completion_guide_to_ai_response(assistant_reply):
    return f'{json_guide}{assistant_reply}'
