from io import BytesIO
from django.shortcuts import redirect, render
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from django.urls import reverse
from django.core.files.base import ContentFile
from .models import Document
from .forms import DocumentForm, VerifySignForm
import fitz
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signDocument(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()

            # Load private key
            with open("private_key.pem", "rb") as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)

            # Read file contents
            with document.document.open("rb") as f:
                contenido = f.read()

            # Generate signature
            sign = private_key.sign(
                contenido,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            # Save signature in the model
            document.sign = sign
            document.save()

            return render(request, "sign_document.html", {"form": DocumentForm(), "message": f"Documento firmado con éxito con la id: {document.id}"})

    else:
        form = DocumentForm()

    return render(request, "sign_document.html", {"form": form})

@csrf_exempt
def verifyDocument(request):
    mensaje = ""
    mod_message = request.GET.get("message", "")
    if request.method == "POST":
        form = VerifySignForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data["documento_id"]
            try:
                document = Document.objects.get(id=doc_id)

                # Load public key
                with open("public_key.pem", "rb") as f:
                    public_key = serialization.load_pem_public_key(f.read())

                # Read file contents
                with document.document.open("rb") as f:
                    contenido = f.read()

                # Verify signature
                try:
                    public_key.verify(
                        document.sign,
                        contenido,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH,
                        ),
                        hashes.SHA256(),
                    )
                    mensaje = "Firma válida ✅"
                except InvalidSignature:
                    mensaje = "Firma no válida ❌"

            except Document.DoesNotExist:
                mensaje = "Documento no encontrado"

    else:
        form = VerifySignForm()

    return render(request, "verify_document.html", {"form": form, "modify_form": VerifySignForm(), "message": mensaje, 'modify_message': mod_message})

@csrf_exempt
def modifyDocument(request):
    message = ""
    doc_id = None  # Define doc_id outside the if block to avoid reference issues

    if request.method == "POST":
        form = VerifySignForm(request.POST)
        if form.is_valid():
            doc_id = form.cleaned_data["documento_id"]
            try:
                document = Document.objects.get(id=doc_id)

                # Open the PDF document
                doc = fitz.open(document.document.path)
                page = doc[0]
                text = "I saw your document"
                x, y = 50, 100
                page.insert_text((x, y), text, fontsize=12, color=(0, 0, 0))

                # Save the modified PDF to memory (BytesIO)
                buffer = BytesIO()
                doc.save(buffer)
                buffer.seek(0)
                doc.close()

                # Create a new filename (or overwrite safely)
                new_filename = f"modified_{document.document.name.split('/')[-1]}"

                # Save the new file to the model
                document.document.save(new_filename, ContentFile(buffer.read()), save=True)

                message = "Documento modificado con éxito"

            except Document.DoesNotExist:
                message = "Documento no encontrado"

    return redirect(f"{reverse('verify')}?message={message}")
