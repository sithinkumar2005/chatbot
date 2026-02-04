def chatbot_response(user_input):
    text = user_input.lower()

    if "digital identity" in text:
        return "You can create a digital identity by registering with your email and password."

    elif "document" in text or "documents" in text:
        return "Required documents: Aadhaar, PAN, Passport."

    elif "verification" in text:
        return "Document verification usually takes 24–48 hours."

    elif "complaint" in text:
        return "To file a complaint, select department, issue type, and provide description."

    else:
        return "Sorry, I didn't understand. Please ask about digital identity, documents, verification, or complaints."
