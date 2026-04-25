def danger_button_style(dark: bool) -> str:
    if dark:
        return """
        QPushButton {
            background-color: transparent;
            color: white;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #ff5c5c;
            border: 1px solid rgba(255,255,255,0.25);
        }

        QPushButton:pressed {
            background-color: #b52b2b;
        }
        """
    else:
        return """
        QPushButton {
            background-color: transparent;
            color: #222;
            border: 1px solid rgba(0,0,0,0.15);
            border-radius: 12px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #ff5c5c;
            color: white;
        }

        QPushButton:pressed {
            background-color: #b52b2b;
            color: white;
        }
        """


def primary_button_style(dark: bool):
    if dark:
        return """
        QPushButton {
            color: white;
            background-color: rgba(76, 175, 80, 0.15);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 12px;
            padding: 6px 10px;
        }

        QPushButton:hover {
            background-color: rgba(76, 175, 80, 0.35);
        }

        QPushButton:pressed {
            background-color: rgba(40, 120, 45, 0.6);
        }
        """
    else:
        return """
        QPushButton {
            color: #222;
            background-color: rgba(76, 175, 80, 0.10);
            border: 1px solid rgba(46, 125, 50, 0.3);
            border-radius: 12px;
            padding: 6px 10px;
        }

        QPushButton:hover {
            background-color: rgba(76, 175, 80, 0.25);
        }

        QPushButton:pressed {
            background-color: rgba(46, 125, 50, 0.5);
            color: white;
        }
        """