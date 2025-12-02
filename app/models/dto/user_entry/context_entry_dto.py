class ContextEntryDto:
    course: str | None # Do we know in which course the flashcards will be used
    topic_path: str | None # Do we know in which topic the flashcards will be used
    fc_to_modify: str | None # Do we know if we have to modify existing flashcard
    def __init__(self, context_text: str):
        self.context_text = context_text