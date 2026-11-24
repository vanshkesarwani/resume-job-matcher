from fastapi import APIRouter, HTTPException, Response, status
from app.schemas.dashboard import PDFReportRequest
from app.services.pdf_report_service import generate_pdf_report

router = APIRouter()

@router.post(
    "/pdf",
    status_code=status.HTTP_200_OK,
    summary="Generate professional downloadable PDF report with ReportLab",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Downloadable PDF report binary stream",
        }
    },
)
def download_pdf_report_endpoint(request: PDFReportRequest):
    """
    Step 13: Download PDF Report
    - Overall match score and score breakdown
    - Matched and missing skills matrix
    - Experience, education, and ATS scores
    - AI suggestions and improvements (summary, projects, bullet rewrites, weak sections)
    """
    try:
        data = request.model_dump()
        pdf_bytes = generate_pdf_report(data)

        filename = f"Resume_Match_Report_{data.get('job_title', 'Role').replace(' ', '_')}.pdf"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "application/pdf",
        }

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers=headers,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating the PDF report: {str(e)}",
        )

