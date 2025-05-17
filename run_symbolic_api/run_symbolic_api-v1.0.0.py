# run_symbolic_api.py (v1.0.0)

import uvicorn
from symbolic_api import app  # Adjust filename/module as needed

if __name__ == "__main__":
    uvicorn.run(
        "symbolic_api:app",  # module:app
        host="0.0.0.0",
        port=7070,
        reload=True,
        log_level="info",
        timeout_keep_alive=30
    )