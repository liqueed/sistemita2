"""Utils Email."""

import threading
from email.mime.image import MIMEImage

# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class EmailThread(threading.Thread):
    """
    Class para enviar un email con thread.
    """

    def __init__(self, subject, body, from_email, recipient_list, fail_silently, html, attach, file):
        self.subject = subject
        self.body = body
        self.recipient_list = recipient_list
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html = html
        self.attach = attach
        self.file = file
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(self.subject, self.body, self.from_email, self.recipient_list)
        # Si es en formato html
        if self.html:
            msg.attach_alternative(self.html, "text/html")

        # Si adjunta un archivo
        if self.attach:
            msg_image = MIMEImage(self.file.read())
            msg_image.add_header('Content-ID', '<{}>'.format("<" + self.file.name + ">"))
            msg_image.add_header("Content-Disposition", "inline", filename=self.file.name)
            msg.attach(msg_image)

        msg.send(self.fail_silently)


def send_mail(
    subject, body, from_email, recipient_list, fail_silently=False, html=None, attach=None, file=None, *args, **kwargs
):
    """
    Send email
    """
    EmailThread(subject, body, from_email, recipient_list, fail_silently, html, attach, file).start()


def send_notification_factura_distribuida(proveedor, facturadistribuida):
    """Envia notificación a proveedor de factura distribuida."""

    html_content = render_to_string(
        'emails/facturas_pendientes.html',
        {
            'factura_numero': facturadistribuida.factura.numero,
            'cliente_razon_social': facturadistribuida.factura.cliente.razon_social,
            'url': '/',
        },
    )

    if proveedor.correo:
        send_mail(
            'Liqueed - Autorización facturas pendientes',
            '',
            settings.EMAIL_FROM,
            [proveedor.correo],
            html=html_content,
        )
