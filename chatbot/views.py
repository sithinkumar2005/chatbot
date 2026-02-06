from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .models import Complaint, DigitalIdentity

# optional Alert model
try:
    from .models import Alert
except Exception:
    Alert = None

from .ml_engine import predict_priority
from .nlp import chatbot_response


# ================= COMMON HELPER =================

def get_digital_id(user):
    digital_identity, _ = DigitalIdentity.objects.get_or_create(user=user)
    return digital_identity.digital_id


# ================= EMAIL + ALERT =================

def send_complaint_email(user, complaint):

    recipient = user.email or user.username

    if not recipient:
        print("⚠ No recipient — skip email")
        return

    try:
        print("📧 Sending mail to:", recipient)

        send_mail(
            subject=f"Complaint Registered: {complaint.complaint_id}",
            message=(
                f"Complaint Registered Successfully\n\n"
                f"ID: {complaint.complaint_id}\n"
                f"Department: {complaint.department}\n"
                f"Issue: {complaint.issue_type}\n"
                f"Priority: {complaint.priority}\n"
                f"Status: {complaint.status}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

        print("✅ Mail sent OK")

    except Exception as e:
        print("❌ Email failed:", e)


def create_alert(user, message):
    if Alert:
        Alert.objects.create(user=user, message=message)


# ================= PAGES =================

@login_required(login_url='/api/login/')
def home(request):
    return render(request, "index.html", {
        "digital_id": get_digital_id(request.user)
    })


@login_required(login_url='/api/login/')
def chat_page(request):
    return render(request, "chat.html", {
        "digital_id": get_digital_id(request.user)
    })


@login_required(login_url='/api/login/')
def document_page(request):
    return render(request, "documents.html", {
        "digital_id": get_digital_id(request.user)
    })


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

    # STATUS C123ABC
    if message.upper().startswith("STATUS"):
        parts = message.split()

        if len(parts) >= 2:
            cid = parts[-1].upper()

            comp = Complaint.objects.filter(
                complaint_id__iexact=cid
            ).first()

            if comp:
                return Response({
                    "reply": (
                        f"Complaint {cid}\n"
                        f"Status: {comp.status}\n"
                        f"Priority: {comp.priority}\n"
                        f"Department: {comp.department}"
                    )
                })

            return Response({"reply": "Complaint not found"})

    reply = chatbot_response(message)
    return Response({"reply": reply})


# ================= REGISTER COMPLAINT =================

@csrf_exempt
@api_view(["POST"])
@login_required
def register_complaint(request):

    print("📥 REGISTER HIT:", request.data)

    department = request.data.get("department", "").strip()
    issue_type = request.data.get("issue_type", "").strip()
    description = request.data.get("description", "").strip()

    if not department or not issue_type or not description:
        return Response({"error": "All fields required"}, status=400)

    # ML safe fallback
    try:
        priority = predict_priority(description)
    except Exception as e:
        print("⚠ ML failed — using Medium:", e)
        priority = "Medium"

    complaint = Complaint.objects.create(
        user=request.user,
        department=department,
        issue_type=issue_type,
        description=description,
        priority=priority
    )

    # notifications (never break API)
    try:
        send_complaint_email(request.user, complaint)
    except Exception as e:
        print("⚠ Mail wrapper error:", e)

    create_alert(
        request.user,
        f"Complaint {complaint.complaint_id} registered"
    )

    return Response({
        "message": "Complaint registered successfully",
        "complaint_id": complaint.complaint_id,
        "priority": complaint.priority,
        "status": complaint.status
    })


# ================= USER ALERTS =================

@api_view(["GET"])
@login_required
def user_alerts(request):

    if not Alert:
        return Response([])

    alerts = Alert.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    return Response([
        {
            "message": a.message,
            "time": a.created_at,
            "read": getattr(a, "is_read", False)
        }
        for a in alerts
    ])


# ================= STATUS =================

@api_view(["GET"])
@login_required
def complaint_status(request, cid):

    cid = cid.strip().upper()

    complaint = Complaint.objects.filter(
        complaint_id__iexact=cid,
        user=request.user
    ).first()

    if not complaint:
        return Response({"error": "Complaint not found"}, status=404)

    return Response({
        "complaint_id": complaint.complaint_id,
        "status": complaint.status,
        "priority": complaint.priority,
        "department": complaint.department,
    })


# ================= MY COMPLAINTS =================

@api_view(["GET"])
@login_required
def my_complaints(request):

    qs = Complaint.objects.filter(user=request.user)\
        .order_by("-created_at")\
        .values(
            "complaint_id",
            "department",
            "status",
            "priority",
            "created_at"
        )

    return Response(list(qs))


# ================= DOC UPLOAD =================

@csrf_exempt
@api_view(["POST"])
@login_required
def upload_document(request):

    if "document" not in request.FILES:
        return Response({"error": "No document uploaded"}, status=400)

    return Response({"message": "Document uploaded"})


# ================= AUTH =================

def signup_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=email).exists():
            return render(request, "signup.html", {"error": "User exists"})

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

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

        return render(request, "login.html", {
            "error": "Invalid credentials"
        })

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('/api/login/')
