from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from .models import Document, ChatSession, Message
from .utils import parse_pdf
import os


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

        file_path = default_storage.save(f"pdfs/{file.name}", file)
        full_path = os.path.join(default_storage.location, file_path)

        try:
            parsed_content = parse_pdf(full_path)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        doc = Document.objects.create(
            name=file.name,
            file=file_path,
            parsed_content=parsed_content
        )

        return Response(
            {"id": doc.id, "name": doc.name, "parsed_pages": len(parsed_content)},
            status=201
        )


class CreateSessionView(APIView):
    def post(self, request):
        doc_ids = request.data.get("document_ids", [])
        if not doc_ids:
            return Response({"error": "No documents provided"}, status=400)

        docs = Document.objects.filter(id__in=doc_ids)
        if docs.count() != len(doc_ids):
            return Response({"error": "Document mismatch"}, status=400)

        session = ChatSession.objects.create()
        session.documents.set(docs)

        return Response({"session_id": session.id}, status=201)


class ChatView(APIView):
    def post(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=404)

        query = request.data.get("message")
        if not query:
            return Response({"error": "No message provided"}, status=400)

        Message.objects.create(session=session, role="user", content=query)

        document_content = {}
        for doc in session.documents.all():
            document_content.update(doc.parsed_content or {})

        history = [
            {"role": m.role, "content": m.content}
            for m in session.messages.order_by("timestamp")
        ]

        try:
            from .graphs import compiled_graph
        except Exception as e:
            return Response({"answer": f"AI unavailable: {str(e)}"}, status=200)

        state = {
            "document_content": document_content,
            "conversation_history": history,
            "current_query": query,
            "selected_context": "",
            "answer": "",
            "is_answerable": False,
            "validation_passed": False,
        }

        try:
            result = compiled_graph.invoke(state)
            answer = result.get("answer", "No answer generated.")
        except Exception as e:
            answer = f"AI error: {str(e)}"

        Message.objects.create(session=session, role="assistant", content=answer)

        return Response({"answer": answer}, status=200)
