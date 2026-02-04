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


# ================= HOME =================
@login_required(login_url='/api/login/')
def home(request):
    digital_identity, _ = DigitalIdentity.objects.get_or_create(
        user=request.user
    )
    return render(request, "index.html", {
        "digital_id": digital_identity.digital_id
    })


# ================= CHATBOT API =================
@csrf_exempt
@api_view(["POST"])
@authentication_classes([])       
@permission_classes([AllowAny])    #  Public API
def chat_view(request):
    message = request.data.get("message", "").strip()

    if not message:
        return Response({"reply": "Please type a message."})

    reply = chatbot_response(message)
    return Response({"reply": reply})


# ================= COMPLAINT =================
@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register_complaint(request):
    description = request.data.get("description", "")

    priority = predict_priority(description)

    Complaint.objects.create(
        department=request.data.get("department"),
        issue_type=request.data.get("issue_type"),
        description=description,
        priority=priority
    )

    return Response({
        "message": "Complaint submitted successfully",
        "priority": priority
    })


# ================= DOCUMENT UPLOAD =================
@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def upload_document(request):
    if "document" not in request.FILES:
        return Response({"error": "No document uploaded"}, status=400)

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

        # create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        # ✅ SAFE create — avoids duplicate error
        DigitalIdentity.objects.get_or_create(user=user)

        login(request, user)
        return redirect("/api/")

    return render(request, "signup.html")





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



def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    return render(request, "index.html")
