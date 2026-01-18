from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.core.files.temp import NamedTemporaryFile

from .models import Document
from .utils import parse_pdf

import cloudinary.uploader
import os


class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy"}, status=200)


class UploadPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        # -------------------------
        # 1️⃣ Save temp PDF locally
        # -------------------------
        temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")

        try:
            for chunk in file.chunks():
                temp_file.write(chunk)

            temp_file.close()

            # -------------------------
            # 2️⃣ Parse local PDF path
            # -------------------------
            parsed_content = parse_pdf(temp_file.name)

        except Exception as e:
            return Response(
                {"error": f"PDF parsing failed: {str(e)}"},
                status=400,
            )

        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass

        # -------------------------
        # 3️⃣ Upload to Cloudinary
        # -------------------------
        file.seek(0)

        upload = cloudinary.uploader.upload(
            file,
            resource_type="raw",
            folder="docuchat_pdfs/",
        )

        # -------------------------
        # 4️⃣ Save DB
        # -------------------------
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

        # lazy import avoids Railway boot crash
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

        return Response(
            {"answer": result.get("answer", "No response generated.")},
            status=200,
        )
