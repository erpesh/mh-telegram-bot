def shorten_string(input_string):
    max_length = 50
    if len(input_string) > max_length:
        shortened = input_string[:max_length-3] + '...'
        return shortened
    else:
        return input_string


def get_available_chats(active_chats: dict) -> list[int]:
    return [key for key, value in active_chats.items() if value is None]
