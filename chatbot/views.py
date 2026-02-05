from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import Complaint, DigitalIdentity
from .ml_engine import predict_priority
from .nlp import chatbot_response


# ================= COMMON HELPER =================

def get_digital_id(user):
    digital_identity, _ = DigitalIdentity.objects.get_or_create(user=user)
    return digital_identity.digital_id


# ================= HOME PAGE =================

@login_required(login_url='/api/login/')
def home(request):
    return render(request, "index.html", {
        "digital_id": get_digital_id(request.user)
    })


# ================= CHAT PAGE =================

@login_required(login_url='/api/login/')
def chat_page(request):
    return render(request, "chat.html", {
        "digital_id": get_digital_id(request.user)
    })


# ================= DOCUMENT PAGE =================

@login_required(login_url='/api/login/')
def document_page(request):
    return render(request, "documents.html", {
        "digital_id": get_digital_id(request.user)
    })


# ================= COMPLAINT PAGE =================

@login_required(login_url='/api/login/')
def complaint_page(request):
    return render(request, "complaint.html", {
        "digital_id": get_digital_id(request.user)
    })


# ================= CHATBOT API =================

@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def chat_view(request):
    message = request.data.get("message", "").strip()

    if not message:
        return Response({"reply": "Please type a message."})

    reply = chatbot_response(message)
    return Response({"reply": reply})


# ================= COMPLAINT REGISTER API =================

@csrf_exempt
@api_view(["POST"])
@login_required
def register_complaint(request):

    if not request.user.is_authenticated:
        return Response({"error": "Login required"}, status=401)

    description = request.data.get("description", "").strip()

    if not description:
        return Response({"error": "Description required"}, status=400)

    priority = predict_priority(description)

    complaint = Complaint.objects.create(
        user=request.user,
        department=request.data.get("department", ""),
        issue_type=request.data.get("issue_type", ""),
        description=description,
        priority=priority
    )

    return Response({
        "message": "Complaint registered successfully",
        "priority": priority,
        "complaint_id": complaint.complaint_id
    })


# ================= COMPLAINT STATUS API =================

@api_view(["GET"])
def complaint_status(request, cid):

    if not request.user.is_authenticated:
        return Response({"error": "Login required"}, status=401)

    try:
        complaint = Complaint.objects.get(
            complaint_id=cid,
            user=request.user
        )
    except Complaint.DoesNotExist:
        return Response({"error": "Complaint not found"}, status=404)

    return Response({
        "complaint_id": complaint.complaint_id,
        "status": complaint.status,
        "priority": complaint.priority,
        "department": complaint.department,
        "issue_type": complaint.issue_type
    })


# ================= DOCUMENT UPLOAD API =================

@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def upload_document(request):

    if "document" not in request.FILES:
        return Response({"error": "No document uploaded"}, status=400)

    # you can save file here later
    return Response({"message": "Document uploaded successfully"})


# ================= SIGNUP =================

def signup_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "signup.html", {
                "error": "Email and password required"
            })

        if User.objects.filter(username=email).exists():
            return render(request, "signup.html", {
                "error": "User already exists"
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        DigitalIdentity.objects.get_or_create(user=user)

        login(request, user)
        return redirect("/api/")

    return render(request, "signup.html")


# ================= LOGIN =================

def login_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

        if user:
            login(request, user)
            return redirect("/api/")
        else:
            return render(request, "login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "login.html")


# ================= LOGOUT =================

def logout_view(request):
    logout(request)
    return redirect('/api/login/')
