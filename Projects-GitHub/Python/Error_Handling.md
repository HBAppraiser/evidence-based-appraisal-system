# ERROR HANDLING AND LOGGING FRAMEWORK

## Logging Configuration

```python
import logging
from datetime import datetime
import os
from typing import Optional, Dict, Any

class AnalysisLogger:
    """Logging framework for market analysis"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.log_file = os.path.join(
            output_dir, 
            f"analysis_log_{datetime.now():%Y%m%d_%H%M%S}.log"
        )
        
        # Configure logging
        self.logger = logging.getLogger('market_analysis')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_analysis_start(self, params: Dict[str, Any]):
        """Log analysis start with parameters"""
        self.logger.info("Starting Market Analysis")
        self.logger.info(f"Parameters: {params}")
    
    def log_data_validation(self, results: Dict[str, Any]):
        """Log data validation results"""
        if results['errors']:
            for error in results['errors']:
                self.logger.error(f"Validation Error: {error}")
        
        if results['warnings']:
            for warning in results['warnings']:
                self.logger.warning(f"Validation Warning: {warning}")
    
    def log_period_analysis(self, period: str, stats: Dict[str, Any]):
        """Log period analysis results"""
        self.logger.info(f"Completed analysis for {period}")
        self.logger.debug(f"Statistics: {stats}")
    
    def log_error(self, error: Exception, context: str = ""):
        """Log exception with context"""
        self.logger.error(f"Error in {context}: {str(error)}", 
                         exc_info=True)

class AnalysisError(Exception):
    """Base class for analysis exceptions"""
    pass

class DataValidationError(AnalysisError):
    """Raised when data validation fails"""
    pass

class InsufficientDataError(AnalysisError):
    """Raised when insufficient data for analysis"""
    pass

class GeographicAnalysisError(AnalysisError):
    """Raised when geographic analysis fails"""
    pass

def error_handler(func):
    """Decorator for error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger('market_analysis')
            logger.error(f"Error in {func.__name__}: {str(e)}", 
                        exc_info=True)
            raise
    return wrapper
```

## Usage Example

```python
# Initialize logging
logger = AnalysisLogger(output_dir="./outputs")

@error_handler
def run_analysis(params):
    logger.log_analysis_start(params)
    
    try:
        # Data preprocessing
        preprocessor = DataPreprocessor(params['date_of_value'])
        results = preprocessor.process_dataset(params['data'])
        logger.log_data_validation(results)
        
        if results['errors']:
            raise DataValidationError("Data validation failed")
        
        # Analysis continues...
        
    except Exception as e:
        logger.log_error(e, "Market Analysis")
        raise
```