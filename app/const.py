from datetime import timezone
from pathlib import Path
from typing import Final

TIMEZONE: Final[timezone] = timezone.utc
ROOT_DIR: Final[Path] = Path(__file__).parent.parent
ENV_FILE: Final[Path] = ROOT_DIR / ".env"

# Time constants
TIME_1M: Final[int] = 60
