"""
Unit tests for AnomalyDetector class.
Tests anomaly detection logic, model integration, and error handling.
Updated to match the real implementation structure.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

from app.agents.anomaly_detector import AnomalyDetector
from app.agents.models.detection_output import DetectionOutput, Anomaly
from app.agents.models.invoice_type_output import InvoiceType


class TestAnomalyDetector:
    """Test suite for AnomalyDetector class."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model instance."""
        mock = Mock()
        mock.invoke = Mock()
        return mock
    
    @pytest.fixture
    def detector(self, mock_model):
        """Create AnomalyDetector instance with mocked model."""
        with patch('app.agents.anomaly_detector.ChatOpenAI') as mock_chat:
            mock_chat.return_value.with_structured_output.return_value = mock_model
            return AnomalyDetector()
    
    @pytest.fixture
    def sample_invoice_data(self):
        """Sample invoice DataFrame for testing."""
        data = {
            'date': ['2024-01-06', '2024-01-15', '2024-01-16', '2024-01-21', '2024-01-27'],
            'total_amount': [1000.0, 2500.0, 90190.51, 66821.84, 70721.51],
            'invoice_type': ['Pago', 'Pago', 'Egreso', 'Ingreso', 'Traslado']
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def normal_invoice_data(self):
        """Normal invoice DataFrame without anomalies."""
        data = {
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'total_amount': [1000.0, 1200.0, 950.0, 1100.0, 1050.0],
            'invoice_type': ['Pago', 'Pago', 'Pago', 'Pago', 'Pago']
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def sample_anomaly(self):
        """Sample Anomaly object for testing."""
        return Anomaly(
            date='2024-01-16',
            total_amount=90190.51,
            invoice_type=InvoiceType.EGRESO,
            reason='Significantly higher than typical range'
        )
    
    @pytest.fixture
    def sample_detection_output(self, sample_anomaly):
        """Sample DetectionOutput for testing."""
        return DetectionOutput(anomalies=[sample_anomaly])
    
    @pytest.fixture
    def empty_detection_output(self):
        """Empty DetectionOutput for testing."""
        return DetectionOutput(anomalies=[])

    @pytest.mark.unit
    def test_initialization(self):
        """Test AnomalyDetector initialization."""
        with patch('app.agents.anomaly_detector.ChatOpenAI') as mock_chat:
            mock_model = Mock()
            mock_chat.return_value.with_structured_output.return_value = mock_model
            detector = AnomalyDetector()
            assert detector.model == mock_model
            mock_chat.assert_called_once_with(model="gpt-4.1-nano", temperature=0)
            mock_chat.return_value.with_structured_output.assert_called_once()

    @pytest.mark.unit
    def test_detect_with_anomalies(self, detector, sample_invoice_data, sample_detection_output):
        """Test anomaly detection with data containing anomalies."""
        # Mock model response indicating anomalies
        detector.model.invoke.return_value = sample_detection_output
        
        result = detector.detect(sample_invoice_data)
        
        # Verify model was called
        detector.model.invoke.assert_called_once()
        
        # Verify the result is a DetectionOutput object
        assert isinstance(result, DetectionOutput)
        assert len(result.anomalies) == 1
        assert result.anomalies[0].date == '2024-01-16'
        assert result.anomalies[0].total_amount == 90190.51
        # Note: Pydantic stores enum values as strings due to use_enum_values = True
        assert result.anomalies[0].invoice_type == 'Egreso'

    @pytest.mark.unit
    def test_detect_no_anomalies(self, detector, normal_invoice_data, empty_detection_output):
        """Test anomaly detection with normal data."""
        # Mock model response indicating no anomalies
        detector.model.invoke.return_value = empty_detection_output
        
        result = detector.detect(normal_invoice_data)
        
        # Verify model was called
        detector.model.invoke.assert_called_once()
        
        # Verify the result indicates no anomalies
        assert isinstance(result, DetectionOutput)
        assert len(result.anomalies) == 0

    @pytest.mark.unit
    def test_detect_empty_data(self, detector, empty_detection_output):
        """Test anomaly detection with empty data."""
        empty_df = pd.DataFrame(columns=['date', 'total_amount', 'invoice_type'])
        
        # Mock model response for empty data
        detector.model.invoke.return_value = empty_detection_output
        
        result = detector.detect(empty_df)
        
        # Verify model was called with empty data
        detector.model.invoke.assert_called_once()
        assert isinstance(result, DetectionOutput)
        assert len(result.anomalies) == 0

    @pytest.mark.unit
    def test_detect_single_data_point(self, detector, empty_detection_output):
        """Test anomaly detection with single data point."""
        single_df = pd.DataFrame({
            'date': ['2024-01-01'],
            'total_amount': [1000.0],
            'invoice_type': ['Pago']
        })
        
        detector.model.invoke.return_value = empty_detection_output
        
        result = detector.detect(single_df)
        
        detector.model.invoke.assert_called_once()
        assert isinstance(result, DetectionOutput)

    @pytest.mark.unit
    def test_prompt_formatting(self, detector, sample_invoice_data, empty_detection_output):
        """Test that the prompt is properly formatted."""
        detector.model.invoke.return_value = empty_detection_output
        
        detector.detect(sample_invoice_data)
        
        # Get the call arguments
        call_args = detector.model.invoke.call_args
        prompt = call_args[0][0]  # First argument should be the prompt
        
        # Verify the prompt contains the expected structure
        assert isinstance(prompt, str)
        assert "Detect anomalies" in prompt
        assert "2024-01-06" in prompt
        assert "1000" in prompt  # Markdown format shows integers without decimals
        assert "Pago" in prompt

    @pytest.mark.unit
    def test_model_error_handling(self, detector, sample_invoice_data):
        """Test handling of model errors."""
        # Mock model to raise an exception
        detector.model.invoke.side_effect = Exception("API Error")
        
        with pytest.raises(Exception) as exc_info:
            detector.detect(sample_invoice_data)
        
        assert "API Error" in str(exc_info.value)

    @pytest.mark.unit
    def test_large_dataset_handling(self, detector, empty_detection_output):
        """Test handling of large datasets."""
        # Create a large dataset
        large_data = {
            'date': [f"2024-01-{i:02d}" for i in range(1, 32)],
            'total_amount': [float(1000 + i * 10) for i in range(1, 32)],
            'invoice_type': ['Pago'] * 31
        }
        large_df = pd.DataFrame(large_data)
        
        detector.model.invoke.return_value = empty_detection_output
        
        result = detector.detect(large_df)
        
        detector.model.invoke.assert_called_once()
        assert isinstance(result, DetectionOutput)
        
        # Verify the prompt contains all data points
        call_args = detector.model.invoke.call_args
        prompt = call_args[0][0]
        assert "2024-01-01" in prompt
        assert "2024-01-31" in prompt

    @pytest.mark.unit
    def test_extreme_values_detection(self, detector):
        """Test detection of extreme values."""
        extreme_df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'],
            'total_amount': [1000.0, 1200.0, 1000000.0, 1100.0, 0.01],
            'invoice_type': ['Pago', 'Pago', 'Egreso', 'Pago', 'Pago']
        })
        
        # Create anomalies for extreme values
        anomalies = [
            Anomaly(
                date='2024-01-03',
                total_amount=1000000.0,
                invoice_type=InvoiceType.EGRESO,
                reason='Extremely high amount'
            ),
            Anomaly(
                date='2024-01-05',
                total_amount=0.01,
                invoice_type=InvoiceType.PAGO,
                reason='Extremely low amount'
            )
        ]
        detection_output = DetectionOutput(anomalies=anomalies)
        detector.model.invoke.return_value = detection_output
        
        result = detector.detect(extreme_df)
        
        assert len(result.anomalies) == 2
        assert any(a.total_amount == 1000000.0 for a in result.anomalies)
        assert any(a.total_amount == 0.01 for a in result.anomalies)

    @pytest.mark.unit
    def test_negative_values_handling(self, detector):
        """Test handling of negative values."""
        negative_df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'total_amount': [1000.0, -500.0, 1200.0],
            'invoice_type': ['Pago', 'Egreso', 'Pago']
        })
        
        anomaly = Anomaly(
            date='2024-01-02',
            total_amount=-500.0,
            invoice_type=InvoiceType.EGRESO,
            reason='Negative amount detected'
        )
        detection_output = DetectionOutput(anomalies=[anomaly])
        detector.model.invoke.return_value = detection_output
        
        result = detector.detect(negative_df)
        
        assert len(result.anomalies) == 1
        assert result.anomalies[0].total_amount == -500.0

    @pytest.mark.unit
    def test_dataframe_to_markdown_conversion(self, detector, sample_invoice_data, empty_detection_output):
        """Test that DataFrame is properly converted to markdown for the prompt."""
        detector.model.invoke.return_value = empty_detection_output
        
        detector.detect(sample_invoice_data)
        
        # Get the call arguments and verify markdown format
        call_args = detector.model.invoke.call_args
        prompt = call_args[0][0]
        
        # Should contain markdown table formatting
        assert "|" in prompt  # Markdown table separator
        assert "date" in prompt
        assert "total_amount" in prompt
        assert "invoice_type" in prompt

    @pytest.mark.unit
    def test_multiple_anomalies_detection(self, detector):
        """Test detection of multiple anomalies."""
        multi_anomaly_df = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
            'total_amount': [1000.0, 50000.0, 1200.0, 75000.0],
            'invoice_type': ['Pago', 'Egreso', 'Pago', 'Ingreso']
        })
        
        anomalies = [
            Anomaly(
                date='2024-01-02',
                total_amount=50000.0,
                invoice_type=InvoiceType.EGRESO,
                reason='Significantly higher than normal'
            ),
            Anomaly(
                date='2024-01-04',
                total_amount=75000.0,
                invoice_type=InvoiceType.INGRESO,
                reason='Unusually high income'
            )
        ]
        detection_output = DetectionOutput(anomalies=anomalies)
        detector.model.invoke.return_value = detection_output
        
        result = detector.detect(multi_anomaly_df)
        
        assert len(result.anomalies) == 2
        assert result.anomalies[0].total_amount == 50000.0
        assert result.anomalies[1].total_amount == 75000.0

    @pytest.mark.unit
    def test_model_constants(self):
        """Test that model constants are correctly defined."""
        assert AnomalyDetector.MODEL_NAME == "gpt-4.1-nano"
        assert "Detect anomalies" in AnomalyDetector.PROMPT
        assert "{data}" in AnomalyDetector.PROMPT
