from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document
from .utils import parse_pdf
import cloudinary.uploader


class HealthCheckView(APIView):
    def get(self, request):
        return Response(
            {"status": "healthy", "message": "Backend is running"},
            status=status.HTTP_200_OK
        )


class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=400)

        upload_result = cloudinary.uploader.upload(
            file,
            resource_type="raw",
            folder="docuchat_pdfs/"
        )

        file_url = upload_result.get("secure_url")

        try:
            parsed_content = parse_pdf(file_url)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        doc = Document.objects.create(
            name=file.name,
            file_url=file_url,
            parsed_content=parsed_content,
        )

        return Response(
            {
                "id": doc.id,
                "name": doc.name,
                "parsed_pages": len(parsed_content),
            },
            status=201,
        )


class ChatView(APIView):
    def post(self, request):
        query = request.data.get("message")

        if not query:
            return Response({"error": "No message provided"}, status=400)

        # get latest document
        doc = Document.objects.order_by("-id").first()

        if not doc:
            return Response(
                {"answer": "No PDF uploaded yet."},
                status=200
            )

        document_content = doc.parsed_content or {}

        # ✅ IMPORTANT: lazy import
        try:
            from .graphs import get_compiled_graph
            graph = get_compiled_graph()
        except Exception as e:
            return Response(
                {"answer": f"AI initialization failed: {str(e)}"},
                status=200
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

        return Response({"answer": answer}, status=200)
