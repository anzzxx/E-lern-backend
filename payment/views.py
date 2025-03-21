from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import razorpay
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from accounts.models import CustomUser as User
from Courses.models import Course, Enrollment

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            amount = int(data.get("amount", 0)) * 100  # Convert to paisa
            course_id = data.get("course_id")
            user_id = request.user.id
            
            if not amount or not course_id:
                return JsonResponse({"success": False, "message": "Missing required fields"}, status=400)
            
            print(f"Creating order for User: {user_id}, Course: {course_id}, Amount: {amount}")
            
            order_data = {
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1",
            }
            
            order = razorpay_client.order.create(order_data)
            return JsonResponse(order)
        
        except Exception as e:
            print(f"Error creating order: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class WebhookView(APIView):
    def post(self, request):
        payload = request.body
        signature = request.headers.get("X-Razorpay-Signature")
        
        try:
            razorpay_client.utility.verify_webhook_signature(payload, signature, settings.RAZORPAY_KEY_SECRET)
            data = json.loads(payload)
            print(f"Webhook Payment Success: {json.dumps(data, indent=4)}")
            return JsonResponse({"status": "success"})
        
        except Exception as e:
            print(f"Webhook verification failed: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            payment_id = data.get("payment_id")
            order_id = data.get("order_id")
            signature = data.get("signature")
            course_id = data.get("course_id")
            transaction_id = data.get("transaction_id")
            payment_method = data.get("method")
            status = data.get("status")
            
            print(f"Verifying payment for Course: {course_id}, User: {request.user.id}, Method: {payment_method}")
            
            if not payment_id or not order_id or not signature:
                return JsonResponse({"success": False, "message": "Missing payment details"}, status=400)
            
            params_dict = {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
                payment_verified = True
            except razorpay.errors.SignatureVerificationError as e:
                print(f"Payment verification failed: {e}")
                return JsonResponse({"success": False, "message": "Invalid payment signature"}, status=400)
            
            if payment_verified:
                user = request.user
                course = Course.objects.get(id=course_id)
                
                # Save payment details in the database
                payment = Payment.objects.create(
                    user=user,
                    course=course,
                    amount=data.get("amount", 0),
                    method=payment_method or "unknown",
                    transaction_id=transaction_id,
                    status="success",
                )
                
                # Enroll user in the course after successful payment
                Enrollment.objects.create(
                    user=user,
                    course=course,
                    payment=True,
                    status="active"
                )
                
                return JsonResponse({"success": True, "message": "Payment verified successfully!"})
        
        except Exception as e:
            print(f"Error in payment verification: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
