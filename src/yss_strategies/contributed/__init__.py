"""
Community Contributed Strategies

This module contains strategies contributed by the YSS community.
Each strategy is implemented as a separate class following the
YSS strategy interface.
"""

import importlib
import pkgutil
from pathlib import Path

# Import all strategy modules dynamically
__path__ = [str(Path(__file__).parent)]

# Auto-discover and import all strategy modules
for importer, modname, ispkg in pkgutil.iter_modules(__path__):
    if not modname.startswith('_'):  # Skip private modules
        try:
            module = importlib.import_module(f'.{modname}', __name__)
            # Add strategy classes to namespace
            for attr_name in dir(module):
                if attr_name.endswith('Strategy') and not attr_name.startswith('_'):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, 'place_bet') and hasattr(attr, 'get_defaults'):
                        globals()[attr_name] = attr
                        if '__all__' not in globals():
                            globals()['__all__'] = []
                        globals()['__all__'].append(attr_name)
        except ImportError as e:
            print(f"Warning: Could not import strategy module {modname}: {e}")

# Ensure __all__ exists even if no strategies are found
if '__all__' not in globals():
    __all__ = []
