"""AI analysis module for AURIX Reconciliation."""

LANGCHAIN_AVAILABLE = False
SKLEARN_AVAILABLE = False

try:
    from langchain_groq import ChatGroq  # noqa: F401
    LANGCHAIN_AVAILABLE = True
except ImportError:
    pass

try:
    from sklearn.ensemble import IsolationForest  # noqa: F401
    SKLEARN_AVAILABLE = True
except ImportError:
    pass
