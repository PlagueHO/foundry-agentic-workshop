"""Run the Module 13 solution proxy locally."""

from __future__ import annotations

from pathlib import Path

import uvicorn


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=3978, reload=True, reload_dirs=[str(Path(__file__).parent)])
