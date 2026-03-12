from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from src.repos.fake_payment_repo import FakePaymentRepository
from src.services.payment_service import PaymentService
from typing import Optional

app = FastAPI(title="Fake Payment Server")
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Forces all FastAPI validation errors (like missing bodies or wrong types) to be 400 Bad Request
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "Invalid input"})

# Maps FastAPI's default "detail" key to the assignment's required "error" key
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

repo = FakePaymentRepository()
service = PaymentService(repo)

# ... existing exception handlers for RequestValidationError and HTTPException ...

# Global catch-all for unexpected 500 errors (Security requirement)
@app.exception_handler(Exception)
async def global_500_exception_handler(request, exc):
    # In a real production app, you would print/log the actual `exc` here for debugging!
    # print(f"CRITICAL ERROR LOGGED SERVER-SIDE: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Something went wrong"}
    )

# --- Pydantic Models ---
class CustomerCreate(BaseModel):
    name: str
    email: str

class PaymentCreate(BaseModel):
    customer_id: str
    amount: int
    currency: str

class RefundCreate(BaseModel):
    # We make these Optional so FastAPI doesn't auto-throw a 422 if they are missing.
    # This allows us to manually throw a 400 to satisfy the strict assignment rubric.
    paymentId: Optional[str] = None
    amount: Optional[int] = None    

# --- Routes ---
@app.post("/customers", status_code=status.HTTP_201_CREATED)
def create_customer(customer_data: CustomerCreate):
    try:
        return service.create_customer(customer_data.name, customer_data.email)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Email already exists":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

@app.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(payment_data: PaymentCreate):
    try:
        return service.create_payment(
            payment_data.customer_id,
            payment_data.amount,
            payment_data.currency
        )
    except ValueError as e:
        error_msg = str(e)
        # Match the specific error strings from your payment_service.py
        if error_msg == "Customer not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)

        # Catch other errors like "Invalid amount" or "Invalid currency"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong")
    
@app.post("/payments/{payment_id}/capture", status_code=status.HTTP_200_OK)
def capture_payment(payment_id: str):
    try:
        return service.capture_payment(payment_id)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Payment not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        if error_msg == "Payment cannot be captured":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)
            
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    
@app.post("/refunds", status_code=status.HTTP_201_CREATED)
def create_refund(refund_data: RefundCreate):
    # Manual checks to return exactly 400 Bad Request
    if refund_data.paymentId is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="paymentId is missing")
    if refund_data.amount is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="amount is missing")

    try:
        return service.create_refund(refund_data.paymentId, refund_data.amount)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Refund amount exceeds payment amount":
            # Return exactly 422 Unprocessable Entity
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=error_msg)
        if error_msg == "Payment not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong") 

# ... existing routes ...

@app.get("/payments", status_code=status.HTTP_200_OK)
def get_all_payments(payment_status: Optional[str] = Query(None, alias="status")):
    try:
        return service.get_all_payments(status=payment_status)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
@app.get("/customers/{customer_id}", status_code=status.HTTP_200_OK)
def get_customer(customer_id: str):
    try:
        return service.get_customer(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/customers/{customer_id}/payments", status_code=status.HTTP_200_OK)
def get_customer_payments(customer_id: str):
    try:
        return service.get_customer_payments(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.get("/payments/{payment_id}", status_code=status.HTTP_200_OK)
def get_payment(payment_id: str):
    try:
        return service.get_payment(payment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.post("/payments/{payment_id}/fail", status_code=status.HTTP_200_OK)
def fail_payment(payment_id: str):
    try:
        return service.fail_payment(payment_id)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Payment not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_msg)

@app.get("/refunds/{refund_id}", status_code=status.HTTP_200_OK)
def get_refund(refund_id: str):
    try:
        return service.get_refund(refund_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))