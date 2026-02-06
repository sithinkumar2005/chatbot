from django.core.mail import send_mail


def send_complaint_email(user, complaint):

    subject = f"Complaint Registered — {complaint.complaint_id}"

    message = f"""
Hello {user.username},

Your complaint has been registered.

Complaint ID: {complaint.complaint_id}
Department: {complaint.department}
Issue Type: {complaint.issue_type}
Priority: {complaint.priority}
Status: {complaint.status}

We will notify you when status changes.

E-Gov AI System
"""

    send_mail(
        subject,
        message,
        None,
        [user.email],
        fail_silently=True
    )
