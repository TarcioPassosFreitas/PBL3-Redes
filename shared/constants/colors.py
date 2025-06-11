class Colors:
    """
    Constantes de cores ANSI para saída no terminal.
    """
    # Cores regulares
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    GREY = "\033[0;37m"
    WHITE = "\033[0;38m"

    # Cores em negrito
    BOLD_BLACK = "\033[1;30m"
    BOLD_RED = "\033[1;31m"
    BOLD_GREEN = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE = "\033[1;34m"
    BOLD_MAGENTA = "\033[1;35m"
    BOLD_CYAN = "\033[1;36m"
    BOLD_GREY = "\033[1;37m"
    BOLD_WHITE = "\033[1;38m"

    # Cores de fundo
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_GREY = "\033[47m"
    BG_WHITE = "\033[48m"

    # Reset
    RESET = "\033[0m"

    # Cores da UI (para uso futuro)
    PRIMARY = BLUE
    SECONDARY = GREY
    SUCCESS = GREEN
    WARNING = YELLOW
    ERROR = RED
    INFO = CYAN

    # Cores de log
    LOG_DEBUG = GREY
    LOG_INFO = GREEN
    LOG_WARNING = YELLOW
    LOG_ERROR = RED
    LOG_CRITICAL = BOLD_RED

    @classmethod
    def disable(cls):
        """
        Desativa todas as cores definindo-as como strings vazias.
        """
        # Cores regulares
        cls.BLACK = ""
        cls.RED = ""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.BLUE = ""
        cls.MAGENTA = ""
        cls.CYAN = ""
        cls.GREY = ""
        cls.WHITE = ""

        # Cores em negrito
        cls.BOLD_BLACK = ""
        cls.BOLD_RED = ""
        cls.BOLD_GREEN = ""
        cls.BOLD_YELLOW = ""
        cls.BOLD_BLUE = ""
        cls.BOLD_MAGENTA = ""
        cls.BOLD_CYAN = ""
        cls.BOLD_GREY = ""
        cls.BOLD_WHITE = ""

        # Cores de fundo
        cls.BG_BLACK = ""
        cls.BG_RED = ""
        cls.BG_GREEN = ""
        cls.BG_YELLOW = ""
        cls.BG_BLUE = ""
        cls.BG_MAGENTA = ""
        cls.BG_CYAN = ""
        cls.BG_GREY = ""
        cls.BG_WHITE = ""

        # Reset
        cls.RESET = ""

        # Cores da UI
        cls.PRIMARY = ""
        cls.SECONDARY = ""
        cls.SUCCESS = ""
        cls.WARNING = ""
        cls.ERROR = ""
        cls.INFO = ""

        # Cores de log
        cls.LOG_DEBUG = ""
        cls.LOG_INFO = ""
        cls.LOG_WARNING = ""
        cls.LOG_ERROR = ""
        cls.LOG_CRITICAL = ""

    @classmethod
    def enable(cls):
        """
        Reativa todas as cores restaurando seus códigos ANSI.
        """
        # Cores regulares
        cls.BLACK = "\033[0;30m"
        cls.RED = "\033[0;31m"
        cls.GREEN = "\033[0;32m"
        cls.YELLOW = "\033[0;33m"
        cls.BLUE = "\033[0;34m"
        cls.MAGENTA = "\033[0;35m"
        cls.CYAN = "\033[0;36m"
        cls.GREY = "\033[0;37m"
        cls.WHITE = "\033[0;38m"

        # Cores em negrito
        cls.BOLD_BLACK = "\033[1;30m"
        cls.BOLD_RED = "\033[1;31m"
        cls.BOLD_GREEN = "\033[1;32m"
        cls.BOLD_YELLOW = "\033[1;33m"
        cls.BOLD_BLUE = "\033[1;34m"
        cls.BOLD_MAGENTA = "\033[1;35m"
        cls.BOLD_CYAN = "\033[1;36m"
        cls.BOLD_GREY = "\033[1;37m"
        cls.BOLD_WHITE = "\033[1;38m"

        # Cores de fundo
        cls.BG_BLACK = "\033[40m"
        cls.BG_RED = "\033[41m"
        cls.BG_GREEN = "\033[42m"
        cls.BG_YELLOW = "\033[43m"
        cls.BG_BLUE = "\033[44m"
        cls.BG_MAGENTA = "\033[45m"
        cls.BG_CYAN = "\033[46m"
        cls.BG_GREY = "\033[47m"
        cls.BG_WHITE = "\033[48m"

        # Reset
        cls.RESET = "\033[0m"

        # Cores da UI
        cls.PRIMARY = cls.BLUE
        cls.SECONDARY = cls.GREY
        cls.SUCCESS = cls.GREEN
        cls.WARNING = cls.YELLOW
        cls.ERROR = cls.RED
        cls.INFO = cls.CYAN

        # Cores de log
        cls.LOG_DEBUG = cls.GREY
        cls.LOG_INFO = cls.GREEN
        cls.LOG_WARNING = cls.YELLOW
        cls.LOG_ERROR = cls.RED
        cls.LOG_CRITICAL = cls.BOLD_RED 