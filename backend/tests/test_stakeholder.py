"""backend/tests/test_stakeholder.py — Unit tests for stakeholder export module."""

from unittest.mock import AsyncMock, patch
import pytest
from backend.models.brd import MergedBRD
from backend.output.stakeholder import export_all_stakeholder_pdfs


@pytest.mark.asyncio
async def test_export_all_stakeholder_pdfs():
    merged_brd = MergedBRD(session_id="12345678-1234-5678-1234-567812345678")

    with patch("backend.output.stakeholder.generate_pdf", new_callable=AsyncMock) as mock_gen_pdf, \
         patch("backend.output.stakeholder.write_pdf", new_callable=AsyncMock) as mock_write_pdf:

        mock_gen_pdf.return_value = b"%PDF-dummy"
        mock_write_pdf.side_effect = lambda sid, fname, b, view: f"gs://prism-outputs/{sid}/output_{view}.pdf"

        result = await export_all_stakeholder_pdfs(merged_brd, merged_brd.session_id)

        assert isinstance(result, dict)
        assert set(result.keys()) == {"investor", "technical", "regulatory"}
        assert "output_investor.pdf" in result["investor"]
        assert "output_technical.pdf" in result["technical"]
        assert "output_regulatory.pdf" in result["regulatory"]
        assert mock_gen_pdf.call_count == 3
        assert mock_write_pdf.call_count == 3
