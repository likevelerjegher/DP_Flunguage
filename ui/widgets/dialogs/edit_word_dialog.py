from ui.widgets.dialogs.create_word_dialog import CreateWordDialog


class EditWordDialog(CreateWordDialog):
    def __init__(self, word):
        super().__init__()

        self.setWindowTitle("Редактировать слово")

        self.original.setText(word["original"])
        self.translation.setText(word["translation"])
        self.transcription.setText(word["transcription"] or "")

        self.language.setCurrentText(word["language"])
        self.difficulty.setCurrentIndex(word["difficulty"] - 1)