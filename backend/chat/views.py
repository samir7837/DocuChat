from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document
from .utils import parse_pdf

import cloudinary.uploader


# =====================================================
# Health Check
# =====================================================
class HealthCheckView(APIView):
    def get(self, request):
        return Response(
            {
                "status": "healthy",
                "message": "DocuChat backend is running"
            },
            status=status.HTTP_200_OK
        )


# =====================================================
# Upload PDF
# =====================================================
class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ IMPORTANT FIX
        # RAW files must be PUBLIC
        upload_result = cloudinary.uploader.upload(
            file,
            resource_type="raw",
            folder="docuchat_pdfs/",
            access_mode="public"
        )

        file_url = upload_result.get("secure_url")

        # Parse PDF text
        try:
            parsed_content = parse_pdf(file_url)
        except Exception as e:
            return Response(
                {"error": f"PDF parsing failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save document
        doc = Document.objects.create(
            name=file.name,
            file_url=file_url,
            parsed_content=parsed_content
        )

        return Response(
            {
                "id": doc.id,
                "name": doc.name,
                "parsed_pages": len(parsed_content),
            },
            status=status.HTTP_201_CREATED
        )


# =====================================================
# Chat Endpoint
# =====================================================
class ChatView(APIView):
    def post(self, request):
        query = request.data.get("message")

        if not query:
            return Response(
                {"error": "No message provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Always use latest uploaded PDF
        doc = Document.objects.order_by("-id").first()

        if not doc:
            return Response(
                {"answer": "No PDF uploaded yet."},
                status=status.HTTP_200_OK
            )

        document_content = doc.parsed_content or {}

        # Lazy import prevents Railway boot crash
        try:
            from .graphs import get_compiled_graph
            graph = get_compiled_graph()
        except Exception as e:
            return Response(
                {"answer": f"AI initialization failed: {str(e)}"},
                status=status.HTTP_200_OK
            )

        state = {
            "document_content": document_content,
            "conversation_history": [],
            "current_query": query,
            "selected_context": "",
            "answer": "",
            "is_answerable": False,
            "validation_passed": False,
        }

        try:
            result = graph.invoke(state)
            answer = result.get("answer", "No answer generated.")
        except Exception as e:
            answer = f"AI error: {str(e)}"

        return Response(
            {"answer": answer},
            status=status.HTTP_200_OK
        )
