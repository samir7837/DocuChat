from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .utils import parse_pdf
import cloudinary.uploader


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy"})


class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        # ✅ parse FIRST
        try:
            parsed_content = parse_pdf(file)
        except Exception as e:
            return Response(
                {"error": f"PDF parsing failed: {str(e)}"},
                status=400,
            )

        # reset pointer before upload
        file.seek(0)

        upload = cloudinary.uploader.upload(
            file,
            resource_type="raw",
            folder="docuchat_pdfs/",
        )

        doc = Document.objects.create(
            name=file.name,
            file_url=upload.get("secure_url"),
            parsed_content=parsed_content,
        )

        return Response(
            {
                "id": doc.id,
                "name": doc.name,
                "pages": len(parsed_content),
            },
            status=201,
        )


class ChatView(APIView):
    def post(self, request):
        query = request.data.get("message")

        if not query:
            return Response({"answer": "Empty message"}, status=200)

        doc = Document.objects.order_by("-id").first()

        if not doc:
            return Response(
                {"answer": "Please upload a PDF first."},
                status=200,
            )

        from .graphs import get_compiled_graph

        graph = get_compiled_graph()

        state = {
            "document_content": doc.parsed_content,
            "conversation_history": [],
            "current_query": query,
            "selected_context": "",
            "answer": "",
            "is_answerable": False,
            "validation_passed": False,
        }

        result = graph.invoke(state)

        return Response({"answer": result.get("answer", "")})
