# ui/widgets/training_widget.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QComboBox, QMessageBox, QHBoxLayout, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt

from ui.widgets.training.training_sesstion_dialog import TrainingSessionDialog
import qtawesome as qta

class TrainingWidget(QWidget):
    def __init__(self, training_service):
        super().__init__()

        self.training_service = training_service
        self.current_task = None

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ======= START PANEL =======
        self.start_panel = QVBoxLayout()

        self.mode_box = QComboBox()
        self.mode_box.addItems(["mixed", "input", "choice"])

        self.source_box = QComboBox()

        self.source_box.addItem("Все слова", {"type": "all", "id": None})

        self.source_box.currentIndexChanged.connect(self.update_limit)

        for d in self.training_service.dict_service.get_all_dictionaries():
            self.source_box.addItem(
                d["name"],
                {"type": "dictionary", "id": d["id"]}
            )

        self.limit_box = QSpinBox()
        self.limit_box.setRange(1, 100)
        self.limit_box.setValue(10)

        mode_header = QHBoxLayout()

        mode_label = QLabel("Режим")

        self.info_btn = QPushButton()
        self.info_btn.setFlat(True)
        self.info_btn.setFixedSize(20, 20)
        self.info_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.info_btn.setToolTip(
            "Режимы тренировки:\n\n"
            "mixed — смешанный режим (input + choice)\n"
            "input — ввод ответа вручную\n"
            "choice — выбор из вариантов"
        )

        mode_header.addWidget(mode_label)
        mode_header.addWidget(self.info_btn)
        mode_header.addStretch()

        self.start_panel.addLayout(mode_header)
        self.start_panel.addWidget(self.mode_box)

        self.start_panel.addWidget(QLabel("Источник"))
        self.start_panel.addWidget(self.source_box)

        self.start_panel.addWidget(QLabel("Количество слов"))
        self.start_panel.addWidget(self.limit_box)

        self.layout.addLayout(self.start_panel)

        # ===== режим статистики =====
        stats_label = QLabel("Записать даннные в статистику?")

        self.stats_group = QButtonGroup(self)

        self.stats_yes = QRadioButton("Да")
        self.stats_no = QRadioButton("Нет")
        self.stats_yes.setStyleSheet("background: transparent;")
        self.stats_no.setStyleSheet("background: transparent;")

        self.stats_yes.setChecked(True)

        self.stats_group.addButton(self.stats_yes)
        self.stats_group.addButton(self.stats_no)

        self.start_panel.addWidget(stats_label)
        self.start_panel.addWidget(self.stats_yes)
        self.start_panel.addWidget(self.stats_no)

        # вопрос
        self.label_question = QLabel("")

        # ввод
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите ответ")

        # результат
        self.label_result = QLabel("")
        self.label_result.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # кнопки
        self.btn_check = QPushButton("Проверить")
        self.btn_next = QPushButton("Следующее")
        self.btn_start = QPushButton("Начать тренировку")
        # варианты (для choice)
        self.options_layout = QVBoxLayout()

        # layout

        self.layout.addWidget(self.label_question)

        self.layout.addWidget(self.input)
        self.layout.addLayout(self.options_layout)
        self.layout.addWidget(self.label_result)
        self.layout.addWidget(self.btn_check)
        self.layout.addWidget(self.btn_next)

        # В САМОМ НИЗУ
        self.layout.addStretch()
        self.layout.addWidget(self.btn_start)

        # events
        self.btn_check.clicked.connect(self.check_answer)
        self.btn_next.clicked.connect(self.load_task)
        self.btn_start.clicked.connect(self.start_training)

        # начальное состояние
        self.input.hide()
        self.btn_check.hide()
        self.btn_next.hide()

        self.update_limit()

    def load_task(self):
        self.clear_options()

        self.current_task = self.training_service.get_next_task()

        if not self.current_task:
            self.label_question.setText("Нет слов для повторения")
            return

        self.label_result.setText("")
        self.input.clear()

        if self.current_task["mode"] == "input":
            self.input.show()
            self.label_question.setText(self.current_task["question"])

        else:
            self.input.hide()
            self.label_question.setText(self.current_task["question"])

            for option in self.current_task["options"]:
                btn = QPushButton(option)
                btn.clicked.connect(lambda _, o=option: self.select_option(o))
                self.options_layout.addWidget(btn)

    def select_option(self, option):
        self.process_answer(option)

    def check_answer(self):
        if not self.current_task:
            return

        answer = self.input.text()
        self.process_answer(answer)

    def process_answer(self, user_answer):
        is_correct = self.training_service.check_answer(self.current_task, user_answer)

        if is_correct:
            self.label_result.setText("✅ Правильно")
        else:
            self.label_result.setText(
                f"❌ Неправильно\nОтвет: {self.current_task['answer']}"
            )

        self.training_service.update_progress(
            self.current_task["word"],
            is_correct
        )

    def clear_options(self):
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def start_training(self):
        mode = self.mode_box.currentText()
        use_stats = self.stats_yes.isChecked()
        data = self.source_box.currentData()
        source_type = data["type"]
        source_id = data["id"]

        words = self.get_words(source_type, source_id)
        count = len(words)

        # логика ошибки
        if count < 2:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Недостаточно слов!\n\n"
                "Для начала тренировки необходимо минимум 2 слова.\n"
            )
            return

        limit = self.limit_box.value()

        # защита лимита
        if limit < 2:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Недостаточно слов!\n\n"
                "Для начала тренировки необходимо минимум 2 слова.\n"
            )
            return

        # защита от переполнения
        if limit > count:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Максимум доступно слов: {count}"
            )
            return

        self.training_service.start_session(
            mode,
            source_type,
            source_id,
            limit,
            use_stats
        )

        dialog = TrainingSessionDialog(self.training_service)
        dialog.exec()

    def update_limit(self):
        data = self.source_box.currentData()
        if not data:
            return

        source_type = data["type"]
        source_id = data["id"]

        words = self.get_words(source_type, source_id)
        count = len(words)

        if count < 2:
            self.limit_box.setMaximum(1)
            return

        self.limit_box.setMaximum(count)

        if self.limit_box.value() > count:
            self.limit_box.setValue(count)

    def get_words(self, source_type, source_id):
        if source_type == "all":
            return self.training_service.word_service.get_all_words()
        else:
            return self.training_service.dict_service.get_words(source_id)

    def update_info_icon(self, color: str):
        self.info_btn.setIcon(qta.icon('fa5s.info-circle', color=color))

    def reload_dictionaries(self):
        self.source_box.blockSignals(True)

        current = self.source_box.currentData()

        self.source_box.clear()
        self.source_box.addItem("Все слова", {"type": "all", "id": None})

        for d in self.training_service.dict_service.get_all_dictionaries():
            self.source_box.addItem(
                d["name"],
                {"type": "dictionary", "id": d["id"]}
            )

        # восстановить выбор (если возможно)
        if current:
            for i in range(self.source_box.count()):
                if self.source_box.itemData(i) == current:
                    self.source_box.setCurrentIndex(i)
                    break

        self.source_box.blockSignals(False)
        self.update_limit()