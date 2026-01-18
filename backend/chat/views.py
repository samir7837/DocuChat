import os
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document
from .utils import parse_pdf


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

        # ✅ save locally
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        for chunk in file.chunks():
            temp_file.write(chunk)

        temp_file.close()

        try:
            parsed_content = parse_pdf(temp_file.name)
        except Exception as e:
            os.remove(temp_file.name)
            return Response(
                {"error": f"PDF parsing failed: {str(e)}"},
                status=400
            )

        os.remove(temp_file.name)

        doc = Document.objects.create(
            name=file.name,
            file_url="",  # optional
            parsed_content=parsed_content,
        )

        return Response(
            {
                "id": doc.id,
                "name": doc.name,
                "parsed_pages": len(parsed_content),
            },
            status=201
        )


class ChatView(APIView):
    def post(self, request):
        query = request.data.get("message")

        if not query:
            return Response({"error": "No message provided"}, status=400)

        doc = Document.objects.order_by("-id").first()

        if not doc:
            return Response(
                {"answer": "No PDF uploaded yet."},
                status=200
            )

        try:
            from .graphs import get_compiled_graph
            graph = get_compiled_graph()
        except Exception as e:
            return Response(
                {"answer": f"AI initialization failed: {str(e)}"},
                status=200
            )

        state = {
            "document_content": doc.parsed_content,
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
