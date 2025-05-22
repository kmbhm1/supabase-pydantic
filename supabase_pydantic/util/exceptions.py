class ConnectionError(Exception):
    """Raised when a connection to the Supabase API cannot be established."""

    pass


class RuffNotFoundError(Exception):
    """Custom exception raised when the ruff executable is not found."""

    def __init__(self, file_path: str, message: str = 'Ruff executable not found. Formatting skipped.'):
        self.file_path = file_path
        self.message = f'{message} For file: {file_path}'
        super().__init__(self.message)
