"""
Data analysis and BI tools
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from .base import Tool, ToolOutput
from ..core.logger import get_logger

logger = get_logger(__name__)


class QueryDatabaseTool(Tool):
    """Query warehouse database for analytics data"""

    def __init__(self, db_connection=None):
        super().__init__()
        self.db_connection = db_connection  # Placeholder for actual DB connection

    async def execute(
        self,
        query: str,
        params: Optional[Dict] = None
    ) -> ToolOutput:
        """
        Execute SQL query

        Args:
            query: SQL query string
            params: Optional query parameters

        Returns:
            Query results
        """
        try:
            # Simulated database query
            # In production, use actual database connection
            logger.info(f"Executing query: {query[:100]}...")

            # Mock data for demonstration
            mock_data = {
                "shuttle_id": [1704, 2921, 1503, 2105],
                "floor": [6, 6, 4, 7],
                "energy_kwh": [245, 243, 198, 195],
                "empty_run_rate": [0.42, 0.41, 0.15, 0.14],
                "utilization": [0.88, 0.87, 0.12, 0.14]
            }

            df = pd.DataFrame(mock_data)

            return ToolOutput(
                success=True,
                result={
                    "data": df.to_dict('records'),
                    "columns": list(df.columns),
                    "row_count": len(df)
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=str(e)
            )

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "SQL query to execute"
            },
            "params": {
                "type": "object",
                "description": "Optional query parameters"
            }
        }

    def _get_required_params(self) -> List[str]:
        return ["query"]


class GenerateChartTool(Tool):
    """Generate visualization charts from data"""

    async def execute(
        self,
        data: List[Dict],
        chart_type: str = "bar",
        title: str = "Chart",
        x_column: Optional[str] = None,
        y_column: Optional[str] = None
    ) -> ToolOutput:
        """
        Generate chart from data

        Args:
            data: List of data records
            chart_type: Type of chart (bar, line, pie, etc.)
            title: Chart title
            x_column: X-axis column name
            y_column: Y-axis column name

        Returns:
            Base64 encoded chart image
        """
        try:
            df = pd.DataFrame(data)

            plt.figure(figsize=(10, 6))

            if chart_type == "bar":
                plt.bar(df[x_column], df[y_column])
            elif chart_type == "line":
                plt.plot(df[x_column], df[y_column], marker='o')
            elif chart_type == "pie":
                plt.pie(df[y_column], labels=df[x_column], autopct='%1.1f%%')
            else:
                return ToolOutput(
                    success=False,
                    result=None,
                    error=f"Unsupported chart type: {chart_type}"
                )

            plt.title(title)
            if chart_type != "pie":
                plt.xlabel(x_column or "X")
                plt.ylabel(y_column or "Y")
            plt.tight_layout()

            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()

            return ToolOutput(
                success=True,
                result={
                    "chart_image": image_base64,
                    "chart_type": chart_type,
                    "title": title
                }
            )

        except Exception as e:
            logger.error(f"Chart generation failed: {str(e)}")
            return ToolOutput(
                success=False,
                result=None,
                error=str(e)
            )

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "data": {
                "type": "array",
                "description": "Data to visualize"
            },
            "chart_type": {
                "type": "string",
                "description": "Type of chart (bar, line, pie)",
                "enum": ["bar", "line", "pie"]
            },
            "title": {
                "type": "string",
                "description": "Chart title"
            },
            "x_column": {
                "type": "string",
                "description": "X-axis column name"
            },
            "y_column": {
                "type": "string",
                "description": "Y-axis column name"
            }
        }

    def _get_required_params(self) -> List[str]:
        return ["data", "chart_type"]


class CalculateMetricsTool(Tool):
    """Calculate statistical metrics and perform anomaly detection"""

    async def execute(
        self,
        data: List[Dict],
        metric_column: str,
        group_by: Optional[str] = None
    ) -> ToolOutput:
        """
        Calculate metrics and detect anomalies

        Args:
            data: Data records
            metric_column: Column to analyze
            group_by: Optional grouping column

        Returns:
            Calculated metrics and anomalies
        """
        try:
            df = pd.DataFrame(data)

            if group_by:
                grouped = df.groupby(group_by)[metric_column].agg([
                    'mean', 'median', 'std', 'min', 'max', 'count'
                ])
                stats = grouped.to_dict('index')
            else:
                stats = {
                    'mean': df[metric_column].mean(),
                    'median': df[metric_column].median(),
                    'std': df[metric_column].std(),
                    'min': df[metric_column].min(),
                    'max': df[metric_column].max(),
                    'count': len(df)
                }

            # Simple anomaly detection (values > mean + 2*std)
            mean_val = df[metric_column].mean()
            std_val = df[metric_column].std()
            threshold = mean_val + 2 * std_val

            anomalies = df[df[metric_column] > threshold].to_dict('records')

            return ToolOutput(
                success=True,
                result={
                    "statistics": stats,
                    "anomalies": anomalies,
                    "anomaly_count": len(anomalies),
                    "threshold": threshold
                }
            )

        except Exception as e:
            return ToolOutput(
                success=False,
                result=None,
                error=str(e)
            )

    def _get_parameters(self) -> Dict[str, Any]:
        return {
            "data": {
                "type": "array",
                "description": "Data records to analyze"
            },
            "metric_column": {
                "type": "string",
                "description": "Column name for metric calculation"
            },
            "group_by": {
                "type": "string",
                "description": "Optional column to group by"
            }
        }

    def _get_required_params(self) -> List[str]:
        return ["data", "metric_column"]
