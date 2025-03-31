from django.urls import path
from .views import signDocument, verifyDocument, modifyDocument

urlpatterns = [
    path("sign/", signDocument, name="sign"),
    path("verify/", verifyDocument, name="verify"),
    path("modify/", modifyDocument, name="modify")
]
